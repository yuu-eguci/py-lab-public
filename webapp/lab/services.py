from .module_specs import ModuleSpec


class LabModuleSpecService:
    """
    Lab モジュールの仕様を管理するサービスクラス。
    """

    def get_module_spec(self, module_name: str) -> ModuleSpec:
        """
        指定されたモジュール名の ModuleSpec を取得する。
        現在は空の ModuleSpec を返す。

        Args:
            module_name (str): モジュール名

        Returns:
            ModuleSpec: モジュール仕様
        """
        # とりあえず空っぽの ModuleSpec を返却
        return ModuleSpec(
            module="",
            description="",
            args={}
        )
