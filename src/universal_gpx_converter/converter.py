#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GPXコンバーターモジュール

このモジュールは、解析されたGPXデータを統一フォーマットに変換する機能を提供します。
"""

import xml.etree.ElementTree as ET
from datetime import datetime
import logging
from typing import Dict, List, Any, Optional
from xml.dom import minidom

# ロギング設定
logger = logging.getLogger(__name__)

# XML名前空間
NAMESPACES = {
    'gpx': 'http://www.topografix.com/GPX/1/1',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'gpxtpx': 'http://www.garmin.com/xmlschemas/TrackPointExtension/v1',
    'yamareco': 'http://www.yamareco.com/xmlschemas/YamarecoExtension/v1',
    'strava': 'http://www.strava.com/xmlschemas/StravaExtension/v1',
    'runkeeper': 'http://www.runkeeper.com/xmlschemas/RunkeeperExtension/v1'
}

class GPXConverter:
    """GPXデータを統一フォーマットに変換するクラス"""

    def __init__(self):
        """初期化"""
        self.namespaces = NAMESPACES

    def register_namespaces(self):
        """XMLの名前空間を登録"""
        for prefix, uri in self.namespaces.items():
            ET.register_namespace(prefix, uri)
        # デフォルト名前空間
        ET.register_namespace('', 'http://www.topografix.com/GPX/1/1')

    def convert_to_universal_format(self, gpx_data: Dict[str, Any], output_file: str, 
                                   track_name: Optional[str] = None, 
                                   activity_type: Optional[str] = None) -> bool:
        """GPXデータを統一フォーマットに変換

        Args:
            gpx_data: 変換するGPXデータ
            output_file: 出力ファイルパス
            track_name: トラック名（指定しない場合は元のデータから推測）
            activity_type: アクティビティタイプ（指定しない場合は元のデータから推測）

        Returns:
            bool: 変換が成功したかどうか
        """
        if not gpx_data or not gpx_data.get('all_points'):
            logger.error("変換するデータがありません")
            return False
        
        self.register_namespaces()
        
        # ルート要素の作成
        root = ET.Element('{http://www.topografix.com/GPX/1/1}gpx')
        root.set('version', '1.1')
        root.set('creator', 'Universal GPX Converter')
        root.set('{http://www.w3.org/2001/XMLSchema-instance}schemaLocation', 
                'http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd')
        
        # 名前空間の追加
        for prefix, uri in self.namespaces.items():
            if prefix != 'gpx' and prefix != 'xsi':
                root.set(f'xmlns:{prefix}', uri)
        
        # メタデータの追加
        metadata = self._create_metadata_element(gpx_data)
        root.append(metadata)
        
        # トラックの作成
        trk = self._create_track_element(gpx_data, track_name, activity_type)
        root.append(trk)
        
        # XMLを整形して保存
        xml_str = ET.tostring(root, encoding='utf-8')
        pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")
        
        # XML宣言を修正（エンコーディングをUTF-8に）
        pretty_xml = pretty_xml.replace('<?xml version="1.0" ?>', '<?xml version="1.0" encoding="UTF-8"?>')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
        
        return True

    def _create_metadata_element(self, gpx_data: Dict[str, Any]) -> ET.Element:
        """メタデータ要素を作成

        Args:
            gpx_data: GPXデータ

        Returns:
            ET.Element: メタデータ要素
        """
        metadata = ET.Element('{http://www.topografix.com/GPX/1/1}metadata')
        
        # 名前
        if gpx_data['metadata'].get('name'):
            name_elem = ET.SubElement(metadata, '{http://www.topografix.com/GPX/1/1}name')
            name_elem.text = gpx_data['metadata']['name']
        
        # 説明
        if gpx_data['metadata'].get('desc'):
            desc_elem = ET.SubElement(metadata, '{http://www.topografix.com/GPX/1/1}desc')
            desc_elem.text = gpx_data['metadata']['desc']
        
        # 時間
        if gpx_data['metadata'].get('time'):
            time_elem = ET.SubElement(metadata, '{http://www.topografix.com/GPX/1/1}time')
            time_elem.text = gpx_data['metadata']['time']
        elif gpx_data['all_points'] and gpx_data['all_points'][0].get('time'):
            time_elem = ET.SubElement(metadata, '{http://www.topografix.com/GPX/1/1}time')
            time_elem.text = gpx_data['all_points'][0]['time']
        
        # キーワード
        if gpx_data['metadata'].get('keywords'):
            keywords_elem = ET.SubElement(metadata, '{http://www.topografix.com/GPX/1/1}keywords')
            keywords_elem.text = gpx_data['metadata']['keywords']
        
        # 作成者
        if gpx_data['metadata'].get('author'):
            author_elem = ET.SubElement(metadata, '{http://www.topografix.com/GPX/1/1}author')
            author_name_elem = ET.SubElement(author_elem, '{http://www.topografix.com/GPX/1/1}name')
            author_name_elem.text = gpx_data['metadata']['author']
        
        # リンク
        if gpx_data['metadata'].get('link'):
            link_elem = ET.SubElement(metadata, '{http://www.topografix.com/GPX/1/1}link')
            link_elem.set('href', gpx_data['metadata']['link'])
            
            if gpx_data['metadata'].get('link_text'):
                link_text_elem = ET.SubElement(link_elem, '{http://www.topografix.com/GPX/1/1}text')
                link_text_elem.text = gpx_data['metadata']['link_text']
        
        # 拡張データ
        extensions = ET.SubElement(metadata, '{http://www.topografix.com/GPX/1/1}extensions')
        source_info = ET.SubElement(extensions, 'source_info')
        
        # 元のサービス
        original_service = ET.SubElement(source_info, 'original_service')
        original_service.text = gpx_data.get('service', 'unknown')
        
        # 変換日時
        conversion_date = ET.SubElement(source_info, 'conversion_date')
        conversion_date.text = datetime.now().isoformat()
        
        return metadata

    def _create_track_element(self, gpx_data: Dict[str, Any], 
                             track_name: Optional[str], 
                             activity_type: Optional[str]) -> ET.Element:
        """トラック要素を作成

        Args:
            gpx_data: GPXデータ
            track_name: トラック名
            activity_type: アクティビティタイプ

        Returns:
            ET.Element: トラック要素
        """
        trk = ET.Element('{http://www.topografix.com/GPX/1/1}trk')
        
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
        
        # トラック番号
        existing_numbers = [t.get('number') for t in gpx_data['tracks'] if t.get('number')]
        if existing_numbers:
            number_elem = ET.SubElement(trk, '{http://www.topografix.com/GPX/1/1}number')
            number_elem.text = existing_numbers[0]
        
        # トラック説明
        existing_descs = [t.get('desc') for t in gpx_data['tracks'] if t.get('desc')]
        if existing_descs:
            desc_elem = ET.SubElement(trk, '{http://www.topografix.com/GPX/1/1}desc')
            desc_elem.text = existing_descs[0]
        
        # 開始時間をトラックにも追加（Runkeeper形式）
        if gpx_data['all_points'] and gpx_data['all_points'][0].get('time'):
            time_elem = ET.SubElement(trk, '{http://www.topografix.com/GPX/1/1}time')
            time_elem.text = gpx_data['all_points'][0]['time']
        
        # サービス固有の拡張データがあれば追加
        service_extensions = self._extract_service_extensions(gpx_data)
        if service_extensions:
            extensions = ET.SubElement(trk, '{http://www.topografix.com/GPX/1/1}extensions')
            service_data = ET.SubElement(extensions, 'service_data')
            
            for key, value in service_extensions.items():
                if ':' in key:
                    # 名前空間付きの要素
                    ns_prefix, local_name = key.split(':')
                    ext_elem = ET.SubElement(service_data, f'{{{self.namespaces[ns_prefix]}}}{local_name}')
                else:
                    # 名前空間なしの要素
                    ext_elem = ET.SubElement(service_data, key)
                ext_elem.text = value
        
        # トラックセグメントの作成
        trkseg = ET.SubElement(trk, '{http://www.topografix.com/GPX/1/1}trkseg')
        
        # トラックポイントの追加（時間順）
        for point in gpx_data['all_points']:
            trkpt = self._create_trackpoint_element(point)
            trkseg.append(trkpt)
        
        return trk

    def _create_trackpoint_element(self, point: Dict[str, Any]) -> ET.Element:
        """トラックポイント要素を作成

        Args:
            point: トラックポイントデータ

        Returns:
            ET.Element: トラックポイント要素
        """
        trkpt = ET.Element('{http://www.topografix.com/GPX/1/1}trkpt')
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
            
            # Garmin拡張データ
            garmin_ext = {}
            for key, value in point['extensions'].items():
                if key in ['hr', 'cad', 'temp', 'atemp']:
                    garmin_ext[key] = value
            
            if garmin_ext:
                tpx = ET.SubElement(extensions, '{http://www.garmin.com/xmlschemas/TrackPointExtension/v1}TrackPointExtension')
                
                for key, value in garmin_ext.items():
                    if key == 'hr':
                        hr_elem = ET.SubElement(tpx, '{http://www.garmin.com/xmlschemas/TrackPointExtension/v1}hr')
                        hr_elem.text = value
                    elif key == 'cad':
                        cad_elem = ET.SubElement(tpx, '{http://www.garmin.com/xmlschemas/TrackPointExtension/v1}cad')
                        cad_elem.text = value
                    elif key == 'temp' or key == 'atemp':
                        temp_elem = ET.SubElement(tpx, '{http://www.garmin.com/xmlschemas/TrackPointExtension/v1}temp')
                        temp_elem.text = value
            
            # その他の拡張データ
            for key, value in point['extensions'].items():
                if key not in ['hr', 'cad', 'temp', 'atemp']:
                    ext_elem = ET.SubElement(extensions, key)
                    ext_elem.text = value
        
        return trkpt

    def _extract_service_extensions(self, gpx_data: Dict[str, Any]) -> Dict[str, str]:
        """サービス固有の拡張データを抽出

        Args:
            gpx_data: GPXデータ

        Returns:
            Dict[str, str]: サービス固有の拡張データ
        """
        extensions = {}
        
        # サービスを検出
        service = gpx_data.get('service', 'unknown')
        
        if service == 'yamareco':
            # ヤマレコ固有のデータを抽出
            for track in gpx_data['tracks']:
                if track.get('name') and track.get('name') != 'track':
                    extensions['yamareco:mountain_name'] = track.get('name')
        
        elif service == 'strava':
            # Strava固有のデータを抽出
            for track in gpx_data['tracks']:
                if track.get('type'):
                    extensions['strava:activity_type'] = track.get('type')
        
        elif service == 'runkeeper':
            # Runkeeper固有のデータを抽出
            for track in gpx_data['tracks']:
                if track.get('name'):
                    # CDATAセクションを処理
                    name = track.get('name')
                    if name and '<![CDATA[' in name:
                        name = name.replace('<![CDATA[', '').replace(']]>', '')
                    extensions['runkeeper:activity_name'] = name
        
        return extensions