#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal GPX Converter

このスクリプトは、様々なサービス（ヤマレコ、Strava、Runkeeper等）からダウンロードした
GPXファイルを、最も互換性の高い統一フォーマットに変換します。

使用方法:
    python universal_gpx_converter.py input.gpx -o output.gpx -n "アクティビティ名" -t "アクティビティタイプ"

オプション:
    -o, --output: 出力ファイル名（指定しない場合は入力ファイル名_converted.gpx）
    -n, --name: トラック名（指定しない場合は元のファイルから推測または自動生成）
    -t, --type: アクティビティタイプ（hiking, running, cycling等、デフォルト: hiking）
"""

import argparse
import os
import sys
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from xml.dom import minidom
import logging

# ロギング設定
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# XML名前空間
NAMESPACES = {
    'gpx': 'http://www.topografix.com/GPX/1/1',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'gpxtpx': 'http://www.garmin.com/xmlschemas/TrackPointExtension/v1'
}

def register_namespaces():
    """XMLの名前空間を登録"""
    for prefix, uri in NAMESPACES.items():
        ET.register_namespace(prefix, uri)
    # デフォルト名前空間
    ET.register_namespace('', 'http://www.topografix.com/GPX/1/1')

def parse_gpx_file(file_path):
    """GPXファイルを解析し、トラックポイントとメタデータを抽出"""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # 名前空間を取得（ファイルによって異なる場合がある）
        ns = {'gpx': root.tag.split('}')[0].strip('{')} if '}' in root.tag else NAMESPACES['gpx']
        
        # ファイル情報
        creator = root.get('creator', 'Unknown')
        
        # メタデータ
        metadata = {}
        metadata_elem = root.find('.//{{{0}}}metadata'.format(ns['gpx']))
        if metadata_elem is not None:
            time_elem = metadata_elem.find('.//{{{0}}}time'.format(ns['gpx']))
            if time_elem is not None:
                metadata['time'] = time_elem.text
        
        # 全トラックとポイントを抽出
        tracks = []
        for trk in root.findall('.//{{{0}}}trk'.format(ns['gpx'])):
            track = {'points': []}
            
            # トラック名
            name_elem = trk.find('.//{{{0}}}name'.format(ns['gpx']))
            if name_elem is not None:
                # CDATAセクションを処理
                if name_elem.text and ']]>' in name_elem.text:
                    track['name'] = name_elem.text.replace('<![CDATA[', '').replace(']]>', '')
                else:
                    track['name'] = name_elem.text
            
            # トラックタイプ
            type_elem = trk.find('.//{{{0}}}type'.format(ns['gpx']))
            if type_elem is not None:
                track['type'] = type_elem.text
            
            # トラック時間（Runkeeper形式）
            time_elem = trk.find('.//{{{0}}}time'.format(ns['gpx']))
            if time_elem is not None:
                track['time'] = time_elem.text
            
            # トラックセグメントとポイント
            for trkseg in trk.findall('.//{{{0}}}trkseg'.format(ns['gpx'])):
                for trkpt in trkseg.findall('.//{{{0}}}trkpt'.format(ns['gpx'])):
                    point = {
                        'lat': trkpt.get('lat'),
                        'lon': trkpt.get('lon'),
                        'ele': None,
                        'time': None,
                        'extensions': {}
                    }
                    
                    ele_elem = trkpt.find('.//{{{0}}}ele'.format(ns['gpx']))
                    if ele_elem is not None:
                        point['ele'] = ele_elem.text
                    
                    time_elem = trkpt.find('.//{{{0}}}time'.format(ns['gpx']))
                    if time_elem is not None:
                        point['time'] = time_elem.text
                        # 時間情報をdatetimeオブジェクトに変換（ソート用）
                        try:
                            point['datetime'] = datetime.fromisoformat(time_elem.text.replace('Z', '+00:00'))
                        except ValueError:
                            point['datetime'] = datetime.min
                    
                    # 拡張データ（Garmin等）
                    extensions_elem = trkpt.find('.//{{{0}}}extensions'.format(ns['gpx']))
                    if extensions_elem is not None:
                        for ext in extensions_elem:
                            tag = ext.tag.split('}')[-1]
                            point['extensions'][tag] = ext.text
                    
                    track['points'].append(point)
            
            tracks.append(track)
        
        # 最初と最後の時間を取得
        all_points = []
        for track in tracks:
            all_points.extend(track['points'])
        
        all_points.sort(key=lambda x: x.get('datetime', datetime.min))
        
        if all_points:
            first_point = all_points[0]
            last_point = all_points[-1]
            
            if 'time' in first_point and 'time' in last_point:
                start_time = first_point['time']
                end_time = last_point['time']
                
                if 'time' not in metadata:
                    metadata['time'] = start_time
            
        return {
            'creator': creator,
            'metadata': metadata,
            'tracks': tracks,
            'all_points': all_points
        }
    
    except Exception as e:
        logger.error(f"ファイル '{file_path}' の解析中にエラーが発生しました: {e}")
        return None

def create_universal_gpx(gpx_data, output_file, track_name=None, activity_type=None):
    """統一フォーマットのGPXファイルを作成"""
    if not gpx_data or not gpx_data.get('all_points'):
        logger.error("変換するデータがありません")
        return False
    
    register_namespaces()
    
    # ルート要素の作成
    root = ET.Element('{http://www.topografix.com/GPX/1/1}gpx')
    root.set('version', '1.1')
    root.set('creator', 'Universal GPX Converter')
    root.set('{http://www.w3.org/2001/XMLSchema-instance}schemaLocation', 
             'http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd')
    
    # 名前空間の追加
    root.set('xmlns:gpxtpx', 'http://www.garmin.com/xmlschemas/TrackPointExtension/v1')
    
    # メタデータの追加
    metadata = ET.SubElement(root, '{http://www.topografix.com/GPX/1/1}metadata')
    
    # 開始時間をメタデータに追加
    if gpx_data['metadata'].get('time'):
        time_elem = ET.SubElement(metadata, '{http://www.topografix.com/GPX/1/1}time')
        time_elem.text = gpx_data['metadata']['time']
    elif gpx_data['all_points'] and gpx_data['all_points'][0].get('time'):
        time_elem = ET.SubElement(metadata, '{http://www.topografix.com/GPX/1/1}time')
        time_elem.text = gpx_data['all_points'][0]['time']
    
    # トラックの作成
    trk = ET.SubElement(root, '{http://www.topografix.com/GPX/1/1}trk')
    
    # トラック名の設定
    name = ET.SubElement(trk, '{http://www.topografix.com/GPX/1/1}name')
    if track_name:
        name.text = track_name
    else:
        # 既存のトラック名から推測
        existing_names = [t.get('name') for t in gpx_data['tracks'] if t.get('name')]
        if existing_names and existing_names[0] != 'track':
            name.text = existing_names[0]
        else:
            # 日付から自動生成
            first_point = gpx_data['all_points'][0]
            last_point = gpx_data['all_points'][-1]
            
            if 'time' in first_point and 'time' in last_point:
                try:
                    start_date = datetime.fromisoformat(first_point['time'].replace('Z', '+00:00'))
                    end_date = datetime.fromisoformat(last_point['time'].replace('Z', '+00:00'))
                    days = (end_date.date() - start_date.date()).days
                    
                    if days > 0:
                        name.text = f"アクティビティ {start_date.strftime('%Y-%m-%d')} から {days+1}日間"
                    else:
                        name.text = f"アクティビティ {start_date.strftime('%Y-%m-%d')}"
                except ValueError:
                    name.text = "変換されたアクティビティ"
            else:
                name.text = "変換されたアクティビティ"
    
    # アクティビティタイプの設定
    if activity_type:
        type_elem = ET.SubElement(trk, '{http://www.topografix.com/GPX/1/1}type')
        type_elem.text = activity_type
    else:
        # 既存のタイプから推測
        existing_types = [t.get('type') for t in gpx_data['tracks'] if t.get('type')]
        if existing_types:
            type_elem = ET.SubElement(trk, '{http://www.topografix.com/GPX/1/1}type')
            type_elem.text = existing_types[0]
        else:
            # デフォルトはハイキング
            type_elem = ET.SubElement(trk, '{http://www.topografix.com/GPX/1/1}type')
            type_elem.text = 'hiking'
    
    # 開始時間をトラックにも追加（Runkeeper形式）
    if gpx_data['all_points'] and gpx_data['all_points'][0].get('time'):
        time_elem = ET.SubElement(trk, '{http://www.topografix.com/GPX/1/1}time')
        time_elem.text = gpx_data['all_points'][0]['time']
    
    # トラックセグメントの作成
    trkseg = ET.SubElement(trk, '{http://www.topografix.com/GPX/1/1}trkseg')
    
    # トラックポイントの追加（時間順）
    for point in gpx_data['all_points']:
        trkpt = ET.SubElement(trkseg, '{http://www.topografix.com/GPX/1/1}trkpt')
        trkpt.set('lat', point['lat'])
        trkpt.set('lon', point['lon'])
        
        if point['ele']:
            ele = ET.SubElement(trkpt, '{http://www.topografix.com/GPX/1/1}ele')
            ele.text = point['ele']
        
        if point['time']:
            time_elem = ET.SubElement(trkpt, '{http://www.topografix.com/GPX/1/1}time')
            time_elem.text = point['time']
        
        # 拡張データがあれば追加
        if point['extensions']:
            extensions = ET.SubElement(trkpt, '{http://www.topografix.com/GPX/1/1}extensions')
            for key, value in point['extensions'].items():
                ext_elem = ET.SubElement(extensions, '{http://www.garmin.com/xmlschemas/TrackPointExtension/v1}' + key)
                ext_elem.text = value
    
    # XMLを整形して保存
    xml_str = ET.tostring(root, encoding='utf-8')
    pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")
    
    # XML宣言を修正（エンコーディングをUTF-8に）
    pretty_xml = pretty_xml.replace('<?xml version="1.0" ?>', '<?xml version="1.0" encoding="UTF-8"?>')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)
    
    return True

def analyze_gpx(gpx_data):
    """GPXデータの分析情報を表示"""
    if not gpx_data:
        return
    
    logger.info("GPXファイル分析:")
    logger.info(f"  作成者: {gpx_data['creator']}")
    
    if gpx_data['metadata']:
        logger.info("  メタデータ:")
        for key, value in gpx_data['metadata'].items():
            logger.info(f"    {key}: {value}")
    
    logger.info(f"  トラック数: {len(gpx_data['tracks'])}")
    
    for i, track in enumerate(gpx_data['tracks'], 1):
        logger.info(f"  トラック {i}:")
        if 'name' in track:
            logger.info(f"    名前: {track['name']}")
        if 'type' in track:
            logger.info(f"    タイプ: {track['type']}")
        logger.info(f"    ポイント数: {len(track['points'])}")
    
    # 日付分析
    if gpx_data['all_points']:
        dates = {}
        min_date = None
        max_date = None
        
        for point in gpx_data['all_points']:
            if 'datetime' in point:
                dt = point['datetime']
                date_str = dt.strftime('%Y-%m-%d')
                dates[date_str] = dates.get(date_str, 0) + 1
                
                if min_date is None or dt < min_date:
                    min_date = dt
                if max_date is None or dt > max_date:
                    max_date = dt
        
        if min_date and max_date:
            logger.info("  日付分析:")
            logger.info(f"    開始日時: {min_date.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"    終了日時: {max_date.strftime('%Y-%m-%d %H:%M:%S')}")
            
            days = (max_date.date() - min_date.date()).days
            logger.info(f"    期間: {days}日")
            
            logger.info(f"    ユニークな日付: {len(dates)}")
            logger.info("    日付ごとのポイント数:")
            for date, count in sorted(dates.items()):
                logger.info(f"      {date}: {count}ポイント")

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='様々なサービスのGPXファイルを統一フォーマットに変換します')
    parser.add_argument('input_file', help='入力GPXファイル')
    parser.add_argument('-o', '--output', help='出力ファイル名（指定しない場合は入力ファイル名_converted.gpx）')
    parser.add_argument('-n', '--name', help='トラック名（指定しない場合は元のファイルから推測または自動生成）')
    parser.add_argument('-t', '--type', help='アクティビティタイプ（hiking, running, cycling等、デフォルト: 元のファイルから推測またはhiking）')
    parser.add_argument('-a', '--analyze', action='store_true', help='GPXファイルの分析情報を表示')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        logger.error(f"ファイル '{args.input_file}' が見つかりません")
        return 1
    
    # 出力ファイル名の決定
    if args.output:
        output_file = args.output
    else:
        base_name, ext = os.path.splitext(args.input_file)
        output_file = f"{base_name}_converted{ext}"
    
    logger.info(f"GPXファイル '{args.input_file}' を解析中...")
    gpx_data = parse_gpx_file(args.input_file)
    
    if not gpx_data:
        logger.error("変換に失敗しました")
        return 1
    
    # 分析情報の表示
    if args.analyze:
        analyze_gpx(gpx_data)
    
    logger.info(f"統一フォーマットのGPXファイルを作成中...")
    if create_universal_gpx(gpx_data, output_file, args.name, args.type):
        logger.info(f"変換完了: '{output_file}' が作成されました")
        
        # 統計情報の表示
        points_count = len(gpx_data['all_points'])
        
        logger.info(f"\n統計情報:")
        logger.info(f"  ポイント数: {points_count}")
        
        if gpx_data['all_points']:
            first_point = gpx_data['all_points'][0]
            last_point = gpx_data['all_points'][-1]
            
            if 'time' in first_point and 'time' in last_point:
                try:
                    start_time = datetime.fromisoformat(first_point['time'].replace('Z', '+00:00'))
                    end_time = datetime.fromisoformat(last_point['time'].replace('Z', '+00:00'))
                    duration = end_time - start_time
                    
                    logger.info(f"  開始時間: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    logger.info(f"  終了時間: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    logger.info(f"  期間: {duration.days}日 {duration.seconds//3600}時間 {(duration.seconds//60)%60}分")
                except ValueError:
                    pass
        
        return 0
    else:
        logger.error("変換に失敗しました")
        return 1

if __name__ == "__main__":
    sys.exit(main())