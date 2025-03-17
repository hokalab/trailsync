# GPXファイル形式の比較分析と統一フォーマット設計書

## 1. 概要

このドキュメントでは、様々なアクティビティログサービス（Runkeeper、ヤマレコ、Strava等）のGPXファイル形式を比較分析し、統一データフォーマットの設計と実装アプローチを提案します。

## 2. 目的

異なるサービス間でアクティビティログを簡単に変換・共有できるウェブサービスの基盤を構築するため、最適な統一GPXフォーマットを設計することを目的としています。

## 3. 各サービスのGPXファイル形式の比較

### 3.1 基本構造の比較

| 特徴 | Runkeeper | ヤマレコ | Strava |
|------|-----------|----------|--------|
| XML宣言 | あり | あり | あり |
| 名前空間 | 複数定義 | 基本のみ | 基本のみ |
| メタデータ要素 | なし | なし | あり |
| トラック名形式 | CDATA | プレーンテキスト | Unicodeエスケープ |
| トラックタイプ | なし | なし | あり |
| トラック番号 | なし | あり | なし |
| トラック時間 | あり | なし | なし |

### 3.2 データ精度の比較

| データ項目 | Runkeeper | ヤマレコ | Strava |
|------------|-----------|----------|--------|
| 緯度・経度精度 | 小数点以下9桁 | 小数点以下14桁 | 小数点以下7桁 |
| 標高精度 | 小数点以下1桁 | 整数値 | 小数点以下1桁 |
| 時間形式 | ISO 8601 (Z) | ISO 8601 (Z) | ISO 8601 (Z) |

### 3.3 拡張機能の比較

| 拡張機能 | Runkeeper | ヤマレコ | Strava |
|----------|-----------|----------|--------|
| Garmin拡張 | 定義あり、未使用 | なし | なし |
| その他拡張 | なし | なし | なし |

## 4. 既存の変換スクリプトの分析

### 4.1 universal_gpx_converter.py
- 様々なGPXファイルを解析し、統一フォーマットに変換
- 名前空間の違いを吸収
- CDATAセクションの処理
- 時間情報の標準化
- 拡張データ（Garmin等）の処理
- 統一フォーマットでのGPXファイル作成

### 4.2 convert_yamareco_to_strava.py
- ヤマレコ形式のGPXファイルをStrava形式に変換
- トラックポイントを時間順にソート
- Strava形式のGPXファイルを作成

### 4.3 analyze_gpx_files.py
- GPXファイルを解析して情報を抽出・表示
- 日付情報を分析
- GPXデータのサマリーを表示

## 5. 統一フォーマットの設計

### 5.1 基本構造

```xml
<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1"
     creator="Universal GPX Converter"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xmlns="http://www.topografix.com/GPX/1/1"
     xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd"
     xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1">
  <metadata>
    <name>アクティビティ名</name>
    <desc>アクティビティの説明</desc>
    <time>2025-01-30T23:32:36Z</time>
    <keywords>キーワード（カンマ区切り）</keywords>
    <author>
      <name>作成者名</name>
    </author>
    <link href="関連URL">
      <text>リンクテキスト</text>
    </link>
    <extensions>
      <source_info>
        <original_service>元のサービス名</original_service>
        <conversion_date>変換日時</conversion_date>
      </source_info>
    </extensions>
  </metadata>
  <trk>
    <name>トラック名</name>
    <type>アクティビティタイプ</type>
    <desc>トラックの説明</desc>
    <number>1</number>
    <extensions>
      <service_data>
        <yamareco:mountain_area>山域情報</yamareco:mountain_area>
        <yamareco:weather>天候情報</yamareco:weather>
        <strava:gear_id>使用機材ID</strava:gear_id>
        <runkeeper:calories>消費カロリー</runkeeper:calories>
      </service_data>
    </extensions>
    <trkseg>
      <trkpt lat="34.932940000" lon="135.765692000">
        <ele>35.2</ele>
        <time>2025-01-30T23:32:36Z</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>心拍数</gpxtpx:hr>
            <gpxtpx:cad>ケイデンス</gpxtpx:cad>
            <gpxtpx:temp>気温</gpxtpx:temp>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>
      <!-- 以下トラックポイント続く -->
    </trkseg>
  </trk>
</gpx>
```

### 5.2 設計の特徴

1. **基本構造**:
   - GPX 1.1規格に完全準拠
   - 必要な名前空間をすべて定義
   - メタデータセクションを含む（Stravaスタイル）
   - 拡張データに対応

2. **メタデータ**:
   - アクティビティ名、説明、時間、作成者情報を格納
   - 元のサービス情報を拡張データとして保持

3. **トラック情報**:
   - トラック名、タイプ（Stravaスタイル）
   - トラック番号（ヤマレコスタイル）
   - サービス固有データを拡張セクションに格納

4. **トラックポイント**:
   - 緯度・経度は小数点以下9桁（Runkeeperスタイル、十分な精度）
   - 標高は小数点以下1桁（Runkeeper/Stravaスタイル）
   - 時間はISO 8601形式（Z）
   - 拡張データ（心拍数、ケイデンス等）に対応

5. **拡張機能**:
   - Garmin拡張に対応
   - サービス固有の拡張データを保持できる構造

## 6. 実装アプローチ

### 6.1 コアモジュール設計

#### 6.1.1 GPXパーサー
- 各サービスのGPXファイルを解析するモジュール
- 名前空間の違いを吸収
- 様々なフォーマットのデータを統一的に扱う

#### 6.1.2 フォーマットコンバーター
- 統一フォーマットへの変換を行うモジュール
- 各サービス固有のデータを適切に変換

#### 6.1.3 サービス固有モジュール
- Runkeeper用モジュール
- ヤマレコ用モジュール
- Strava用モジュール
- 各サービス固有の処理を実装

### 6.2 拡張機能

#### 6.2.1 メタデータ拡張
- 元のサービス情報を保持
- 変換履歴を記録

#### 6.2.2 サービス固有データ拡張
- 各サービス固有のデータを保持
- 相互変換時のデータ損失を最小化

#### 6.2.3 トラックポイント拡張
- 心拍数、ケイデンス、気温等の拡張データに対応
- サービス固有の拡張データを保持

### 6.3 ウェブサービス設計

#### 6.3.1 APIレイヤー
- RESTful API設計
- OAuth認証

#### 6.3.2 フロントエンド
- ユーザーフレンドリーなUI
- ファイルアップロード機能
- 変換設定のカスタマイズ

#### 6.3.3 バックエンド処理
- 非同期処理
- キャッシュ機能
- エラーハンドリング

## 7. 開発ロードマップ

### 7.1 フェーズ1: コア機能の開発
- 統一GPXフォーマットの実装
- 基本的な変換機能の実装
- コマンドラインインターフェースの実装

### 7.2 フェーズ2: 拡張機能の開発
- サービス固有データの保持機能
- 拡張データの対応
- バッチ処理機能

### 7.3 フェーズ3: ウェブサービスの開発
- APIの実装
- フロントエンドの実装
- ユーザー認証機能

### 7.4 フェーズ4: サービス連携の拡張
- 他のサービスへの対応
- APIを使用した直接連携
- 自動同期機能

## 8. 結論

3つのサービス（Runkeeper、ヤマレコ、Strava）のGPXファイル形式を比較分析した結果、それぞれに独自の特徴がありますが、GPX 1.1規格をベースにした統一フォーマットで相互変換が可能です。

提案した統一フォーマットは、各サービスの長所を取り入れつつ、拡張性と互換性を確保しています。このフォーマットを中心に据えることで、様々なアクティビティログをサービス間でシームレスに変換できるウェブサービスの構築が可能になります。