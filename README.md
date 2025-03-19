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

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細はLICENSEファイルを参照してください。

## サポート

問題や質問がある場合は、GitHubのIssueを作成してください。