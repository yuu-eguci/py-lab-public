import asyncio
import logging
from datetime import datetime

from asgiref.sync import async_to_sync
from django.http import HttpRequest, JsonResponse
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
    curl -X POST http://localhost:8001/api/app/bar \
        -H "Content-Type: application/json" \
        -d '{"value": "bar"}'

    urls では:
    path('bar', views.BarView.as_view())
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
