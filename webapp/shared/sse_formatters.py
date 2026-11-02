import json
from collections.abc import Iterable

from django.http import StreamingHttpResponse
from django.utils import timezone


def create_sse_response(stream: Iterable[str]) -> StreamingHttpResponse:
    """
    SSE のストリームを返す StreamingHttpResponse を作ります。

    NOTE: Cache-Control: no-cache でキャッシュさせず、
          X-Accel-Buffering: no で nginx などのプロキシにバッファさせないようにしています。
          バッファされると、メッセージが逐一ではなく最後にまとめて届いてしまいます。

    Args:
        stream (Iterable[str]): SSEFormatter で整形したイベントを yield するもの

    Returns:
        StreamingHttpResponse: text/event-stream のレスポンス
    """
    response = StreamingHttpResponse(stream, content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response


class SSEFormatter:
    """
    Server-Sent Events (SSE) 形式のメッセージをフォーマットするクラス。
    NOTE: マイ SSE 勉強メモ
          SSE は、 StreamingHttpResponse + content_type="text/event-stream" で実現するっぽい。
          なんかよく分かんないんだが、 SSE では、 `data: ここにメッセージ\n\n` という形式を使うらしい。
          payload は json.dumps で 1 行にしているので、メッセージ中の改行でイベントが割れることはありません。
          DOC: https://html.spec.whatwg.org/multipage/server-sent-events.html#server-sent-events
    """

    @staticmethod
    def format_message(request_id: str, message: str, **extra_data) -> str:
        """
        メッセージを SSE 形式にフォーマットする。

        Args:
            request_id (str): リクエストID
            message (str): フォーマットするメッセージ
            **extra_data: data 内に追加するフィールド

        Returns:
            str: SSE 形式の文字列 ("data: {...}\n\n")
        """
        response = {
            "requestId": request_id,
            "data": {"message": message, "sentAt": timezone.now().strftime("%Y-%m-%dT%H:%M:%S%z"), **extra_data},
        }
        return f"data: {json.dumps(response)}\n\n"

    @staticmethod
    def format_error(request_id: str, error_message: str, **extra_data) -> str:
        """
        エラーメッセージを SSE 形式にフォーマットする。

        Args:
            request_id (str): リクエストID
            error_message (str): エラーメッセージ
            **extra_data: data 内に追加するフィールド

        Returns:
            str: SSE 形式のエラーメッセージ
        """
        response = {
            "requestId": request_id,
            "data": {"error": error_message, "sentAt": timezone.now().strftime("%Y-%m-%dT%H:%M:%S%z"), **extra_data},
        }
        return f"data: {json.dumps(response)}\n\n"

    @staticmethod
    def format_completion(request_id: str, **extra_data) -> str:
        """
        完了メッセージを SSE 形式にフォーマットする。

        Args:
            request_id (str): リクエストID
            **extra_data: data 内に追加するフィールド

        Returns:
            str: SSE 形式の完了メッセージ
        """
        response = {
            "requestId": request_id,
            "data": {
                "message": "Stream completed",
                "sentAt": timezone.now().strftime("%Y-%m-%dT%H:%M:%S%z"),
                **extra_data,
            },
        }
        return f"data: {json.dumps(response)}\n\n"
