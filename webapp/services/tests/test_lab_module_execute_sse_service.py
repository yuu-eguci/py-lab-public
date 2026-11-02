"""
services.tests.test_lab_module_execute_sse_service
"""

import sys
from types import ModuleType
from unittest import mock

from django.test import SimpleTestCase

from ..lab_module_execute_sse_service import LabModuleExecuteSSEService
from ..lab_module_loader import LabModuleError


class TestGetMainFunction(SimpleTestCase):
    def test_returns_main(self) -> None:
        fake = ModuleType("lab.fake")
        fake.main = lambda **args: "ok"  # type: ignore[attr-defined]
        with mock.patch.dict(sys.modules, {"lab.fake": fake}):
            self.assertIs(LabModuleExecuteSSEService().get_main_function("fake"), fake.main)  # type: ignore[attr-defined]

    def test_module_without_main(self) -> None:
        with self.assertRaisesMessage(LabModuleError, "Module 'module_specs' does not have a 'main' function"):
            LabModuleExecuteSSEService().get_main_function("module_specs")

    def test_missing_module(self) -> None:
        with self.assertRaises(LabModuleError):
            LabModuleExecuteSSEService().get_main_function("nope")


class TestExecuteModuleSSE(SimpleTestCase):
    def test_generator_messages_are_converted_to_str(self) -> None:
        def main(**args):
            yield "start"
            yield 42
            yield f"{args['x']}!"

        messages = list(LabModuleExecuteSSEService().execute_module_sse(main, {"x": "done"}))
        self.assertEqual(messages, ["start", "42", "done!"])

    def test_single_return_value(self) -> None:
        messages = list(LabModuleExecuteSSEService().execute_module_sse(lambda **args: {"a": 1}, {}))
        self.assertEqual(messages, ["{'a': 1}"])

    def test_string_return_value_is_one_message(self) -> None:
        messages = list(LabModuleExecuteSSEService().execute_module_sse(lambda **args: "abc", {}))
        self.assertEqual(messages, ["abc"])

    def test_exception_propagates(self) -> None:
        # 例外はメッセージにせず呼び出し元へ投げます。エラーイベントにするのは view の役目です。
        def main(**args):
            yield "start"
            raise ValueError("boom")

        stream = LabModuleExecuteSSEService().execute_module_sse(main, {})
        self.assertEqual(next(stream), "start")
        with self.assertRaisesMessage(ValueError, "boom"):
            next(stream)

    def test_close_closes_lab_generator(self) -> None:
        # クライアントが切断してストリームが close されたら、 lab module 側も後片付けできることを確認します。
        cleaned_up = []

        def main(**args):
            try:
                yield "first"
                yield "second"
            finally:
                cleaned_up.append(True)

        stream = LabModuleExecuteSSEService().execute_module_sse(main, {})
        self.assertEqual(next(stream), "first")
        stream.close()
        self.assertEqual(cleaned_up, [True])
