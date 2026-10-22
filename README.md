# RunLog

ランニング・散歩の記録（距離・時間・メモ）を登録すると、その日の天気を
[OpenWeatherMap API](https://openweathermap.org/current) から自動で取得して一緒に保存する Web アプリです。

## 主な機能
- ユーザー登録 / ログイン / ログアウト
- 記録の登録・一覧・詳細・編集・削除（自分の記録のみ操作可能）
- 今日の日付で記録すると、その日の天気（天気・気温・湿度・風速）を自動で保存
- 一覧画面で、今月の合計距離と、日ごとの距離・天気を棒グラフで表示
- プロフィールで「よく走る都市」を設定（新規登録時の都市の初期値になる）

## 技術スタック
Python 3.12 / Django 5.x / MySQL 8.0 / Bootstrap 5 / Docker Compose

## セットアップ

**最初に環境変数ファイル（.env）を作成します**
- Mac、Windows(PowerShell、Git Bash)の場合
```.sh
cp .env.example .env
```
- Windows(コマンドプロンプト)の場合
```
copy .env.example .env
```

`.env` を開いて、以下の値を書き換えてください。

| 変数 | 内容 |
|---|---|
| `SECRET_KEY` | Django の秘密鍵。推測されにくい長いランダム文字列にする |
| `MYSQL_PASSWORD` / `MYSQL_ROOT_PASSWORD` | MySQL のパスワード |
| `OPENWEATHER_API_KEY` | OpenWeatherMap の API キー（無料プランで可）。空でもアプリは動くが、天気は取得されない |

※ `.env` は秘密情報を含むため、Git にコミットしないでください（`.gitignore` 済み）。

## 起動方法
1. イメージのビルド

```.sh
docker compose build
```
- `docker-compose.yml` の内容に従って、コンテナイメージをビルドします。
- 初回または依存パッケージを更新したときに実行してください。

2. コンテナの起動

```.sh
docker compose up
```
- コンテナを起動します。MySQL の起動を待ってから Django が立ち上がります。
- `-d` オプションをつけるとバックグラウンドで起動します。

3. データベースの初期化（初回のみ）

別のターミナルで実行します。

```.sh
docker compose exec web python manage.py migrate
```

停止したいときは `Ctrl + C` または以下のコマンドを使ってください：
```.sh
docker compose down
```
- DB のデータは `mysql_data` ボリュームに残ります。データも消す場合のみ `docker compose down -v` を使います。

**ブラウザで確認**
```
http://localhost:8000
```

「アカウントを作成」から登録し、「記録する」で今日の日付の記録を作ると、天気が一緒に保存されます。

### 管理画面（任意）
```.sh
docker compose exec web python manage.py createsuperuser
```
作成後、http://localhost:8000/admin/ にログインできます。

## 画面一覧
| 画面 | URL | ログイン |
|---|---|---|
| トップ | `/` | 不要 |
| ユーザー登録 | `/signup/` | 不要 |
| ログイン | `/login/` | 不要 |
| 記録一覧 | `/records/` | 必要 |
| 記録詳細 | `/records/<id>/` | 必要 |
| 新規登録 | `/records/new/` | 必要 |
| 編集 | `/records/<id>/edit/` | 必要 |
| 削除確認 | `/records/<id>/delete/` | 必要 |
| プロフィール | `/profile/` | 必要 |

## 天気取得の仕様
- 天気を取得するのは**新規登録時で、日付が今日の場合のみ**です（無料プランは現在の天気しか取れないため）。過去日付の記録は天気なしで保存されます。
- 編集時は天気を再取得しません（記録した時点の天気を残します）。
- 都市名は英語で入力します（例: `Tokyo`, `Osaka`）。
- API のエラーやタイムアウト、API キー未設定の場合でも、記録は保存され「天気を取得できませんでした」と表示されます。

## ディレクトリ構成
```
.
├── CLAUDE.md            # 開発方針（Claude Code 用）
├── DESIGN.md            # 画面デザインの指示書
├── config               # Django プロジェクト設定
│   ├── settings.py      # 設定（秘密情報は環境変数から読む）
│   ├── urls.py
│   └── wsgi.py
├── records              # Django アプリ（記録・認証・天気）
│   ├── models.py        # Profile / RunRecord / Weather
│   ├── forms.py         # フォームとバリデーション
│   ├── views.py         # 画面の処理
│   ├── urls.py          # URL 定義
│   ├── weather.py       # 天気 API の呼び出し（ここだけ）
│   ├── admin.py
│   ├── migrations
│   └── templates        # Template(HTML)用ディレクトリ
├── static
│   └── css
│       └── style.css    # 独自 CSS
├── .env.example         # 環境変数ファイル（.env）を作成する為のサンプルファイル
├── Dockerfile           # Django 用 Dockerファイル
├── docker-compose.yml   # Docker-composeファイル
├── manage.py
└── requirements.txt     # 使用モジュール記述ファイル（Django / mysqlclient / requests）
```
