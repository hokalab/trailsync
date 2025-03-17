# TrailSync

様々なアクティビティログサービス（ヤマレコ、Strava、Runkeeper等）のGPXファイルを統一フォーマットに変換し、相互運用性を高めるツールです。

## 概要

このプロジェクトは、異なるサービス間でアクティビティログを簡単に変換・共有できるようにすることを目的としています。将来的には、様々なアクティビティログをサービス間でコンバートするウェブサービスの基盤となることを目指しています。

## 機能

- 様々なサービス（ヤマレコ、Strava、Runkeeper等）のGPXファイルを解析
- 統一フォーマットへの変換
- サービス固有のデータを保持
- 拡張データ（心拍数、ケイデンス等）に対応
- コマンドラインインターフェース
- Streamlitによるウェブインターフェース

## デモ

Streamlit Community Cloudでホストされたデモアプリケーションを試すことができます：
[TrailSync Demo](https://trailsync.streamlit.app/)

## インストール

```bash
# リポジトリをクローン
git clone https://github.com/HokaLabs/trailsync.git
cd trailsync

# 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Linuxの場合
# venv\Scripts\activate  # Windowsの場合

# 依存パッケージのインストール
pip install -r requirements.txt
```

## 使用方法

### Streamlitアプリケーション

```bash
# Streamlitアプリケーションを実行
./run_app.sh

# または手動で実行
source venv/bin/activate
streamlit run app.py
```

ブラウザで http://localhost:8501 を開き、ウェブインターフェースを使用します。

1. GPXファイルをアップロード
2. サービスを自動検出または選択
3. 変換オプションを設定
4. 変換結果をダウンロード

### コマンドライン

```bash
# 基本的な使用方法
python -m trailsync.main input.gpx -o output.gpx

# トラック名とアクティビティタイプを指定
python -m trailsync.main input.gpx -o output.gpx -n "山行記録" -t "hiking"

# GPXファイルの分析
python -m trailsync.main input.gpx --analyze
```

### オプション

- `-o, --output`: 出力ファイル名（指定しない場合は入力ファイル名_converted.gpx）
- `-n, --name`: トラック名（指定しない場合は元のファイルから推測または自動生成）
- `-t, --type`: アクティビティタイプ（hiking, running, cycling等、デフォルト: hiking）
- `-a, --analyze`: GPXファイルの分析情報を表示

## プロジェクト構成

```
trailsync/
├── docs/               # ドキュメント
│   └── design.md       # 設計書
├── src/                # ソースコード
│   └── trailsync/      # メインパッケージ
│       ├── __init__.py
│       ├── main.py     # メインモジュール
│       ├── parser.py   # GPXパーサー
│       ├── converter.py # フォーマットコンバーター
│       └── services/   # サービス固有モジュール
│           ├── __init__.py
│           ├── runkeeper.py
│           ├── yamareco.py
│           └── strava.py
├── tests/              # テストコード
│   ├── test_parser.py  # テストファイル
│   └── test_data/      # テスト用データ
├── app.py              # Streamlitアプリケーション
├── run_app.sh          # アプリケーション実行スクリプト
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

## デプロイ

### Streamlit Community Cloud

このアプリケーションは、Streamlit Community Cloudを使用して簡単にデプロイできます：

1. GitHubにリポジトリをプッシュします
2. [Streamlit Community Cloud](https://streamlit.io/cloud)にアクセスし、GitHubアカウントでログインします
3. 「New app」をクリックし、リポジトリを選択します
4. メインファイルとして「app.py」を指定します
5. 「Deploy」をクリックします

変更をGitHubにプッシュするたびに、アプリケーションは自動的に更新されます。

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