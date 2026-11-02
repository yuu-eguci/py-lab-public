"""
shared.tests.test_sse_formatters
"""

import json
from collections.abc import Iterator

from django.test import SimpleTestCase

from ..sse_formatters import SSEFormatter, create_sse_response


def parse_event(event: str) -> dict:
    """
    `data: {...}\\n\\n` 形式のイベントをひとつ読み取って payload を返します。
    """
    assert event.startswith("data: ") and event.endswith("\n\n"), f"SSE イベントの形式ではありません: {event!r}"
    return json.loads(event[len("data: ") : -2])


class TestSSEFormatter(SimpleTestCase):
    def test_format_message(self) -> None:
        event = SSEFormatter.format_message("rq-1", "こんにちは", module="foo")
        payload = parse_event(event)
        self.assertEqual(payload["requestId"], "rq-1")
        self.assertEqual(payload["data"]["message"], "こんにちは")
        self.assertEqual(payload["data"]["module"], "foo")
        self.assertIn("sentAt", payload["data"])

    def test_multiline_message_stays_in_one_data_line(self) -> None:
        # 改行入りのメッセージでも、イベントが割れたり別のフィールドが紛れ込んだりしないことを確認します。
        event = SSEFormatter.format_message("rq-1", "line1\n\ndata: injected\r\nline3")
        self.assertEqual(event.count("\n"), 2)
        self.assertNotIn("\r", event)
        self.assertEqual(parse_event(event)["data"]["message"], "line1\n\ndata: injected\r\nline3")

    def test_format_error(self) -> None:
        payload = parse_event(SSEFormatter.format_error("rq-1", "boom", module="foo"))
        self.assertEqual(payload["data"]["error"], "boom")
        self.assertNotIn("message", payload["data"])

    def test_format_completion(self) -> None:
        payload = parse_event(SSEFormatter.format_completion("rq-1"))
        self.assertEqual(payload["data"]["message"], "Stream completed")


class TestCreateSSEResponse(SimpleTestCase):
    def test_headers(self) -> None:
        def stream() -> Iterator[str]:
            yield SSEFormatter.format_message("rq-1", "hi")

        response = create_sse_response(stream())
        self.assertEqual(response["Content-Type"], "text/event-stream")
        self.assertEqual(response["Cache-Control"], "no-cache")
        self.assertEqual(response["X-Accel-Buffering"], "no")
        self.assertTrue(response.streaming)
