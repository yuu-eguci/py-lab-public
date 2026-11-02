import logging
from collections.abc import Callable, Generator, Iterator
from typing import Any

from .lab_module_loader import get_lab_function

logger = logging.getLogger(__name__)


class LabModuleExecuteSSEService:
    """
    Lab モジュールを実行して、 SSE で返すメッセージを作るサービスクラスです。
    """

    def get_main_function(self, module_name: str) -> Callable[..., Any]:
        """
        webapp.lab.{module_name} の main 関数を返します。
        ストリームを始める前に呼んで、モジュールが使えるかどうかを確かめるために使います。

        Args:
            module_name (str): モジュール名

        Returns:
            Callable[..., Any]: lab module の main 関数

        Raises:
            LabModuleError: モジュールが見つからない場合、または main 関数が定義されていない場合
        """
        return get_lab_function(module_name, "main")

    def execute_module_sse(self, main_func: Callable[..., Any], args: dict[str, Any]) -> Generator[str]:
        """
        main 関数を実行して、結果をメッセージ (str) として 1 件ずつ yield します。
        main がジェネレータなら yield された値を順に、そうでなければ戻り値をひとつ返します。

        NOTE: 例外はここでは握りつぶさずに呼び出し元へ投げます。
              また、このジェネレータが close されたら (クライアントの切断など) main のジェネレータも close します。

        Args:
            main_func (Callable[..., Any]): lab module の main 関数
            args (dict[str, Any]): main に渡す引数

        Yields:
            str: メッセージ
        """
        result = main_func(**args)

        if not isinstance(result, Iterator):
            yield str(result)
            return

        try:
            for message in result:
                yield str(message)
        finally:
            close = getattr(result, "close", None)
            if callable(close):
                close()
