import asyncio
import json
import logging
import time
from datetime import datetime

from asgiref.sync import async_to_sync
from django.http import HttpRequest, JsonResponse, StreamingHttpResponse
from rest_framework.decorators import api_view
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


@api_view(["GET", "POST"])
def foo_view(request: HttpRequest):
    """
    View を関数ベースで実装するパターン。
    - ひとつのエンドポイントに対して、ひとつの HTTP メソッドを定義するんだったら一番シンプルなんじゃない?
    - でもこのように↓複数 HTTP メソッドが欲しいなら分岐ができちゃう。クラスベースのほうがいいんじゃない?

    POST 面倒くさいよね? どうぞ curl です。
    curl -X POST http://localhost:8001/api/app/foo \
        -H "Content-Type: application/json" \
        -d '{"value": "foo"}'

    urls では:
    path('foo', views.foo_view)
    """

    if request.method == "GET":
        return JsonResponse({"requestId": request.request_id, "message": "This endpoint is GET foo."})
    elif request.method == "POST":
        return JsonResponse({"requestId": request.request_id, "message": "This endpoint is POST foo."})


class BarView(APIView):
    """
    というわけで View をクラスベースで実装するパターン。
    - ちょっと複雑になるけど、ひとつのエンドポイントに対して、複数 HTTP メソッドを定義できる。

    POST 面倒くさいよね? どうぞ curl です。
    curl -X POST http://localhost:8001/api/app/bar \
        -H "Content-Type: application/json" \
        -d '{"value": "bar"}'

    urls では:
    path('bar', views.BarView.as_view())

    まとめ:
    - "関数ベースの @api_view とクラスベースの APIView はどう違う?"
        - 自分なりの回答: ひとつのエンドポイントに対して、複数 HTTP メソッドを定義するときのキレイさが違うよ。
    """

    def get(self, request, *args, **kwargs):
        # NOTE: shared.exception_handlers.custom_exception_handler を試すためにわざと例外を発生させているよ。
        raise NotImplementedError(
            "To test custom_exception_handler, this endpoint raises NotImplementedError intentionally."
        )
        return JsonResponse({"requestId": request.request_id, "message": "This endpoint is GET bar."})

    def post(self, request, *args, **kwargs):
        return JsonResponse({"requestId": request.request_id, "message": "This endpoint is POST bar."})


class BazView(APIView):
    """
    Async + クラスベースで実装するパターン。
    NOTE: 開発サーバでのみ動作を確認している。
          まだ良くわかっていないのだけど、 ASGI サーバでのみ有効なのかもしれない。

    POST 面倒くさいよね? どうぞ curl です。
    curl -X POST http://localhost:8001/api/app/baz \
        -H "Content-Type: application/json" \
        -d '{"value": "baz"}'

    urls では:
    path('baz', views.BazView.as_view())
    """

    def post(self, request, *args, **kwargs):
        # NOTE: Django の view は同期的 → async で定義することは不可。
        #       async_to_sync でラップすることで、 async を同期的に扱うことができる。
        #       djangorestframework はもともと async に非対応だが、これで対応できる。
        return async_to_sync(self.__post)(request)

    async def __post(self, request):
        await asyncio.gather(
            self.__wait_task("3秒待機", 3),
            self.__wait_task("2秒待機", 2),
            self.__wait_task("1秒待機", 1),
        )
        # 出力↓
        # [INFO] name='1秒待機' wait_time=1 now='11:13:50'
        # [INFO] name='2秒待機' wait_time=2 now='11:13:51'
        # [INFO] name='3秒待機' wait_time=3 now='11:13:52'
        # 同時に実行されている! これぞ async!

        return JsonResponse(
            {"requestId": request.request_id, "message": "This endpoint is POST baz for testing async view."}
        )

    async def __wait_task(self, name: str, wait_time: int):
        """
        指定した秒数待機して、完了時間を記録。
        """
        await asyncio.sleep(wait_time)
        now = datetime.now().strftime("%H:%M:%S")
        logger.info(f"{name=} {wait_time=} {now=}")


class SSEView(APIView):
    """
    SSE (Server-Sent Events) でクライアントに少しずつメッセージを返すパターン。

    使用例:
    curl -i --no-buffer -X GET http://localhost:8001/api/app/sse

    または JavaScript で:
    const eventSource = new EventSource('http://localhost:8001/api/app/sse');
    eventSource.onmessage = function(event) {
        console.log('Received:', event.data);
    };

    urls では:
    path('sse', views.SSEView.as_view())
    """

    def get(self, request, *args, **kwargs):
        """
        SSE ストリームを開始する。
        """
        # SSE は、 StreamingHttpResponse + content_type="text/event-stream" で実現するっぽい。
        response = StreamingHttpResponse(self.__event_stream(request), content_type="text/event-stream")

        # ブラウザにキャッシュさせないよう設定 (よく分かってない)。
        response["Cache-Control"] = "no-cache"

        return response

    def __event_stream(self, request):
        """
        SSE イベントストリームを生成する。
        """

        # 接続開始メッセージ
        # なんかよく分かんないんだが、 SSE では、 `data: ここにメッセージ\n\n` という形式を使うらしい。
        # DOC: https://html.spec.whatwg.org/multipage/server-sent-events.html#server-sent-events
        start_message = {
            "requestId": request.request_id,
            "message": "SSE connection started",
            "timestamp": datetime.now().isoformat(),
        }
        yield f"data: {json.dumps(start_message)}\n\n"

        # 10回のメッセージを1秒間隔で送信
        for i in range(1, 11):
            time.sleep(1)

            message_data = {
                "requestId": request.request_id,
                "message": f"Message {i} of 10",
                "progress": f"{i * 10}%",
                "timestamp": datetime.now().isoformat(),
            }

            # SSE フォーマットでJSONデータを送信
            yield f"data: {json.dumps(message_data)}\n\n"

            logger.info(f"SSE message sent: {message_data}")

        # 完了メッセージ
        final_message = {
            "requestId": request.request_id,
            "message": "SSE stream completed",
            "timestamp": datetime.now().isoformat(),
        }
        yield f"data: {json.dumps(final_message)}\n\n"

        logger.info("SSE stream completed")
