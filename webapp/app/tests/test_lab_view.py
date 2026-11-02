"""
app.tests.test_lab_view
"""

import json
import sys
from types import ModuleType
from unittest import mock

from django.test import SimpleTestCase, override_settings

from lab.module_specs import ModuleSpec

URL = "/api/app/lab"


def make_lab_module(name: str, main=None, get_spec=None) -> ModuleType:
    module = ModuleType(f"lab.{name}")
    if main is not None:
        module.main = main  # type: ignore[attr-defined]
    if get_spec is not None:
        module.get_spec = get_spec  # type: ignore[attr-defined]
    return module


def read_events(response) -> list[dict]:
    """
    StreamingHttpResponse の中身を最後まで読んで、 SSE イベントの payload のリストにします。
    """
    body = b"".join(response.streaming_content).decode()
    events = [event for event in body.split("\n\n") if event]
    for event in events:
        assert event.startswith("data: ") and "\n" not in event, event
    return [json.loads(event[len("data: ") :]) for event in events]


class TestLabViewGet(SimpleTestCase):
    def test_returns_spec(self) -> None:
        response = self.client.get(URL, {"module": "foo"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["module"], "foo")
        self.assertIn("arg1", response.json()["data"]["args"])

    def test_missing_module_param(self) -> None:
        self.assertEqual(self.client.get(URL).status_code, 400)

    def test_unknown_module(self) -> None:
        response = self.client.get(URL, {"module": "nope"})
        self.assertEqual(response.status_code, 400)

    def test_invalid_module_name(self) -> None:
        self.assertEqual(self.client.get(URL, {"module": "../foo"}).status_code, 400)

    def test_module_without_get_spec(self) -> None:
        self.assertEqual(self.client.get(URL, {"module": "module_specs"}).status_code, 400)

    def test_error_inside_get_spec_is_not_reported_as_missing(self) -> None:
        # get_spec の中の AttributeError を "get_spec が無い" と取り違えないことを確認します。
        def get_spec() -> ModuleSpec:
            raise AttributeError("bug in get_spec")

        with mock.patch.dict(sys.modules, {"lab.broken": make_lab_module("broken", get_spec=get_spec)}):
            response = self.client.get(URL, {"module": "broken"})
        self.assertEqual(response.status_code, 500)


class TestLabViewPost(SimpleTestCase):
    def post(self, body: dict):
        return self.client.post(URL, data=body, content_type="application/json")

    def test_streams_messages_then_completion(self) -> None:
        def main(**args):
            yield "hello"
            yield f"got {args['arg1']}\nnext line"

        with mock.patch.dict(sys.modules, {"lab.fake": make_lab_module("fake", main=main)}):
            response = self.post({"module": "fake", "args": {"arg1": "x"}})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response["Content-Type"], "text/event-stream")
            self.assertEqual(response["Cache-Control"], "no-cache")
            self.assertEqual(response["X-Accel-Buffering"], "no")
            events = read_events(response)

        messages = [event["data"].get("message") for event in events]
        self.assertEqual(messages, ["Starting module: fake", "hello", "got x\nnext line", "Stream completed"])
        self.assertTrue(all(event["requestId"] == events[0]["requestId"] for event in events))

    def test_unknown_module_returns_400_without_stream(self) -> None:
        response = self.post({"module": "nope"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response["Content-Type"], "application/json")

    def test_invalid_module_name_returns_400(self) -> None:
        for module in ["../foo", "_private", 123]:
            with self.subTest(module=module):
                self.assertEqual(self.post({"module": module}).status_code, 400)

    def test_module_without_main_returns_400(self) -> None:
        self.assertEqual(self.post({"module": "module_specs"}).status_code, 400)

    def test_args_must_be_object(self) -> None:
        self.assertEqual(self.post({"module": "foo", "args": ["a"]}).status_code, 400)

    def test_error_event_without_completion_and_details_hidden(self) -> None:
        def main(**args):
            yield "before"
            raise RuntimeError("secret detail")

        with mock.patch.dict(sys.modules, {"lab.fake": make_lab_module("fake", main=main)}):
            with self.assertLogs("app.views", level="ERROR"):
                events = read_events(self.post({"module": "fake"}))

        self.assertEqual(events[1]["data"]["message"], "before")
        last = events[-1]["data"]
        self.assertIn("error", last)
        self.assertNotIn("secret detail", last["error"])
        self.assertNotIn("Stream completed", [event["data"].get("message") for event in events])

    @override_settings(DEBUG=True)
    def test_error_details_are_shown_in_debug(self) -> None:
        def main(**args):
            raise RuntimeError("secret detail")
            yield  # pragma: no cover

        with mock.patch.dict(sys.modules, {"lab.fake": make_lab_module("fake", main=main)}):
            with self.assertLogs("app.views", level="ERROR"):
                events = read_events(self.post({"module": "fake"}))

        self.assertEqual(events[-1]["data"]["error"], "RuntimeError: secret detail")
