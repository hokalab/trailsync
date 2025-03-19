# TrailSync

TrailSyncは、ヤマレコのGPXファイルをRunkeeper互換フォーマットに変換するツールです。特に複数日にわたるアクティビティデータの正確な変換に対応しています。

## 特徴

- 複数日にわたるアクティビティデータの正確な変換
- アクティビティタイプの明示的な指定（ハイキング、ランニングなど）
- メタデータセクションの追加
- XMLフォーマットの構造化オプション
- 拡張されたコマンドラインオプション

## 使い方

### コマンドラインから使用

```bash
# リポジトリをクローン
git clone https://github.com/mump0nd/trailsync.git
cd trailsync

# 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Linuxの場合
# venv\Scripts\activate  # Windowsの場合

# 依存パッケージのインストール
pip install -r requirements.txt

# 改良版スクリプトを実行
python src/yamareco_to_runkeeper_improved.py input.gpx -o output.gpx
```

### Webアプリケーション

TrailSyncはWebアプリケーションとしても利用できます。以下のURLでアクセスできます：

[TrailSync Demo](https://trailsync-ziew.onrender.com)

または、ローカルで実行することもできます：

```bash
# リポジトリをクローン
git clone https://github.com/mump0nd/trailsync.git
cd trailsync

# 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Linuxの場合
# venv\Scripts\activate  # Windowsの場合

# 依存パッケージのインストール
pip install -r requirements.txt

# アプリケーションを実行
python app.py
```

ブラウザで http://localhost:8050 を開くと、ローカルで実行されているTrailSyncのWebインターフェースが表示されます。

## Renderへのデプロイ

### 自動デプロイの設定

TrailSyncプロジェクトのRenderデプロイフックは以下のURLで設定されています：

```
YOUR WEBHOOK URL
```

GitHubのリポジトリからRenderへの自動デプロイを設定するには、以下の手順に従います：

1. GitHubのリポジトリページ（https://github.com/mump0nd/trailsync）に移動します
2. 「Settings」タブを選択します
3. 左側のメニューから「Webhooks」を選択します
4. 「Add webhook」ボタンをクリックします
5. 以下の情報を入力します：
   - 「Payload URL」: `YOUR WEBHOOK URL`
   - 「Content type」: `application/json`
   - 「Which events would you like to trigger this webhook?」: `Just the push event`
   - 「Active」チェックボックスをオンにします
6. 「Add webhook」ボタンをクリックして設定を完了します

これにより、GitHubのリポジトリにプッシュがあるたびに、Renderのデプロイフックが呼び出され、自動的にデプロイが開始されます。

### 手動デプロイ

Webhookの設定が完了するまで、または設定に問題がある場合は、以下の方法で手動でデプロイをトリガーできます：

1. Renderのダッシュボードにログインする
2. デプロイするサービスを選択する
3. 「Manual Deploy」ボタンをクリックする
4. 「Deploy latest commit」を選択する

または、curlコマンドを使用してデプロイフックURLにPOSTリクエストを送信することもできます：

```bash
curl -X POST YOUR WEBHOOK URL
```

あるいは、ブラウザで直接デプロイフックURLにアクセスすることもできます：

```
YOUR WEBHOOK URL
```

### Render CLIを使用したデプロイとログの確認

Render CLIを使用すると、コマンドラインからRenderのサービスを管理し、ログを確認することができます。

#### Render CLIのインストール

```bash
# npmを使用してインストール
npm install -g @render/cli

# または、yarnを使用してインストール
yarn global add @render/cli
```

#### Render CLIの設定

初回使用時に認証が必要です：

```bash
render login
```

ブラウザが開き、Renderアカウントでの認証が求められます。認証が完了すると、CLIが使用可能になります。

#### デプロイの状態確認

```bash
# サービス一覧の表示
render list

# 特定のサービスの詳細を表示
render get-service trailsync
```

#### ログの確認

```bash
# 最新のデプロイログを表示
render logs trailsync

# リアルタイムでログを表示（tail -f のように）
render logs trailsync --follow

# 特定の時間範囲のログを表示
render logs trailsync --start "2025-03-18T00:00:00Z" --end "2025-03-19T00:00:00Z"

# ログの行数を制限
render logs trailsync --limit 100
```

#### 手動デプロイの実行

```bash
# 最新のコミットでデプロイを実行
render deploy trailsync

# 特定のブランチからデプロイを実行
render deploy trailsync --branch main
```

#### 環境変数の管理

```bash
# 環境変数の一覧表示
render env trailsync

# 環境変数の設定
render env set trailsync KEY=VALUE

# 環境変数の削除
render env unset trailsync KEY
```

詳細なコマンドオプションは、以下のコマンドで確認できます：

```bash
render --help
render logs --help
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細はLICENSEファイルを参照してください。

## サポート

問題や質問がある場合は、GitHubのIssueを作成してください。