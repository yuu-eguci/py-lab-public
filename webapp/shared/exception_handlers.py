import logging
from typing import Any

from django.http import JsonResponse
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | JsonResponse:
    """
    カスタム例外ハンドラ。500エラーの場合に詳細なロギングを行い、Json 形式でエラーメッセージを返す。

    Args:
        exc (Exception): 発生した例外オブジェクト。
        context (Dict[str, Any]): REST framework のコンテキスト情報。request オブジェクトなどが含まれる。

    Returns:
        Union[Response, JsonResponse]: エラーレスポンス。通常は REST framework のデフォルトレスポンスか、
                                       500エラーの場合は JsonResponse。
    """
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response: Response | None = exception_handler(exc, context)
    request: Request = context["request"]

    # 何であれエラーが発生した場合はロギング。
    logger.exception(f"Exception occurred during processing request ID: {request.request_id}")

    if response:
        return response

    # 500 エラーの場合はしっかりリクエストをロギング。
    logger.error(
        {
            "message": "Request that caused the Internal Server Error",
            "method": request.method,
            "path": request.path,
            "data": request.data,
            "request_id": request.request_id,
        }
    )
    return JsonResponse({"message": "Internal Server Error"}, status=HTTP_500_INTERNAL_SERVER_ERROR)
