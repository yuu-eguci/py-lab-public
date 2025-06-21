DEPLOY_ON_UBUNTU (React 時代)
===

## 初期デプロイ

```bash
# Ubuntu 22 は素の状態であるとする。

# firewall で 80 ポートを開ける。
# Azure VM でインバウンドポートルールを追加する例↓
#     - Source: Any
#     - Source port ranges: *
#     - Destination: Any
#     - Service: Custom
#     - Destination port ranges: 80
#     - Protocol: TCP
#     - Action: Allow
#     - Priority: 100（適切な値に変更してね）
#     - Name: HTTP-Inbound
#     - Description: Allow HTTP traffic

# Ubuntu へログインする
# いや、まあ Remote-SSH がベストだろう。
ssh -i ~/.ssh/id_rsa USERNAME@IP_ADDRESS

# Git をアップデート
sudo add-apt-repository ppa:git-core/ppa
sudo apt update
sudo apt install git -y
git --version
# --> git version 2.43.2

# Docker をインストール
# まあここは毎回改めて調べている。
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
# Docker の公式 GPG キー を追加
# 「このソフトウェア、本当に公式が作ったやつだよ！」って証明するための電子的な署名キー
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo tee /etc/apt/keyrings/docker.asc > /dev/null
sudo chmod a+r /etc/apt/keyrings/docker.asc
# Docker リポジトリを追加
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
# 動作確認 (Hello world コンテナ)
sudo docker run hello-world
# docker compose の確認
docker compose version

# Nginx をインストール
sudo apt update
sudo apt install nginx -y
sudo systemctl start nginx
sudo systemctl enable nginx
sudo systemctl status nginx
# 動作確認
# http://130.33.7.118
# http://banana.hitoren.net

# ローカルリポジトリを用意
REPO_NAME=django-react-gemini
sudo mkdir -p /var/www
(cd /var/www; sudo git clone https://github.com/yuu-eguci/${REPO_NAME}.git)
sudo chown -R $(whoami):$(whoami) /var/www/${REPO_NAME}

# リリースブランチがあるならここで設定
(cd /var/www/${REPO_NAME}; sudo git checkout staging)
(cd /var/www/${REPO_NAME}; sudo git fetch origin)
(cd /var/www/${REPO_NAME}; sudo git reset --hard origin/staging)
# ブランチ変更によって追加されたフォルダにも chown が必要そう
sudo chown -R $(whoami):$(whoami) /var/www/${REPO_NAME}

# .env を用意する
cp /var/www/${REPO_NAME}/local.env /var/www/${REPO_NAME}/.env
# ここで .env をちゃんとしたものへ編集。 Remote-SSH のおかげでラク。

# Dockefile を用意する
cp /var/www/${REPO_NAME}/webapp-container/Dockerfile.staging /var/www/${REPO_NAME}/webapp-container/Dockerfile
# こっちは編集不要のはず。

# Docker を起動する
# NOTE: うまくいっていれば、ここで migrate, collectstatic, gunicorn まで実行されるはず
(cd /var/www/${REPO_NAME}; sudo docker compose up -d)
# ログを確認
# migration log とか gunicorn のログがあれば OK.
(cd /var/www/${REPO_NAME}; sudo docker compose logs -f --tail=20 webapp-service)
# collectstatic できていることを確認
(cd /var/www/${REPO_NAME}/webapp/static; ls -l)
# gunicorn で起動していることを確認
curl http://localhost:8001/

# Nginx を設定する
sudo ln -sf /var/www/${REPO_NAME}/env-staging/staging-nginx.conf /etc/nginx/conf.d/default.conf
# NOTE: /etc/nginx/nginx.conf の中に 'include /etc/nginx/conf.d/*.conf;' の記載がある。
#       そこで読んでもらうことを意図しています。
#       (あと、デフォルトの設定ファイルの編集を避けるのも意図。)

# これ↓をコメントアウトする (自分の設定とバッティングするから)
# include /etc/nginx/sites-enabled/*;
# nano なので、 ^O + Enter で保存して、 ^X で終了する
sudo nano /etc/nginx/nginx.conf

sudo nginx -t
# リロード。
sudo systemctl reload nginx
# --> curl http://localhost
# 切っておく
sudo systemctl stop nginx

# Django をサービスへ登録する
# NOTE: cat とか EOF を使うのは、改行と変数展開に対応するためっぽい。
sudo bash -c "cat > /etc/systemd/system/webapp-service.service <<EOF
[Unit]
Description=Start webapp-service via Docker Compose
Requires=docker.service
After=docker.service

[Service]
WorkingDirectory=/var/www/${REPO_NAME}
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose stop
Restart=always
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF"
sudo systemctl daemon-reload
sudo systemctl enable webapp-service
sudo systemctl start webapp-service
sudo systemctl stop webapp-service
```

## HTTPS 化

最初に設定するときは、 nginx.conf の設定は port 80 状態のままこれ↓を打って大丈夫。
不正な pem パスが nginx.conf に存在する状態でこれ↓をやるとエラーになる。

```bash
# Certbot のインストール
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo add-apt-repository ppa:certbot/certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# SSL/TLS 証明書の取得
sudo certbot certonly --nginx -d www.mrrhp.com
sudo certbot --nginx -d www.mrrhp.com

# 自動更新 (えっ、いまそれ自動なの?!)
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
sudo systemctl status certbot.timer

sudo systemctl restart nginx
```

## MySQL リセットノート

```bash
REPO_NAME=django-react-gemini

# コンテナを削除
(cd /var/www/${REPO_NAME}$; sudo docker compose down)

# MySQL データ削除
sudo rm -rf /var/www/${REPO_NAME}$/data

# コンテナ再構築
(cd /var/www/${REPO_NAME}$; sudo docker compose up -d)

# ログを確認
(cd /var/www/${REPO_NAME}$; sudo docker compose logs -f --tail=20 webapp-service)
(cd /var/www/${REPO_NAME}$; sudo docker compose logs -f --tail=20 mysql-service)

# 中に入って確認
(cd /var/www/${REPO_NAME}$; docker compose exec webapp-service sh)
```

## ソースコードを修正したときのデプロイ

```bash
# Ubuntu へログインする
# いや、まあ Remote-SSH がベストだろう。
ssh -i ~/.ssh/id_rsa USERNAME@IP_ADDRESS

# ローカルリポジトリを最新化
REPO_NAME=django-react-gemini
(cd /var/www/${REPO_NAME}; sudo git fetch origin)
(cd /var/www/${REPO_NAME}; sudo git pull)
# NOTE: mrrhp ではこういうことやってるよね。
# (cd /var/www/${REPO_NAME}; sudo git reset --hard origin/release)

# いちおう権限をつけなおしておく
sudo chown -R $(whoami):$(whoami) /var/www/${REPO_NAME}

# 必要であれば .env を更新する

# Dockefile を更新する。
cp /var/www/${REPO_NAME}/webapp-container/Dockerfile.staging /var/www/${REPO_NAME}/webapp-container/Dockerfile

# Docker Compose を使ってコンテナを起動
# Dockerfile の変更を適用するために `--build` が必要。
(cd /var/www/${REPO_NAME}; sudo docker compose up -d --build)

# webapp-service を再起動
# これは webapp-service の Dockerfile にある CMD を再実行するためのコマンド。
# Dockerfile に変更があれば `--build` の時点で CMD も再実行されるけれど、
# そうでなければ `restart` 何もしてくれないから、こっちで再実行する。
(cd /var/www/${REPO_NAME}; sudo docker compose restart webapp-service)

# ログを確認
(cd /var/www/${REPO_NAME}; sudo docker compose logs -f --tail=20 webapp-service)

# webapp-service で React をビルドする (dist を更新!)
(cd /var/www/${REPO_NAME}; sudo docker compose exec webapp-service sh -c "yarn install")
(cd /var/www/${REPO_NAME}; sudo docker compose exec webapp-service sh -c "yarn build")

# (nginx.conf.production を変更した場合) Nginx 再起動
# 設定ファイルのテスト
sudo nginx -t
sudo systemctl restart nginx
```

## ログ

```bash
REPO_NAME=django-react-gemini
(cd /var/www/${REPO_NAME}; sudo docker compose logs -f --tail=20 webapp-service)
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```
