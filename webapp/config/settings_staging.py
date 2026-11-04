import os

from .settings import *  # noqa: F401, F403

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'middlewares.request_id_middleware.RequestIDMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# NOTE: staging は外から見えるので DEBUG は切っています。 (エラーページに設定の中身が出てしまうため。)
DEBUG = False

# 受け付けるドメインです。 .env の DJANGO_ALLOWED_HOSTS にカンマ区切りで書きます。
ALLOWED_HOSTS = [host.strip() for host in os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost').split(',')]
ALLOWED_HOSTS = [host for host in ALLOWED_HOSTS if host]
