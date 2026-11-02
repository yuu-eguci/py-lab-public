import importlib
import logging
import re
from collections.abc import Callable
from types import ModuleType
from typing import Any

logger = logging.getLogger(__name__)

# lab module として扱う名前です。英小文字・数字・ _ だけで、 _ 始まりは対象外にしています。
# NOTE: "foo.bar" や "../foo" のような名前で lab の外やサブモジュールを import しないための制限です。
LAB_MODULE_NAME_PATTERN = re.compile(r"[a-z][a-z0-9_]*")


class LabModuleError(Exception):
    """
    lab module が使えないときの例外です。 view ではこれを 400 にします。
    (名前が不正、 lab に無い、必要な関数が無い、のどれかです。)
    """


def get_lab_function(module_name: str, function_name: str) -> Callable[..., Any]:
    """
    lab module から関数を取り出して返します。

    Raises:
        LabModuleError: モジュールが使えないとき、または関数が無いとき
    """
    func = getattr(import_lab_module(module_name), function_name, None)
    if not callable(func):
        raise LabModuleError(f"Module '{module_name}' does not have a '{function_name}' function")
    return func


def import_lab_module(module_name: str) -> ModuleType:
    """
    webapp.lab.{module_name} を import して返します。

    Args:
        module_name (str): モジュール名

    Returns:
        ModuleType: import した lab module

    Raises:
        LabModuleError: 名前が不正なとき、または lab に該当するモジュールが無いとき
        ModuleNotFoundError: lab module の中の import に失敗したとき
    """
    if not isinstance(module_name, str) or not LAB_MODULE_NAME_PATTERN.fullmatch(module_name):
        logger.warning(f"Invalid lab module name: {module_name!r}")
        raise LabModuleError(f"Module '{module_name}' not found in lab directory")

    module_path = f"lab.{module_name}"
    try:
        return importlib.import_module(module_path)
    except ModuleNotFoundError as e:
        # lab module の中で別のモジュールの import に失敗したときは、そのまま投げます。
        if e.name != module_path:
            raise
        logger.warning(f"Module not found: {module_path}")
        raise LabModuleError(f"Module '{module_name}' not found in lab directory") from e
