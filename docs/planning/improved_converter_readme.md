# 改良版ヤマレコ→ランキーパー変換スクリプト

## 概要

このドキュメントでは、GPXファイル変換分析に基づいて改良された `yamareco_to_runkeeper_improved.py` スクリプトの使用方法と改善点について説明します。

改良版スクリプトは、ヤマレコからエクスポートされたGPXファイルをランキーパーが複数日のアクティビティとして正しく認識できるフォーマットに変換します。特に、Stravaを経由せずに直接変換する際の互換性問題を解決することを目的としています。

## 主な改善点

元の `yamareco_to_runkeeper.py` スクリプトと比較して、以下の改善が実装されています：

1. **アクティビティタイプの明示的な指定**
   - Stravaスタイルの `<type>` タグを追加
   - コマンドラインから選択可能（hiking, running, cycling, walking, swimming, other）

2. **メタデータセクションの追加**
   - Stravaスタイルの `<metadata>` セクションを追加
   - 開始時間、アクティビティ名、元のサービス情報を含む

3. **XMLフォーマットの構造化オプション**
   - 可読性向上のためのXML整形機能
   - インデントの追加

4. **拡張されたコマンドラインオプション**
   - アクティビティタイプの選択
   - トラック名の指定
   - XMLフォーマットの整形
   - 座標精度の調整
   - 標高調整値の設定
   - メタデータセクションの追加/非追加
   - 元のサービス情報の保持/非保持

5. **データ精度の最適化**
   - 座標精度を調整可能（デフォルト: 6桁）
   - 標高データの調整値を設定可能（デフォルト: +5.2m）

## 使用方法

### 基本的な使用方法

```bash
python yamareco_to_runkeeper_improved.py input.gpx -o output.gpx
```

これにより、デフォルト設定（ハイキングアクティビティ、メタデータ追加、座標精度6桁、標高調整+5.2m）で変換が実行されます。

### 詳細なオプション

```bash
python yamareco_to_runkeeper_improved.py input.gpx -o output.gpx \
  --activity-type hiking \
  --track-name "京都一周トレイル2泊3日" \
  --format-xml \
  --coordinate-precision 6 \
  --elevation-adjustment 5.2 \
  --add-metadata \
  --keep-source
```

### オプションの説明

| オプション | 説明 | デフォルト値 |
|------------|------|--------------|
| `input_file` | 入力ヤマレコGPXファイルのパス | (必須) |
| `-o, --output` | 出力ファイルのパス | 入力ファイル名に_runkeeper.gpxを追加 |
| `--activity-type` | アクティビティタイプ | hiking |
| `--track-name` | トラック名 | 日時から自動生成 |
| `--format-xml` | XMLを整形する（インデントを追加） | False |
| `--coordinate-precision` | 座標精度（小数点以下の桁数） | 6 |
| `--elevation-adjustment` | 標高調整値（メートル単位） | 5.2 |
| `--add-metadata` | メタデータセクションを追加する | True |
| `--no-metadata` | メタデータセクションを追加しない | - |
| `--keep-source` | 元のサービス情報を保持する | True |
| `--no-source` | 元のサービス情報を保持しない | - |

## 使用例

### 1. 基本的な変換

```bash
python yamareco_to_runkeeper_improved.py yamareco.gpx
```

### 2. アクティビティタイプとトラック名を指定

```bash
python yamareco_to_runkeeper_improved.py yamareco.gpx \
  --activity-type hiking \
  --track-name "京都一周トレイル2泊3日"
```

### 3. XMLを整形して可読性を向上

```bash
python yamareco_to_runkeeper_improved.py yamareco.gpx \
  --format-xml
```

### 4. 座標精度と標高調整値をカスタマイズ

```bash
python yamareco_to_runkeeper_improved.py yamareco.gpx \
  --coordinate-precision 9 \
  --elevation-adjustment 4.5
```

### 5. メタデータを含めない最小限の変換

```bash
python yamareco_to_runkeeper_improved.py yamareco.gpx \
  --no-metadata \
  --no-source
```

## 変換結果の例

### 入力（ヤマレコ形式）

```xml
<?xml version="1.0" encoding="UTF-8"?>
<gpx xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.topografix.com/GPX/1/1" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd" creator="Yamareco iOS 7.22 - www.yamareco.com">
<trk><name>track</name><number>1</number><trkseg>
<trkpt lat="34.93293983529206" lon="135.76569236945932"><ele>30</ele><time>2025-01-30T23:32:36Z</time></trkpt>
<trkpt lat="34.933004458708005" lon="135.76616544961826"><ele>31</ele><time>2025-01-30T23:33:29Z</time></trkpt>
```

### 出力（ランキーパー形式、整形オプション有効）

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
      <trkpt lat="34.933004" lon="135.766165">
        <ele>36.2</ele>
        <time>2025-01-30T23:33:29Z</time>
      </trkpt>
    </trkseg>
  </trk>
</gpx>
```

## 技術的な詳細

### 複数日アクティビティの処理

スクリプトは、GPXファイル内のタイムスタンプを分析して複数日にわたるアクティビティを検出します。日付情報は変換後も保持され、ランキーパーが複数日のアクティビティとして正しく認識できるようになります。

### 座標精度の調整

ヤマレコの座標精度（14桁）は実用的な精度（デフォルト6桁）に調整されます。これにより、ファイルサイズが削減され、処理効率が向上します。

### 標高データの精緻化

ヤマレコの整数値の標高データは、小数点付きの値に変換され、ランキーパーの標高基準に合わせて調整されます（デフォルト+5.2m）。

## 今後の改善予定

1. **バッチ処理機能**
   - 複数のGPXファイルを一括変換する機能

2. **GUIインターフェース**
   - ウェブアプリケーションとの統合

3. **追加サービスのサポート**
   - Garmin Connect、Suunto、Polar等のサポート

4. **拡張データの保持**
   - 心拍数、ケイデンス、気温等の拡張データの保持

## 結論

改良版スクリプトは、GPXファイル変換分析で明らかになった知見を実装に反映し、ヤマレコからランキーパーへの直接変換における互換性問題を解決します。特に、複数日にわたるアクティビティデータの正確な変換が可能になり、Stravaを経由せずに直接変換できるようになります。