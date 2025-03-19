# TrailSync v1.1.0 リリースノート

## 概要

TrailSync v1.1.0では、ヤマレコからランキーパーへの変換機能が大幅に改善されました。特に、複数日にわたるアクティビティデータの正確な変換が可能になり、Stravaを経由せずに直接変換できるようになりました。

このリリースは、GPXファイル変換分析に基づく改善の第一弾であり、コア機能の強化に焦点を当てています。今後のリリースでは、ウェブアプリケーションの強化、ドキュメントとテストの強化、リリースと評価を予定しています。

## 主な新機能

### 1. メタデータセクションの追加

Stravaスタイルのメタデータセクションを追加し、アクティビティの基本情報を明確化しました。

```xml
<metadata>
  <time>2025-01-30T23:32:36Z</time>
  <name>京都一周トレイル2泊3日</name>
  <extensions>
    <source_info>
      <original_service>Yamareco</original_service>
      <conversion_date>2025-03-19T16:40:00.123456</conversion_date>
    </source_info>
  </extensions>
</metadata>
```

### 2. アクティビティタイプの明示的な指定

ハイキング、ランニング、サイクリングなど、アクティビティタイプを明示的に指定できるようになりました。

```xml
<trk>
  <type>hiking</type>
  <name><![CDATA[Hiking 31/1/25 8:32 am]]></name>
  <time>2025-01-30T23:32:36Z</time>
  <trkseg>
    ...
  </trkseg>
</trk>
```

コマンドラインからアクティビティタイプを指定できます：

```bash
python src/yamareco_to_runkeeper_improved.py input.gpx --activity-type hiking
```

### 3. XMLフォーマットの構造化オプション

可読性向上のためのXML整形機能を追加しました。整形オプションを有効にすると、インデントが追加され、可読性が向上します。

整形前：
```xml
<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="TrailSync - Runkeeper Converter" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.topografix.com/GPX/1/1" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd"><metadata><time>2025-01-30T23:32:36Z</time><extensions><source_info><original_service>Yamareco</original_service><conversion_date>2025-03-19T16:40:00.123456</conversion_date></source_info></extensions></metadata><trk><type>hiking</type><name><![CDATA[Hiking 31/1/25 8:32 am]]></name><time>2025-01-30T23:32:36Z</time><trkseg><trkpt lat="34.932940" lon="135.765692"><ele>35.2</ele><time>2025-01-30T23:32:36Z</time></trkpt>...</trkseg></trk></gpx>
```

整形後：
```xml
<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="TrailSync - Runkeeper Converter" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.topografix.com/GPX/1/1" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
  <metadata>
    <time>2025-01-30T23:32:36Z</time>
    <extensions>
      <source_info>
        <original_service>Yamareco</original_service>
        <conversion_date>2025-03-19T16:40:00.123456</conversion_date>
      </source_info>
    </extensions>
  </metadata>
  <trk>
    <type>hiking</type>
    <name><![CDATA[Hiking 31/1/25 8:32 am]]></name>
    <time>2025-01-30T23:32:36Z</time>
    <trkseg>
      <trkpt lat="34.932940" lon="135.765692">
        <ele>35.2</ele>
        <time>2025-01-30T23:32:36Z</time>
      </trkpt>
      ...
    </trkseg>
  </trk>
</gpx>
```

コマンドラインから整形オプションを指定できます：

```bash
python src/yamareco_to_runkeeper_improved.py input.gpx --format-xml
```

### 4. 拡張されたコマンドラインオプション

より柔軟な変換設定が可能になりました。主なオプションは以下の通りです：

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

## 改善点

### 1. 座標精度の最適化

座標精度を調整可能になりました（デフォルト: 6桁）。これにより、ファイルサイズが削減され、処理効率が向上します。

```bash
python src/yamareco_to_runkeeper_improved.py input.gpx --coordinate-precision 9
```

### 2. 標高データの精緻化

標高データの調整値を設定可能になりました（デフォルト: +5.2m）。これにより、ランキーパーの標高基準に合わせた調整が可能になります。

```bash
python src/yamareco_to_runkeeper_improved.py input.gpx --elevation-adjustment 4.5
```

### 3. ドキュメントの充実

詳細な使用方法と技術的な説明を追加しました。主なドキュメントは以下の通りです：

- [GPXファイル変換分析レポート](docs/gpx_conversion_analysis.md)
- [実装改善提案書](docs/implementation_proposal.md)
- [改良版スクリプトのREADME](docs/improved_converter_readme.md)

## バグ修正

### 複数日アクティビティの変換問題を解決

ヤマレコからランキーパーへの直接変換で複数日のアクティビティが正しく認識されるように修正しました。これにより、Stravaを経由せずに直接変換できるようになりました。

主な修正点：
- メタデータセクションの追加
- アクティビティタイプの明示的な指定
- 日付情報の適切な保持

## インストール方法

### 1. リポジトリのクローン

```bash
git clone https://github.com/mump0nd/trailsync.git
cd trailsync
```

### 2. 依存関係のインストール

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本的な使用方法

```bash
python src/yamareco_to_runkeeper_improved.py input.gpx -o output.gpx
```

### 詳細なオプションを指定

```bash
python src/yamareco_to_runkeeper_improved.py input.gpx -o output.gpx \
  --activity-type hiking \
  --track-name "京都一周トレイル2泊3日" \
  --format-xml \
  --coordinate-precision 6 \
  --elevation-adjustment 5.2 \
  --add-metadata \
  --keep-source
```

詳細な使用方法については、[改良版スクリプトのREADME](docs/improved_converter_readme.md)を参照してください。

## ウェブアプリケーションでの使用

TrailSyncウェブアプリケーションでは、以下の手順で改良版変換機能を使用できます：

1. ヤマレコGPXファイルをアップロード
2. サービスとして「Yamareco」を選択
3. アクティビティタイプを選択
4. トラック名を入力（オプション）
5. XMLフォーマットオプションを選択
6. 「統一フォーマットに変換」ボタンをクリック
7. 変換結果をダウンロード

## 既知の問題

- 非常に大きなGPXファイル（10MB以上）の変換時にメモリ使用量が増加する可能性があります
- 一部の古いバージョンのランキーパーアプリでは、拡張データが正しく表示されない場合があります

## 今後の予定

このリリースはフェーズ1（コア機能の強化）に相当します。今後のフェーズでは、以下の改善を予定しています：

- フェーズ2: ウェブアプリケーションの強化（2週間）
  - 変換オプションの拡張
  - 変換プレビュー機能の実装
  - バッチ変換機能の実装

- フェーズ3: ドキュメントとテストの強化（1週間）
  - サービス別変換ガイドの作成
  - トラブルシューティングガイドの作成
  - 総合テストの実施

- フェーズ4: リリースと評価（1週間）
  - ベータ版のリリース
  - ユーザーフィードバックの収集
  - 最終調整とリリース

## フィードバック

バグ報告や機能リクエストは、GitHubのIssueトラッカーで受け付けています：
https://github.com/mump0nd/trailsync/issues

## 謝辞

このリリースは、GPXファイル変換分析に基づいて実装されました。分析に協力してくださったユーザーの皆様に感謝いたします。

## ライセンス

TrailSyncはMITライセンスの下で公開されています。詳細については、[LICENSE](LICENSE)ファイルを参照してください。