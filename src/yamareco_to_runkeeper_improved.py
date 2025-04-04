#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ヤマレコのGPXファイルをランキーパーが正しく読み込めるフォーマットに変換する改良版スクリプト

このスクリプトは、ヤマレコからエクスポートされたGPXファイルを解析し、
ランキーパーが複数日のアクティビティとして正しく認識できるフォーマットに変換します。
変換には、XMLフォーマットの構造化、アクティビティタイプの追加、座標精度の調整、
標高データの精緻化、日付情報の適切な保持などが含まれます。

改良版の主な機能：
- アクティビティタイプの明示的な指定
- メタデータセクションの追加
- XMLフォーマットの構造化オプション
- 拡張されたコマンドラインオプション
"""

import argparse
import xml.etree.ElementTree as ET
import os
import re
import datetime
from decimal import Decimal, ROUND_HALF_UP

# 名前空間の定義
NAMESPACES = {
    'gpx': 'http://www.topografix.com/GPX/1/1',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'gpxtpx': 'http://www.garmin.com/xmlschemas/TrackPointExtension/v1'
}

# アクティビティタイプの定義
ACTIVITY_TYPES = ['hiking', 'running', 'cycling', 'walking', 'swimming', 'other']

def register_namespaces():
    """XMLの名前空間を登録する"""
    for prefix, uri in NAMESPACES.items():
        ET.register_namespace(prefix, uri)
    # デフォルト名前空間の登録（接頭辞なし）
    ET.register_namespace('', NAMESPACES['gpx'])

def parse_gpx(file_path):
    """GPXファイルを解析してElementTreeオブジェクトを返す"""
    try:
        tree = ET.parse(file_path)
        return tree
    except Exception as e:
        print(f"GPXファイルの解析中にエラーが発生しました: {e}")
        return None

def format_coordinate(coord_str, precision=6):
    """座標値を指定された精度に調整する"""
    try:
        # 文字列を10進数に変換
        decimal_value = Decimal(coord_str)
        # 指定された精度に丸める
        formatted_value = decimal_value.quantize(Decimal('0.' + '0' * precision), rounding=ROUND_HALF_UP)
        # 文字列に戻す
        return f"{formatted_value:.{precision}f}"
    except Exception as e:
        print(f"座標値の変換中にエラーが発生しました: {e}")
        return coord_str

def adjust_elevation(ele_str, adjustment=5.2):
    """標高値を小数点付きの値に変換する"""
    try:
        # 整数値を浮動小数点に変換し、小数点第1位まで表示
        ele_float = float(ele_str)
        # ランキーパーの標高値は若干高めに設定されているようなので、調整
        adjusted_ele = ele_float + adjustment  # 分析結果から推定した調整値
        return f"{adjusted_ele:.1f}"
    except Exception as e:
        print(f"標高値の変換中にエラーが発生しました: {e}")
        return ele_str

def extract_activity_dates(tree):
    """GPXファイルから活動日を抽出する"""
    dates = set()
    root = tree.getroot()
    
    # 名前空間を考慮してトラックポイントを検索
    for trkpt in root.findall('.//gpx:trkpt', NAMESPACES):
        time_elem = trkpt.find('./gpx:time', NAMESPACES)
        if time_elem is not None and time_elem.text:
            # 日付部分（YYYY-MM-DD）を抽出
            date_match = re.match(r'(\d{4}-\d{2}-\d{2})', time_elem.text)
            if date_match:
                dates.add(date_match.group(1))
    
    return sorted(list(dates))

def format_xml(element, level=0):
    """XMLを整形する（インデントを追加）"""
    i = "\n" + level * " "
    if len(element):
        if not element.text or not element.text.strip():
            element.text = i + "  "
        if not element.tail or not element.tail.strip():
            element.tail = i
        for elem in element:
            format_xml(elem, level + 2)
        if not element.tail or not element.tail.strip():
            element.tail = i
    else:
        if level and (not element.tail or not element.tail.strip()):
            element.tail = i

def convert_yamareco_to_runkeeper(input_file, output_file, options):
    """ヤマレコのGPXファイルをランキーパー形式に変換する"""
    # 名前空間を登録
    register_namespaces()
    
    # GPXファイルを解析
    tree = parse_gpx(input_file)
    if tree is None:
        return False
    
    root = tree.getroot()
    
    # 活動日を抽出
    activity_dates = extract_activity_dates(tree)
    if not activity_dates:
        print("GPXファイルから活動日を抽出できませんでした。")
        return False
    
    # 最初の活動日を取得
    first_activity_date = activity_dates[0]
    
    # 新しいGPXルート要素を作成
    new_root = ET.Element('{' + NAMESPACES['gpx'] + '}gpx')
    new_root.set('version', '1.1')
    new_root.set('creator', 'TrailSync - Runkeeper Converter')
    new_root.set('{' + NAMESPACES['xsi'] + '}schemaLocation', 
                 'http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd')
    
    # 最初のトラックポイントから時刻を取得
    first_trkpt = root.find('.//gpx:trkpt', NAMESPACES)
    first_time = first_trkpt.find('./gpx:time', NAMESPACES).text if first_trkpt is not None else ""
    
    # メタデータセクションを追加（Stravaスタイル）
    if options.add_metadata:
        metadata = ET.SubElement(new_root, '{' + NAMESPACES['gpx'] + '}metadata')
        meta_time = ET.SubElement(metadata, '{' + NAMESPACES['gpx'] + '}time')
        meta_time.text = first_time
        
        # アクティビティ名をメタデータに追加
        if options.track_name:
            meta_name = ET.SubElement(metadata, '{' + NAMESPACES['gpx'] + '}name')
            meta_name.text = options.track_name
        
        # 元のサービス情報を追加
        if options.keep_source:
            extensions = ET.SubElement(metadata, '{' + NAMESPACES['gpx'] + '}extensions')
            source_info = ET.SubElement(extensions, 'source_info')
            original_service = ET.SubElement(source_info, 'original_service')
            original_service.text = "Yamareco"
            conversion_date = ET.SubElement(source_info, 'conversion_date')
            conversion_date.text = datetime.datetime.now().isoformat()
    
    # トラック要素を作成
    trk = ET.SubElement(new_root, '{' + NAMESPACES['gpx'] + '}trk')
    
    # アクティビティタイプを追加（Stravaスタイル）
    if options.activity_type:
        type_elem = ET.SubElement(trk, '{' + NAMESPACES['gpx'] + '}type')
        type_elem.text = options.activity_type
    
    # トラック名を設定
    name = ET.SubElement(trk, '{' + NAMESPACES['gpx'] + '}name')
    
    if options.track_name:
        track_name = options.track_name
    else:
        # 日付をYYYY-MM-DDからDD/MM/YY形式に変換
        date_parts = first_activity_date.split('-')
        formatted_date = f"{date_parts[2]}/{date_parts[1]}/{date_parts[0][2:]}"
        
        # 時刻を取得
        time_match = re.search(r'T(\d{2}):(\d{2}):\d{2}Z', first_time)
        time_str = ""
        if time_match:
            hour = int(time_match.group(1))
            minute = time_match.group(2)
            am_pm = "am" if hour < 12 else "pm"
            hour = hour % 12
            if hour == 0:
                hour = 12
            time_str = f"{hour}:{minute} {am_pm}"
        
        track_name = f"{options.activity_type.capitalize()} {formatted_date} {time_str}"
    
    # CDATA形式で名前を設定
    name.text = None
    cdata = ET.Comment(f'![CDATA[{track_name}]]')
    name.append(cdata)
    
    # 時間要素を追加
    time_elem = ET.SubElement(trk, '{' + NAMESPACES['gpx'] + '}time')
    time_elem.text = first_time
    
    # トラックセグメントを作成
    trkseg = ET.SubElement(trk, '{' + NAMESPACES['gpx'] + '}trkseg')
    
    # 元のトラックポイントを処理
    for trkpt in root.findall('.//gpx:trkpt', NAMESPACES):
        # 新しいトラックポイントを作成
        new_trkpt = ET.SubElement(trkseg, '{' + NAMESPACES['gpx'] + '}trkpt')
        
        # 座標を調整して設定
        lat = format_coordinate(trkpt.get('lat'), options.coordinate_precision)
        lon = format_coordinate(trkpt.get('lon'), options.coordinate_precision)
        new_trkpt.set('lat', lat)
        new_trkpt.set('lon', lon)
        
        # 標高を調整
        ele = trkpt.find('./gpx:ele', NAMESPACES)
        if ele is not None:
            new_ele = ET.SubElement(new_trkpt, '{' + NAMESPACES['gpx'] + '}ele')
            new_ele.text = adjust_elevation(ele.text, options.elevation_adjustment)
        
        # 時間を設定
        time_elem = trkpt.find('./gpx:time', NAMESPACES)
        if time_elem is not None:
            new_time = ET.SubElement(new_trkpt, '{' + NAMESPACES['gpx'] + '}time')
            new_time.text = time_elem.text
    
    # XMLを整形する
    if options.format_xml:
        format_xml(new_root)
    
    # XMLツリーを文字列に変換
    xml_str = ET.tostring(new_root, encoding='utf-8').decode('utf-8')
    
    # XML宣言を追加
    xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str
    
    # CDATAセクションを正しく修正（ElementTreeはCDATAを適切に処理できない）
    xml_str = xml_str.replace('&lt;!--![CDATA[', '<![CDATA[')
    xml_str = xml_str.replace(']]--&gt;', ']]>')
    
    # 出力ファイルに保存
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xml_str)
        print(f"変換が完了しました。出力ファイル: {output_file}")
        return True
    except Exception as e:
        print(f"ファイルの保存中にエラーが発生しました: {e}")
        return False

# app.pyで使用するための関数エイリアス
def convert_gpx(input_file, output_file, **options):
    """
    app.pyで使用するための関数エイリアス
    convert_yamareco_to_runkeeperのラッパー関数
    """
    # オプションをargparseの名前空間オブジェクトに変換
    class Options:
        pass
    
    args = Options()
    for key, value in options.items():
        setattr(args, key, value)
    
    # デフォルト値の設定
    if not hasattr(args, 'activity_type'):
        args.activity_type = 'hiking'
    if not hasattr(args, 'format_xml'):
        args.format_xml = True
    if not hasattr(args, 'coordinate_precision'):
        args.coordinate_precision = 6
    if not hasattr(args, 'elevation_adjustment'):
        args.elevation_adjustment = 5.2
    if not hasattr(args, 'add_metadata'):
        args.add_metadata = True
    if not hasattr(args, 'keep_source'):
        args.keep_source = True
    if not hasattr(args, 'track_name'):
        args.track_name = None
    
    return convert_yamareco_to_runkeeper(input_file, output_file, args)

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='ヤマレコのGPXファイルをランキーパー形式に変換します。')
    parser.add_argument('input_file', help='入力ヤマレコGPXファイルのパス')
    parser.add_argument('-o', '--output', help='出力ファイルのパス（指定しない場合は入力ファイル名に_runkeeper.gpxを追加）')
    parser.add_argument('--activity-type', choices=ACTIVITY_TYPES, default='hiking', 
                        help='アクティビティタイプ（デフォルト: hiking）')
    parser.add_argument('--track-name', help='トラック名（指定しない場合は日時から自動生成）')
    parser.add_argument('--format-xml', action='store_true', help='XMLを整形する（インデントを追加）')
    parser.add_argument('--coordinate-precision', type=int, default=6, 
                        help='座標精度（小数点以下の桁数、デフォルト: 6）')
    parser.add_argument('--elevation-adjustment', type=float, default=5.2, 
                        help='標高調整値（メートル単位、デフォルト: 5.2）')
    parser.add_argument('--add-metadata', action='store_true', default=True, 
                        help='メタデータセクションを追加する')
    parser.add_argument('--no-metadata', action='store_false', dest='add_metadata', 
                        help='メタデータセクションを追加しない')
    parser.add_argument('--keep-source', action='store_true', default=True, 
                        help='元のサービス情報を保持する')
    parser.add_argument('--no-source', action='store_false', dest='keep_source', 
                        help='元のサービス情報を保持しない')
    
    args = parser.parse_args()
    
    # 入力ファイルの存在確認
    if not os.path.exists(args.input_file):
        print(f"エラー: 入力ファイル '{args.input_file}' が見つかりません。")
        return 1
    
    # 出力ファイル名の設定
    if args.output:
        output_file = args.output
    else:
        base_name, ext = os.path.splitext(args.input_file)
        output_file = f"{base_name}_runkeeper{ext}"
    
    # 変換実行
    success = convert_yamareco_to_runkeeper(args.input_file, output_file, args)
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())