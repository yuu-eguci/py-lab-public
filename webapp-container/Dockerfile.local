# 他の image はこちら https://hub.docker.com/_/python
FROM python:3.13-slim-bookworm

# 開発環境では .pyc をスキップ。
ENV PYTHONDONTWRITEBYTECODE 1
# 標準出力のバッファリングをスキップ。
ENV PYTHONUNBUFFERED 1

WORKDIR /webapp

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libmariadb-dev gcc libc-dev default-mysql-client pkg-config \
    nginx curl && \
    # NOTE: slim-bookworm のベースイメージには v18 しか無い。
    #       でも react-router-dom が新しめの node を要求してくる。
    #       Node の公式リポジトリから setup_current を使うと最新版が手に入る。
    #       しかし最新版は新しすぎるようで、 22 を指定。
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash && \
    apt-get install -y nodejs && \
    # キャッシュクリア。
    apt-get clean && \
    # 不要なパッケージリストを削除。
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools && \
    pip install -U pipenv

RUN npm install --global yarn

# NOTE: いやあ、ここで nginx.conf のコピーと nginx 起動を終えたほうが docker の使い方としてはいいんだけど、
#       mount している webapp フォルダの中にあったほうが、コンテナ内で色々試せるのでいいかなって……。
# COPY nginx.conf /etc/nginx/http.d/default.conf
# CMD ["sh", "-c", "nginx -g daemon off"]

# NOTE: まだぼくは "自分で起動すればよくね?" って思ってる派。
# CMD ["sh", "-c", "pipenv sync --dev && pipenv run python manage.py migrate && pipenv run server 0.0.0.0:8000"]
