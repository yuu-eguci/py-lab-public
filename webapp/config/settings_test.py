import os

from .settings import *  # noqa: F401, F403

# ユニットテストでは root ユーザーを使うための設定です。
# NOTE: ユニットテストで --parallel オプションを使うとき、
#       schema をクローンできる root ユーザーが必要です。
#       これ↓のこと
#       Creating test database for alias 'default'...
#       Cloning test database for alias 'default'...
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ['MYSQL_DATABASE'],
        'USER': 'root',
        'PASSWORD': os.environ['MYSQL_ROOT_PASSWORD'],
        'HOST': os.environ['MYSQL_HOSTNAME'],
        'PORT': os.environ['MYSQL_PORT'],
    }
}

DEBUG = False
