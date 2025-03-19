# TrailSync プロジェクト統合計画

## 概要

GPXファイル変換分析と改良版スクリプトの開発が完了したため、これらの成果をTrailSyncプロジェクトに正式に統合するための計画を提案します。この計画では、コードレビュー、テスト、ドキュメント更新、リリースの各段階について詳細に説明します。

## 1. プルリクエスト（PR）の準備

### 1.1 ブランチ戦略

```bash
# 開発ブランチを作成
git checkout -b feature/improved-yamareco-converter

# 変更をステージング
git add docs/gpx_conversion_analysis.md
git add docs/implementation_proposal.md
git add docs/improved_converter_readme.md
git add src/yamareco_to_runkeeper_improved.py
git add tests/test_improved_converter.py

# コミット
git commit -m "[feat] ヤマレコ→ランキーパー変換機能の改善

- GPXファイル変換分析に基づく改良版スクリプトの実装
- メタデータセクションの追加
- アクティビティタイプの明示的な指定
- XMLフォーマットの構造化オプション
- 拡張されたコマンドラインオプション
- テストスクリプトの追加"

# リモートにプッシュ
git push origin feature/improved-yamareco-converter
```

### 1.2 PRの作成

GitHub UIまたは`gh` CLIを使用してPRを作成：

```bash
gh pr create --title "ヤマレコ→ランキーパー変換機能の改善" \
  --body "# 概要

GPXファイル変換分析に基づき、ヤマレコからランキーパーへの直接変換機能を改善しました。特に、複数日にわたるアクティビティデータの正確な変換が可能になります。

## 主な変更点

- メタデータセクションの追加
- アクティビティタイプの明示的な指定
- XMLフォーマットの構造化オプション
- 拡張されたコマンドラインオプション
- テストスクリプトの追加

## テスト結果

テストスクリプトを実行し、元のスクリプトと改良版スクリプトの変換結果を比較しました。改良版スクリプトは元のスクリプトの基本機能を維持しつつ、重要な改善点が正しく実装されていることを確認しました。

## 関連ドキュメント

- [GPXファイル変換分析レポート](docs/gpx_conversion_analysis.md)
- [実装改善提案書](docs/implementation_proposal.md)
- [改良版スクリプトのREADME](docs/improved_converter_readme.md)

## 今後の展開

このPRはフェーズ1（コア機能の強化）に相当します。今後のフェーズでは、ウェブアプリケーションの強化、ドキュメントとテストの強化、リリースと評価を予定しています。"
```

## 2. コードレビュー

### 2.1 レビュー観点

以下の観点でコードレビューを依頼します：

1. **機能性**
   - 複数日アクティビティの正しい変換
   - メタデータセクションの追加
   - アクティビティタイプの指定
   - XMLフォーマットの整形

2. **コード品質**
   - コーディング規約への準拠
   - エラーハンドリング
   - パフォーマンス
   - セキュリティ

3. **テスト品質**
   - テストカバレッジ
   - エッジケースの考慮
   - テスト結果の検証

4. **ドキュメント品質**
   - 使用方法の明確さ
   - 改善点の説明
   - 技術的な詳細の正確さ

### 2.2 レビュー後の対応

レビューコメントに基づいて必要な修正を行い、再レビューを依頼します。

## 3. 統合テスト

### 3.1 テスト環境の準備

```bash
# テスト用ディレクトリの作成
mkdir -p tests/integration_tests

# テストデータの準備
cp tests/test_data/yamareco.gpx tests/integration_tests/
```

### 3.2 統合テストの実行

```bash
# 統合テストスクリプトの実行
python tests/integration_tests/run_integration_tests.py
```

### 3.3 テスト結果の検証

- 変換結果のGPXファイルをRunkeeperにインポート
- 複数日のアクティビティが正しく認識されることを確認
- 標高データ、座標データが正しく変換されていることを確認

## 4. ドキュメント更新

### 4.1 READMEの更新

プロジェクトのメインREADMEに改良版スクリプトについての情報を追加：

```markdown
## ヤマレコ→ランキーパー変換

TrailSyncは、ヤマレコからエクスポートされたGPXファイルをランキーパーが正しく読み込めるフォーマットに変換する機能を提供しています。特に、複数日にわたるアクティビティデータの正確な変換に対応しています。

### コマンドラインツール

```bash
# 基本的な使用方法
python src/yamareco_to_runkeeper_improved.py input.gpx -o output.gpx

# 詳細なオプション
python src/yamareco_to_runkeeper_improved.py input.gpx -o output.gpx \
  --activity-type hiking \
  --track-name "京都一周トレイル2泊3日" \
  --format-xml
```

詳細な使用方法については、[改良版スクリプトのREADME](docs/improved_converter_readme.md)を参照してください。
```

### 4.2 ウェブアプリケーションのヘルプページ更新

ウェブアプリケーションのヘルプページに改良版スクリプトについての情報を追加：

```html
<div class="help-section">
  <h3>ヤマレコ→ランキーパー変換</h3>
  <p>
    TrailSyncは、ヤマレコからエクスポートされたGPXファイルをランキーパーが正しく読み込めるフォーマットに変換する機能を提供しています。特に、複数日にわたるアクティビティデータの正確な変換に対応しています。
  </p>
  <h4>主な機能</h4>
  <ul>
    <li>メタデータセクションの追加</li>
    <li>アクティビティタイプの明示的な指定</li>
    <li>XMLフォーマットの構造化オプション</li>
    <li>座標精度と標高データの最適化</li>
  </ul>
</div>
```

## 5. ウェブアプリケーションへの統合

### 5.1 変換オプションの追加

app.pyに変換オプションを追加：

```python
dbc.Row([
    dbc.Col([
        html.Label("XMLフォーマット"),
        dcc.RadioItems(
            id='xml-format-radio',
            options=[
                {'label': '圧縮（サイズ優先）', 'value': 'compact'},
                {'label': '整形（可読性優先）', 'value': 'formatted'}
            ],
            value='formatted',
            labelStyle={'display': 'block'}
        ),
    ], width=6),
    dbc.Col([
        html.Label("メタデータ"),
        dcc.Checklist(
            id='metadata-checklist',
            options=[
                {'label': 'メタデータセクションを追加', 'value': 'add_metadata'},
                {'label': '元のサービス情報を保持', 'value': 'keep_source'}
            ],
            value=['add_metadata', 'keep_source']
        ),
    ], width=6)
]),
```

### 5.2 変換ロジックの更新

GPXConverterクラスを更新して改良版スクリプトの機能を統合：

```python
def convert_yamareco_to_runkeeper(self, gpx_data, output_file, options):
    """ヤマレコのGPXデータをランキーパー形式に変換する"""
    # 改良版スクリプトの変換ロジックを統合
    # ...
```

## 6. リリース準備

### 6.1 バージョン番号の更新

```python
# src/trailsync/__init__.py
__version__ = '1.1.0'  # 機能追加のためマイナーバージョンアップ
```

### 6.2 CHANGELOGの更新

```markdown
# Changelog

## [1.1.0] - 2025-03-20

### 追加
- ヤマレコ→ランキーパー変換機能の改善
  - メタデータセクションの追加
  - アクティビティタイプの明示的な指定
  - XMLフォーマットの構造化オプション
  - 拡張されたコマンドラインオプション
- テストスクリプトの追加

### 変更
- 座標精度と標高データの最適化
- ドキュメントの更新

### 修正
- 複数日アクティビティの変換問題を解決
```

### 6.3 リリースノートの作成

```markdown
# TrailSync v1.1.0 リリースノート

TrailSync v1.1.0では、ヤマレコからランキーパーへの変換機能が大幅に改善されました。特に、複数日にわたるアクティビティデータの正確な変換が可能になり、Stravaを経由せずに直接変換できるようになりました。

## 主な新機能

- **メタデータセクションの追加**: Stravaスタイルのメタデータセクションを追加し、アクティビティの基本情報を明確化
- **アクティビティタイプの明示的な指定**: ハイキング、ランニング、サイクリングなど、アクティビティタイプを明示的に指定可能
- **XMLフォーマットの構造化オプション**: 可読性向上のためのXML整形機能を追加
- **拡張されたコマンドラインオプション**: より柔軟な変換設定が可能に

## 改善点

- **座標精度の最適化**: 座標精度を調整可能に（デフォルト: 6桁）
- **標高データの精緻化**: 標高データの調整値を設定可能に（デフォルト: +5.2m）
- **ドキュメントの充実**: 詳細な使用方法と技術的な説明を追加

## バグ修正

- **複数日アクティビティの変換問題を解決**: ヤマレコからランキーパーへの直接変換で複数日のアクティビティが正しく認識されるように修正

## インストール方法

```bash
git clone https://github.com/mump0nd/trailsync.git
cd trailsync
pip install -r requirements.txt
```

## 使用方法

```bash
python src/yamareco_to_runkeeper_improved.py input.gpx -o output.gpx
```

詳細な使用方法については、[改良版スクリプトのREADME](docs/improved_converter_readme.md)を参照してください。
```

## 7. リリース

### 7.1 マージ

PRがレビューされ、承認されたら、developブランチにマージします：

```bash
git checkout develop
git merge feature/improved-yamareco-converter
git push origin develop
```

### 7.2 リリースブランチの作成

```bash
git checkout -b release/v1.1.0
git push origin release/v1.1.0
```

### 7.3 最終テスト

リリースブランチで最終テストを実施し、問題がなければmainブランチにマージします：

```bash
git checkout main
git merge release/v1.1.0
git tag -a v1.1.0 -m "TrailSync v1.1.0"
git push origin main --tags
```

### 7.4 リリースの公開

GitHubのリリースページでリリースを公開し、リリースノートを添付します。

## 8. 展開

### 8.1 Renderへのデプロイ

```bash
# Renderへの自動デプロイが設定されている場合、
# mainブランチへのプッシュで自動的にデプロイされます
```

### 8.2 デプロイ後の確認

- ウェブアプリケーションが正常に動作することを確認
- 変換機能が正しく動作することを確認
- エラーログを確認

## 9. 今後の展開

### 9.1 フィードバックの収集

- ユーザーからのフィードバックを収集
- バグ報告や機能リクエストを追跡

### 9.2 次のフェーズの計画

- フェーズ2: ウェブアプリケーションの強化
- フェーズ3: ドキュメントとテストの強化
- フェーズ4: リリースと評価

## 10. 結論

GPXファイル変換分析に基づく改良版スクリプトの統合により、TrailSyncプロジェクトは以下の利点を得ることができます：

1. **サービス間の互換性向上**: 特に複数日にわたるアクティビティデータの正確な変換
2. **ユーザーエクスペリエンスの向上**: より柔軟な変換オプションとバッチ処理機能
3. **データ品質の向上**: 適切なデータ精度と標準化されたXML構造
4. **拡張性の向上**: 新しいサービスへの対応が容易になる設計

これらの改善により、TrailSyncは様々なアクティビティログサービス間のデータ変換における信頼性の高いツールとなり、アウトドア愛好家の活動記録管理をより効率的にサポートすることができます。