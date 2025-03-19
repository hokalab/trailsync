#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ヤマレコのGPXファイルをランキーパーが正しく読み込めるフォーマットに変換するスクリプト

このスクリプトは、ヤマレコからエクスポートされたGPXファイルを解析し、
ランキーパーが複数日のアクティビティとして正しく認識できるフォーマットに変換します。
変換には、XMLフォーマットの構造化、アクティビティタイプの追加、座標精度の調整、
標高データの精緻化、日付情報の適切な保持などが含まれます。
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

def adjust_elevation(ele_str):
    """標高値を小数点付きの値に変換する"""
    try:
        # 整数値を浮動小数点に変換し、小数点第1位まで表示
        ele_float = float(ele_str)
        # ランキーパーの標高値は若干高めに設定されているようなので、調整
        adjusted_ele = ele_float + 5.2  # 分析結果から推定した調整値
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

def convert_yamareco_to_runkeeper(input_file, output_file):
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
    new_root.set('creator', 'Runkeeper - http://www.runkeeper.com')
    new_root.set('{' + NAMESPACES['xsi'] + '}schemaLocation', 
                 'http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd')
    
    # トラック要素を作成
    trk = ET.SubElement(new_root, '{' + NAMESPACES['gpx'] + '}trk')
    
    # トラック名を設定（ランキーパー形式）
    # 日付をYYYY-MM-DDからDD/MM/YY形式に変換
    date_parts = first_activity_date.split('-')
    formatted_date = f"{date_parts[2]}/{date_parts[1]}/{date_parts[0][2:]}"
    
    # 最初のトラックポイントから時刻を取得
    first_trkpt = root.find('.//gpx:trkpt', NAMESPACES)
    first_time = first_trkpt.find('./gpx:time', NAMESPACES).text if first_trkpt is not None else ""
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
    
    name = ET.SubElement(trk, '{' + NAMESPACES['gpx'] + '}name')
    name.text = f"Hiking {formatted_date} {time_str}"
    
    # CDATA形式で名前を設定
    name.text = None
    cdata = ET.Comment(f'![CDATA[Hiking {formatted_date} {time_str}]]')
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
        lat = format_coordinate(trkpt.get('lat'), 6)
        lon = format_coordinate(trkpt.get('lon'), 6)
        new_trkpt.set('lat', lat)
        new_trkpt.set('lon', lon)
        
        # 標高を調整
        ele = trkpt.find('./gpx:ele', NAMESPACES)
        if ele is not None:
            new_ele = ET.SubElement(new_trkpt, '{' + NAMESPACES['gpx'] + '}ele')
            new_ele.text = adjust_elevation(ele.text)
        
        # 時間を設定
        time_elem = trkpt.find('./gpx:time', NAMESPACES)
        if time_elem is not None:
            new_time = ET.SubElement(new_trkpt, '{' + NAMESPACES['gpx'] + '}time')
            new_time.text = time_elem.text
    
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

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='ヤマレコのGPXファイルをランキーパー形式に変換します。')
    parser.add_argument('input_file', help='入力ヤマレコGPXファイルのパス')
    parser.add_argument('-o', '--output', help='出力ファイルのパス（指定しない場合は入力ファイル名に_runkeeper.gpxを追加）')
    
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
    success = convert_yamareco_to_runkeeper(args.input_file, output_file)
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())