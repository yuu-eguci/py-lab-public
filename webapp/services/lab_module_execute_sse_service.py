import importlib
import logging
from typing import Any, Generator

logger = logging.getLogger(__name__)


class LabModuleExecuteSSEService:
    """
    Lab モジュールをSSE形式で実行するサービスクラス。
    """

    def execute_module_sse(self, module_name: str, args: dict[str, Any]) -> Generator[str, None, None]:
        """
        指定されたモジュールをSSE形式で実行する。
        webapp.lab.{module_name} をインポートし、main 関数を実行してその結果をyieldする。

        Args:
            module_name (str): モジュール名
            args (dict[str, Any]): モジュールに渡す引数

        Yields:
            str: SSE形式のメッセージ

        Raises:
            ModuleNotFoundError: 指定されたモジュールが見つからない場合
            AttributeError: モジュールに main 関数が定義されていない場合
        """
        logger.info(f"LabModuleExecuteSSEService.execute_module_sse called with module_name={module_name}, args={args}")

        try:
            # webapp.lab.{module_name} をインポート
            module_path = f"lab.{module_name}"
            module = importlib.import_module(module_path)
            logger.info(f"Successfully imported module: {module_path}")

        except ModuleNotFoundError as e:
            logger.error(f"Module not found: {module_name}")
            raise ModuleNotFoundError(f"Module '{module_name}' not found in lab directory") from e

        try:
            # main 関数を取得
            main_func = getattr(module, "main")
            logger.info(f"Successfully found main function in module: {module_name}")

        except AttributeError as e:
            logger.error(f"main function not found in module: {module_name}")
            raise AttributeError(f"Module '{module_name}' does not have a 'main' function") from e

        try:
            # main関数を実行してyield
            result = main_func(**args)

            # main関数がジェネレーターを返す場合
            if hasattr(result, "__iter__") and hasattr(result, "__next__"):
                try:
                    yield from result
                except Exception as e:
                    logger.error(f"Error during generator execution in module {module_name}: {e}")
                    yield f"ERROR: {str(e)}"
            else:
                # main関数が単一の値を返す場合
                yield str(result)

            logger.info(f"Successfully executed main function for module: {module_name}")

        except Exception as e:
            logger.error(f"Error executing main function in module {module_name}: {e}")
            yield f"ERROR: {str(e)}"
