"""
services.tests.test_lab_module_loader
"""

import sys
from types import ModuleType
from unittest import mock

from django.test import SimpleTestCase

from ..lab_module_loader import LabModuleError, get_lab_function, import_lab_module


class TestImportLabModule(SimpleTestCase):
    def test_imports_lab_module(self) -> None:
        module = import_lab_module("foo")
        self.assertEqual(module.__name__, "lab.foo")

    def test_rejects_invalid_names(self) -> None:
        # lab の外へ出る名前、サブモジュール、 _ 始まり、文字列以外は import 前に弾きます。
        for name in ["", "../foo", "foo.bar", "_private", "__init__", "Foo", "1foo", "foo-bar", 1, None]:
            with self.subTest(name=name):
                with mock.patch("importlib.import_module") as import_module:
                    with self.assertRaises(LabModuleError):
                        import_lab_module(name)  # type: ignore[arg-type]
                    import_module.assert_not_called()

    def test_missing_module(self) -> None:
        with self.assertRaisesMessage(LabModuleError, "Module 'nope' not found in lab directory"):
            import_lab_module("nope")

    def test_missing_dependency_inside_lab_module_is_not_hidden(self) -> None:
        # lab module の中で import に失敗したときは、 "module が無い" 扱いにせずそのまま投げます。
        error = ModuleNotFoundError("No module named 'requests'", name="requests")
        with mock.patch("importlib.import_module", side_effect=error):
            with self.assertRaises(ModuleNotFoundError) as cm:
                import_lab_module("needs_requests")
        self.assertIs(cm.exception, error)

    def test_uses_registered_module(self) -> None:
        fake = ModuleType("lab.fake")
        with mock.patch.dict(sys.modules, {"lab.fake": fake}):
            self.assertIs(import_lab_module("fake"), fake)


class TestGetLabFunction(SimpleTestCase):
    def test_returns_function(self) -> None:
        fake = ModuleType("lab.fake")
        fake.main = lambda: "ok"  # type: ignore[attr-defined]
        with mock.patch.dict(sys.modules, {"lab.fake": fake}):
            self.assertIs(get_lab_function("fake", "main"), fake.main)  # type: ignore[attr-defined]

    def test_missing_or_not_callable_function(self) -> None:
        fake = ModuleType("lab.fake")
        fake.main = "not callable"  # type: ignore[attr-defined]
        with mock.patch.dict(sys.modules, {"lab.fake": fake}):
            for function_name in ["main", "get_spec"]:
                with self.subTest(function_name=function_name):
                    with self.assertRaisesMessage(
                        LabModuleError, f"Module 'fake' does not have a '{function_name}' function"
                    ):
                        get_lab_function("fake", function_name)
