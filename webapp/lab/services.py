import importlib
import logging

from .module_specs import ModuleSpec

logger = logging.getLogger(__name__)


class LabModuleSpecService:
    """
    Lab モジュールの仕様を管理するサービスクラス。
    """

    def get_module_spec(self, module_name: str) -> ModuleSpec:
        """
        指定されたモジュール名の ModuleSpec を取得する。
        webapp.lab ディレクトリのモジュールを探して、その中の get_spec をコールして返却する。

        Args:
            module_name (str): モジュール名

        Returns:
            ModuleSpec: モジュール仕様

        Raises:
            ModuleNotFoundError: 指定されたモジュールが見つからない場合
            AttributeError: モジュールに get_spec 関数が定義されていない場合
        """
        try:
            # webapp.lab.{module_name} をインポート
            module_path = f"lab.{module_name}"
            module = importlib.import_module(module_path)
            logger.info(f"Successfully imported module: {module_path}")

        except ModuleNotFoundError as e:
            logger.error(f"Module not found: {module_name}")
            raise ModuleNotFoundError(f"Module '{module_name}' not found in lab directory") from e

        try:
            # get_spec 関数を取得して実行
            get_spec_func = getattr(module, "get_spec")
            module_spec = get_spec_func()
            logger.info(f"Successfully retrieved spec for module: {module_name}")
            return module_spec

        except AttributeError as e:
            logger.error(f"get_spec function not found in module: {module_name}")
            raise AttributeError(f"Module '{module_name}' does not have a 'get_spec' function") from e
