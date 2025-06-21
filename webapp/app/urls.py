from django.urls import path

from . import views

urlpatterns = [
    # djangorestframework 関数ベース @api_view で実装した View。
    path('foo', views.foo_view),
    # djangorestframework クラスベース APIView で実装した View。
    path('bar', views.BarView.as_view()),
    # djangorestframework クラスベース APIView で実装した async View。
    path('baz', views.BazView.as_view()),
]
