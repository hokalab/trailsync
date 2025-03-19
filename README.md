# TrailSync

ヤマレコのGPXファイルをRunkeeper互換フォーマットに変換するツールです。

## 概要

このプロジェクトは、ヤマレコで記録したGPXファイルをRunkeeper互換フォーマットに変換し、複数日にわたるアクティビティデータを正確に変換することを目的としています。

## 機能

- ヤマレコのGPXファイルをRunkeeper互換フォーマットに変換
- 複数日にわたるアクティビティデータの正確な変換
- メタデータセクションの追加
- アクティビティタイプの明示的な指定
- XMLフォーマットの構造化オプション
- 拡張されたコマンドラインオプション

## デモ

Renderでホストされたデモアプリケーションを試すことができます：
[TrailSync Demo](https://trailsync-ziew.onrender.com)

## インストール

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
```

## 使用方法

### 基本的な変換

```bash
# 基本的な使用方法
python src/yamareco_to_runkeeper.py input.gpx -o output.gpx
```

### 改良版変換スクリプト

```bash
# 基本的な使用方法
python src/yamareco_to_runkeeper_improved.py input.gpx -o output.gpx

# 詳細なオプションを指定
python src/yamareco_to_runkeeper_improved.py input.gpx -o output.gpx \
  --activity-type hiking \
  --track-name "京都一周トレイル2泊3日" \
  --format-xml \
  --coordinate-precision 6 \
  --elevation-adjustment 5.2 \
  --add-metadata \
  --keep-source
```

### 利用可能なオプション

| オプション | 説明 | デフォルト値 |
|------------|------|--------------|
| `--activity-type` | アクティビティタイプ | hiking |
| `--track-name` | トラック名 | 日時から自動生成 |
| `--format-xml` | XMLを整形する（インデントを追加） | False |
| `--coordinate-precision` | 座標精度（小数点以下の桁数） | 6 |
| `--elevation-adjustment` | 標高調整値（メートル単位） | 5.2 |
| `--add-metadata` | メタデータセクションを追加する | True |
| `--no-metadata` | メタデータセクションを追加しない | - |
| `--keep-source` | 元のサービス情報を保持する | True |
| `--no-source` | 元のサービス情報を保持しない | - |

### Renderへのデプロイ

このリポジトリはRenderへの直接デプロイに対応しています。

1. [Render](https://render.com/)にアカウントを作成
2. 「New Web Service」をクリック
3. このリポジトリのURLを入力
4. 以下の設定を行う：
   - Name: trailsync（または任意の名前）
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:server`
5. 「Create Web Service」をクリック

## プロジェクト構成

```
trailsync/
├── docs/               # ドキュメント
│   └── design.md       # 設計書
├── src/                # ソースコード
│   ├── yamareco_to_runkeeper.py        # 基本変換スクリプト
│   └── yamareco_to_runkeeper_improved.py # 改良版変換スクリプト
├── tests/              # テストコード
│   ├── test_improved_converter.py # 改良版スクリプトのテスト
│   └── test_data/      # テスト用データ
│       ├── yamareco.gpx      # ヤマレコのGPXファイル
│       ├── strava.gpx        # Stravaのエクスポートファイル
│       └── runkeeper.gpx     # Runkeeperのエクスポートファイル
├── app.py              # Dashアプリケーション
├── Procfile            # Renderデプロイ用
├── render.yaml         # Render設定ファイル
├── venv/               # 仮想環境（gitignoreに追加）
├── requirements.txt    # 依存関係
└── requirements-dev.txt # 開発用依存関係
```

## 開発

### 開発環境のセットアップ

```bash
# 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Linuxの場合
# venv\Scripts\activate  # Windowsの場合

# 開発用依存パッケージのインストール
pip install -r requirements-dev.txt
```

### テストの実行

```bash
pytest
```

### コードスタイルのチェック

```bash
ruff check .
```

## サポート

このプロジェクトが役立つと思われる場合は、以下の方法でサポートしていただけると嬉しいです：

<a href="https://www.buymeacoffee.com/mump0nd" target="_blank">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" >
</a>

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 貢献

バグ報告や機能リクエストは、GitHubのIssueで受け付けています。プルリクエストも歓迎します。

---

© 2025 HōkaLabs. All rights reserved.