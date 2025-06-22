import asyncio
import logging
import time
from datetime import datetime
from typing import Generator

from asgiref.sync import async_to_sync
from django.http import HttpRequest, JsonResponse, StreamingHttpResponse
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from services.lab_module_execute_sse_service import LabModuleExecuteSSEService
from services.lab_module_spec_service import LabModuleSpecService
from shared.sse_formatters import SSEFormatter

logger = logging.getLogger(__name__)


@api_view(["GET", "POST"])
def foo_view(request: HttpRequest):
    """
    View を関数ベースで実装するパターン。
    - ひとつのエンドポイントに対して、ひとつの HTTP メソッドを定義するんだったら一番シンプルなんじゃない?
    - でもこのように↓複数 HTTP メソッドが欲しいなら分岐ができちゃう。クラスベースのほうがいいんじゃない?

    POST 面倒くさいよね? どうぞ curl です。
    curl -i -X POST http://localhost:8001/api/app/foo \
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

    def get(self, request: HttpRequest, *args, **kwargs) -> StreamingHttpResponse:
        """
        SSE ストリームを開始する。
        """
        response = StreamingHttpResponse(self._create_sse_stream(request), content_type="text/event-stream")
        response["Cache-Control"] = "no-cache"
        return response

    def _create_sse_stream(self, request: HttpRequest) -> Generator[str, None, None]:
        """
        SSE形式のストリームを作成する。
        """
        try:
            # 接続開始メッセージ
            yield SSEFormatter.format_message(request.request_id, "SSE connection started")

            # ビジネスロジックからメッセージを取得してSSE形式に変換
            for i, message in enumerate(self._generate_demo_messages(), 1):
                yield SSEFormatter.format_message(request.request_id, message, progress=f"{i * 10}%")
                logger.info(f"SSE message sent: {message}")

            # 完了メッセージ
            yield SSEFormatter.format_completion(request.request_id)
            logger.info("SSE stream completed")

        except Exception as e:
            # エラーが発生した場合のログ出力
            logger.error(f"SSE stream error: {e}")
            # エラーメッセージをクライアントに送信
            yield SSEFormatter.format_error(request.request_id, f"SSE stream error occurred: {str(e)}")

    def _generate_demo_messages(self) -> Generator[str, None, None]:
        """
        デモメッセージを生成する。
        10回のメッセージを1秒間隔で生成する。

        NOTE: 本メソッドの機能は本当なら Service 層に定義したい。
              本クラスはサンプルなので、ここに書いてるだけ。
              将来的には SSEStreamService のような専用サービスに移動を検討。
        """
        for i in range(1, 11):
            time.sleep(1)
            yield f"Message {i} of 10"


class LabView(APIView):
    """
    Lab API エンドポイント。

    使用例:
    curl -i -X GET "http://localhost:8001/api/app/lab?module=foo_bar_baz"

    urls では:
    path('v1/lab', views.LabView.as_view())
    """

    def get(self, request, *args, **kwargs):
        """
        モジュール情報を返す API。
        """
        # クエリパラメータから module を取得
        module_name = request.GET.get("module")

        if not module_name:
            # NOTE: エラー処理はなるべく DRF の機能を使うようにしている。
            #       shared.exception_handlers.custom_exception_handler へ飛んでいきます。
            raise ValidationError({"module": ["This query parameter is required."]})

        # LabModuleSpecService を使用してモジュール仕様を取得
        service = LabModuleSpecService()

        try:
            module_spec = service.get_module_spec(module_name)

            response_data = {
                "requestId": request.request_id,
                "message": f"How to use {module_name}",
                "data": {
                    "module": module_spec.module,
                    "description": module_spec.description,
                    "args": module_spec.args,
                },
            }

            return JsonResponse(response_data)

        except ModuleNotFoundError:
            # モジュールが見つからない場合
            raise ValidationError({"module": [f"Module '{module_name}' not found in lab directory."]})

        except AttributeError:
            # get_spec 関数が見つからない場合
            raise ValidationError({"module": [f"Module '{module_name}' does not have a 'get_spec' function."]})

    def post(self, request, *args, **kwargs):
        """
        モジュールを実行する API (SSE ストリーミング対応)。
        """
        # リクエストボディからmoduleとargsを取得
        module_name = request.data.get("module")
        args = request.data.get("args", {})

        if not module_name:
            raise ValidationError({"module": ["This field is required."]})

        if not isinstance(args, dict):
            raise ValidationError({"args": ["This field must be a dictionary."]})

        # SSE ストリーミングレスポンスを返却
        response = StreamingHttpResponse(
            self._create_lab_sse_stream(request, module_name, args), content_type="text/event-stream"
        )
        response["Cache-Control"] = "no-cache"
        return response

    def _create_lab_sse_stream(self, request: HttpRequest, module_name: str, args: dict) -> Generator[str, None, None]:
        """
        Lab モジュール実行の SSE ストリームを作成する。
        """
        try:
            # 開始メッセージ
            yield SSEFormatter.format_message(
                request.request_id, f"Starting module: {module_name}", module=module_name, args=args
            )
            logger.info(f"Lab module execution started: {module_name}")

            # LabModuleExecuteSSEService を使用してモジュールを実行
            sse_service = LabModuleExecuteSSEService()

            for message in sse_service.execute_module_sse(module_name, args):
                # execute_module_sse から受け取ったメッセージをそのまま SSE 形式でフォーマット
                yield SSEFormatter.format_message(request.request_id, message, module=module_name)
                logger.info(f"Lab module message sent: {message}")

            # 完了メッセージ
            yield SSEFormatter.format_completion(request.request_id, module=module_name)
            logger.info(f"Lab module execution completed: {module_name}")

        except (ModuleNotFoundError, AttributeError) as e:
            # モジュール/関数の存在チェックエラー (設定ミス)
            logger.error(f"Lab module configuration error: {e}")
            yield SSEFormatter.format_error(request.request_id, str(e), module=module_name)

        except Exception as e:
            # その他の予期しないエラー
            logger.error(f"Lab module execution error: {e}")
            yield SSEFormatter.format_error(request.request_id, f"Unexpected error: {str(e)}", module=module_name)
