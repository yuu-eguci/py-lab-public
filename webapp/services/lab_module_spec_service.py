import logging

from lab.module_specs import ModuleSpec

from .lab_module_loader import get_lab_function

logger = logging.getLogger(__name__)


class LabModuleSpecService:
    """
    Lab モジュールの仕様を管理するサービスクラスです。
    """

    def get_module_spec(self, module_name: str) -> ModuleSpec:
        """
        指定されたモジュール名の ModuleSpec を取得します。
        webapp.lab ディレクトリのモジュールを探して、その中の get_spec をコールして返却します。

        Args:
            module_name (str): モジュール名

        Returns:
            ModuleSpec: モジュール仕様

        Raises:
            LabModuleError: モジュールが見つからない場合、または get_spec 関数が定義されていない場合
        """
        module_spec = get_lab_function(module_name, "get_spec")()
        logger.info(f"Successfully retrieved spec for module: {module_name}")
        return module_spec
