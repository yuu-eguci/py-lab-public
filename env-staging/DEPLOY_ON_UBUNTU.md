DEPLOY_ON_UBUNTU (React 時代)
===

NOTE: いちいち UBUNTU のほうも更新するの面倒なんだよね……デプロイ環境のほうはこれ↓をベースにうまくやって。

## デプロイパッケージを作る

```bash
# Repository から zip をダウンロード。

# トップディレクトリでターミナルを。

# staging.env をチェック。 (staging.env を置くこと)
[ -f ./staging.env ] && echo "Env exists, proceed." || echo "Error: No env."

# Nuxt.js の静的サイトを生成して static フォルダへ配置。
(cd ./webapp/frontend-nuxt; yarn install)

# UBUNTU 環境用の .env を適用してビルド。
# NOTE: .env 内部のコメント行を grep で無視しつつ行う。
(cd ./webapp/frontend-nuxt; env $(grep -v '^#' ../../staging.env | xargs) yarn generate --production)

mkdir ./webapp/static; mv ./webapp/frontend-nuxt/dist/* ./webapp/static/

# デプロイパッケージに必要なものを集める。
mkdir ./deploy_package
rsync -av --exclude='.DS_Store' --exclude='webapp/.gitignore' --exclude='webapp/frontend-nuxt/*' docker-compose.yml mysql-container staging.env webapp webapp-container ./deploy_package/
# staging.env -> .env
mv ./deploy_package/staging.env ./deploy_package/.env
# Dockerfile-staging -> Dockerfile
mv ./deploy_package/webapp-container/Dockerfile-staging ./deploy_package/webapp-container/Dockerfile

# zip 化。
zip -r deploy_package.zip deploy_package/

# デプロイパッケージをサーバへ UL。 (コマンドは別メモに。 IP とか入ってるからさ。)
scp -i ~/.ssh/???.pem deploy_package.zip username@ip:~/
```

## デプロイパッケージを展開する

```bash
# デプロイ先のサーバへ ssh 接続。

# デプロイパッケージを展開。
sudo unzip ~/deploy_package.zip -d ~/

# 中身を /webapp へコピー。
# NOTE: ~/deploy_package/* って書くと .env を無視する。 (えぇ〜)
sudo cp -r ~/deploy_package/. /webapp/

# ~/deploy_package.zip と ~/deploy_package/ を削除
sudo rm -rf ~/deploy_package.zip ~/deploy_package/
```

## Docker を起動する

```bash
# Docker 存在確認。
docker --version
# --> Docker version 24.0.6, build ed223bc

# Docker コンテナを起動。 (--build は最初だけ。)
(cd /webapp; sudo docker compose up -d)

(cd /webapp; sudo docker compose logs -f --tail=10 webapp-service)

# MySQL のユーザを確認。
(cd /webapp; sudo docker compose exec mysql-service sh)
# mysql -u StagingAdmin -p
# --> Enter password: ??? (stage.env に書いてある) --> 入れることを確認
# SHOW DATABASES; --> app があることを確認
# exit
```

## Django をサービスへ登録する

```bash
sudo nano /etc/systemd/system/webapp-service.service
```

```conf
[Unit]
Description=Start webapp-service via Docker Compose
Requires=docker.service
After=docker.service

[Service]
WorkingDirectory=/webapp
ExecStartPre=-/usr/local/bin/docker-compose down
ExecStart=/usr/local/bin/docker-compose up webapp-service
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable webapp-service
sudo systemctl start webapp-service
sudo systemctl stop webapp-service
# --> curl http://localhost:8001
```

## Nginx を起動する

```bash
# nginx の設定を追加。
# NOTE: /etc/nginx/nginx.conf の中に 'include /etc/nginx/conf.d/*.conf;' の記載がある。
#       そこで読んでもらうことを意図しています。
#       (あと、デフォルトの設定ファイルの編集を避けるのも意図。)
sudo cp /webapp/staging-nginx.conf /etc/nginx/conf.d/default.conf

sudo nginx -t

# リロード。
sudo systemctl reload nginx
# --> curl http://localhost
```
