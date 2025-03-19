# Changelog

すべての重要な変更はこのファイルに記録されます。

フォーマットは[Keep a Changelog](https://keepachangelog.com/ja/1.0.0/)に基づいており、
このプロジェクトは[Semantic Versioning](https://semver.org/spec/v2.0.0.html)に準拠しています。

## [1.1.0] - 2025-03-20

### 追加
- ヤマレコ→ランキーパー変換機能の改善
  - メタデータセクションの追加
  - アクティビティタイプの明示的な指定
  - XMLフォーマットの構造化オプション
  - 拡張されたコマンドラインオプション
- 新規ファイル
  - src/yamareco_to_runkeeper_improved.py: 改良版変換スクリプト
  - docs/gpx_conversion_analysis.md: GPXファイル変換分析レポート
  - docs/implementation_proposal.md: 実装改善提案書
  - docs/improved_converter_readme.md: 改良版スクリプトのREADME
  - tests/test_improved_converter.py: テストスクリプト
  - docs/integration_plan.md: プロジェクト統合計画
  - docs/release_notes_v1.1.0.md: リリースノート

### 変更
- 座標精度と標高データの最適化
  - 座標精度を調整可能に（デフォルト: 6桁）
  - 標高データの調整値を設定可能に（デフォルト: +5.2m）
- ドキュメントの更新
  - 詳細な使用方法と技術的な説明を追加
  - 変換オプションの説明を追加

### 修正
- 複数日アクティビティの変換問題を解決
  - ヤマレコからランキーパーへの直接変換で複数日のアクティビティが正しく認識されるように修正
  - Stravaを経由せずに直接変換できるように改善

## [1.0.0] - 2025-01-15

### 追加
- 初期リリース
- 基本的なGPX変換機能
  - ヤマレコ→ランキーパー変換
  - Strava→ヤマレコ変換
  - ランキーパー→Strava変換
- ウェブアプリケーションインターフェース
  - ファイルアップロード機能
  - 変換設定のカスタマイズ
  - 変換結果のダウンロード
- コマンドラインインターフェース
  - 基本的な変換コマンド
  - 出力ファイル名の指定