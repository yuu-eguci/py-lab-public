py-lab-public
===

🐍 ⚛️ 🐳 🇳 Python 3.14 + Django 6.1 + React 19 + Docker + SSE (Server-Sent Events)

## Status

- Docker: 対応!
- Python 3.14 / Django 6.1 / Django REST framework 3.18 / MySQL 8.4
- Node.js 22 / React 19 / Vite 6 / MUI 7
- Linter: Ruff, ESLint
- Tests: Django test runner, Vitest (GitHub Actions で PR ごとに実行します)
- Quick start: `cp ./local.env ./.env && cp ./webapp-container/Dockerfile.local ./webapp-container/Dockerfile && docker compose up -d` (このあとの手順は下の「runserver と yarn dev で起動するところまで」にあります)

## Description

- へー、 SSE っていうのがあるんだ。なんかに使ってみたいなー。
- (この間、3年くらいの年月が流れた……)
- 土曜の朝のぼく「Server 側で実行した Python の log を逐一ブラウザに返すとかできるんじゃね?!」
- 土曜の朝のぼく「やる!」
- 日曜の夜のぼく「できた!」

https://github.com/user-attachments/assets/c5119bfe-03f8-423e-b47b-b203d84270bc

ちなみにこちらは `text/event-stream (SSE)` を受け取る Postman はこんなふうになる、という図。豆知識となっております。

![](./docs/(2025-06-22)postman-demo.png)

- 将来的にはこんなふうにしたい↓
    - いろんな Python scripts を lab に置く
    - React のフロントエンドから、実行したい script を選ぶ
    - ポチッと押すとその script が実行されて、進捗も見れるし結果もブラウザ上で得られる

このリポジトリは django-react-gemini を template にしている↓

***

django-react-gemini ♊
===

🐍 ⚛️ 🐳 🇳 Python 3.13 + Django v4 + Yarn + React + Nginx + Docker + GitHub Actions + Ruff + CI/CD | React も使いてーし、 Django も使いてーけど、サーバはふたつも使いたくねーから、 Nginx を使って Django と React を同ドメインで配信しよーぜ。あと Docker は当然使うぜ。

## コイツのいいところ

- Docker 環境 + Django + React (frontend) + MySQL + Nginx がひとつのリポジトリに詰まっててシンプルだよ。
    - まあいいことばかりじゃないけど。
- up で3つ一気に立ち上がるよ。
- 開発環境:
    - Django runserver (8000) -> docker-compose portforward (8001) -> localhost:8001
    - React yarn dev (5173) -> docker-compose portforward (5001) -> localhost:5001
- Ubuntu 環境:
    - Django Dockerfile gunicorn (8000) -> docker-compose portforward (8001) -> nginx (80) -> domain:80
    - 

### Django エリアのいいところ

- 開発環境用、本番環境用の settings が分かれてるよ。
- 当然 Pipenv で管理できてるよ。
- コンソールと、 ./logs/ へのロギングができてるよ。ロギングの日時は UTC と JST を選べる。
- ユニットテストの基礎もちゃんとあるよ。
- ひさしぶりに来て、 "view どんなふうに書くんだっけ?" ってなったときのため views に view のベースを書いてるよ。
    - 最近、 async の view も足しといたよ。ただ動かすにはこれ↓が必要かも
    - uvicorn (asgi サーバ) を pip install
    - gunicorn が内蔵の wsgi サーバのみならず uvicorn を動かせるように設定する
    - そうすると gunicorn が uvicorn を worker として動かして、
    - uvicorn は asgi サーバとして django を配信してくれる!
- GitHub Actions で ruff, test がちゃんと走るよ。 main への push と PR で動きます。
- プロジェクト内部のモジュールをインポートするときは、つねに相対インポートを使ってる (3rd party との区別のため) よ。

### React エリアのいいところ

- `vite-tsconfig-paths` とか `react-router-dom` とか `react-i18next` とか導入済み。
- "さあオリジナリティ出していくぜ、" のひとつ前の段階まで揃えてある。
    - これ以上をやると、オリジナリティを出していくときの邪魔になる。

### Nginx エリアのいいところ

- Apache ではない (笑)

### いいことばかりじゃないところ

- 1アプリケーションにつき1 docker container を使うと、 VSCode 開発のときに devcontainer をキレイに使えたりして利点がある。ひとつの container に複数アプリケーションが入っていると、その利点を利用することが不可。

## runserver と yarn dev で起動するところまで

```bash
# NOTE: (2025-03-04) 久しぶりに clone してみたけど、マジで
#       Create containers -> Django のほう
#       をサッサと打つだけで開始できた。イイぞ。

# Create containers
cp ./local.env ./.env; cp ./webapp-container/Dockerfile.local ./webapp-container/Dockerfile;
docker compose up -d; docker compose exec webapp-service bash

# Get into webapp-service
# NOTE: It's a good practice to have separate terminals for Django and React for easier debugging and log tracking.
docker compose exec webapp-service bash
# Check↓
python -V
# --> Python 3.14.x
pipenv --version
# --> pipenv, version 2026.10.5
yarn -v
# --> 1.22.22

(cd ./frontend-react; yarn list react)
# --> └─ react@19.1.0

# Django のほう。
# NOTE: PIPENV_VENV_IN_PROJECT は env で設定してある。
pipenv sync --dev
pipenv run python manage.py migrate
pipenv run python manage.py runserver 0.0.0.0:8000
# --> http://localhost:8001/ でアクセス。

# React のほう。
(cd ./frontend-react; yarn install)
(cd ./frontend-react; yarn dev --host)
# --> http://localhost:5001/ でアクセス。
```

```bash
# Test commands.
time pipenv run ruff check .
time pipenv run python manage.py test --failfast --parallel --settings=config.settings_test

# run 無し: watch mode
# run 有り: いつもの
(cd ./frontend-react; time yarn test run)
(cd ./frontend-react; time yarn lint)
```

```bash
# i18n commands.
(cd ./frontend-react; yarn run i18next "./src/App.tsx" "./src/**/*.tsx" --config "./i18next-parser.config.js")
```
