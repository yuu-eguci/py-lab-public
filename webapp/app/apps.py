# NOTE: mypy に Name "AppConfig" already defined (possibly by an import)  [no-redef] って叱られる。
#       本来なら変更の必要はない。たまたまぼくのサービスが app っていう名前なので
#       AppConfig っていう名前でカブっちゃった。それを回避するためのもの。
from django.apps import AppConfig as OriginalAppConfig


class AppConfig(OriginalAppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
