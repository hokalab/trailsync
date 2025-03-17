#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GPXパーサーモジュール

このモジュールは、様々なサービス（ヤマレコ、Strava、Runkeeper等）からダウンロードした
GPXファイルを解析し、統一的なデータ構造に変換する機能を提供します。
"""

import xml.etree.ElementTree as ET
from datetime import datetime
import logging
from typing import Dict, List, Any, Optional, Tuple

# ロギング設定
logger = logging.getLogger(__name__)

# XML名前空間
NAMESPACES = {
    'gpx': 'http://www.topografix.com/GPX/1/1',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'gpxtpx': 'http://www.garmin.com/xmlschemas/TrackPointExtension/v1'
}

class GPXParser:
    """GPXファイルを解析するクラス"""

    def __init__(self):
        """初期化"""
        self.namespaces = NAMESPACES

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """GPXファイルを解析し、トラックポイントとメタデータを抽出

        Args:
            file_path: GPXファイルのパス

        Returns:
            Dict[str, Any]: 解析結果を含む辞書
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # 名前空間を取得（ファイルによって異なる場合がある）
            ns = self._detect_namespaces(root)
            
            # ファイル情報
            creator = root.get('creator', 'Unknown')
            
            # メタデータ
            metadata = self._parse_metadata(root, ns)
            
            # 全トラックとポイントを抽出
            tracks = self._parse_tracks(root, ns)
            
            # 全ポイントを時間順にソート
            all_points = []
            for track in tracks:
                all_points.extend(track['points'])
            
            all_points.sort(key=lambda x: x.get('datetime', datetime.min))
            
            # 最初と最後の時間を取得
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

    def _detect_namespaces(self, root: ET.Element) -> Dict[str, str]:
        """XMLの名前空間を検出

        Args:
            root: XMLのルート要素

        Returns:
            Dict[str, str]: 検出された名前空間の辞書
        """
        ns = {}
        for key, value in self.namespaces.items():
            ns[key] = value
        
        # ルート要素から名前空間を検出
        if '}' in root.tag:
            default_ns = root.tag.split('}')[0].strip('{')
            ns['gpx'] = default_ns
        
        return ns

    def _parse_metadata(self, root: ET.Element, ns: Dict[str, str]) -> Dict[str, Any]:
        """メタデータを解析

        Args:
            root: XMLのルート要素
            ns: 名前空間の辞書

        Returns:
            Dict[str, Any]: メタデータの辞書
        """
        metadata = {}
        metadata_elem = root.find('.//{{{0}}}metadata'.format(ns['gpx']))
        
        if metadata_elem is not None:
            # 時間
            time_elem = metadata_elem.find('.//{{{0}}}time'.format(ns['gpx']))
            if time_elem is not None:
                metadata['time'] = time_elem.text
            
            # 名前
            name_elem = metadata_elem.find('.//{{{0}}}name'.format(ns['gpx']))
            if name_elem is not None:
                metadata['name'] = name_elem.text
            
            # 説明
            desc_elem = metadata_elem.find('.//{{{0}}}desc'.format(ns['gpx']))
            if desc_elem is not None:
                metadata['desc'] = desc_elem.text
            
            # キーワード
            keywords_elem = metadata_elem.find('.//{{{0}}}keywords'.format(ns['gpx']))
            if keywords_elem is not None:
                metadata['keywords'] = keywords_elem.text
            
            # 作成者
            author_elem = metadata_elem.find('.//{{{0}}}author'.format(ns['gpx']))
            if author_elem is not None:
                author_name_elem = author_elem.find('.//{{{0}}}name'.format(ns['gpx']))
                if author_name_elem is not None:
                    metadata['author'] = author_name_elem.text
            
            # リンク
            link_elem = metadata_elem.find('.//{{{0}}}link'.format(ns['gpx']))
            if link_elem is not None:
                link_href = link_elem.get('href')
                if link_href:
                    metadata['link'] = link_href
                
                link_text_elem = link_elem.find('.//{{{0}}}text'.format(ns['gpx']))
                if link_text_elem is not None:
                    metadata['link_text'] = link_text_elem.text
        
        return metadata

    def _parse_tracks(self, root: ET.Element, ns: Dict[str, str]) -> List[Dict[str, Any]]:
        """トラックを解析

        Args:
            root: XMLのルート要素
            ns: 名前空間の辞書

        Returns:
            List[Dict[str, Any]]: トラックのリスト
        """
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
            
            # トラック番号
            number_elem = trk.find('.//{{{0}}}number'.format(ns['gpx']))
            if number_elem is not None:
                track['number'] = number_elem.text
            
            # トラック時間（Runkeeper形式）
            time_elem = trk.find('.//{{{0}}}time'.format(ns['gpx']))
            if time_elem is not None:
                track['time'] = time_elem.text
            
            # トラック説明
            desc_elem = trk.find('.//{{{0}}}desc'.format(ns['gpx']))
            if desc_elem is not None:
                track['desc'] = desc_elem.text
            
            # トラックセグメントとポイント
            for trkseg in trk.findall('.//{{{0}}}trkseg'.format(ns['gpx'])):
                for trkpt in trkseg.findall('.//{{{0}}}trkpt'.format(ns['gpx'])):
                    point = self._parse_trackpoint(trkpt, ns)
                    track['points'].append(point)
            
            tracks.append(track)
        
        return tracks

    def _parse_trackpoint(self, trkpt: ET.Element, ns: Dict[str, str]) -> Dict[str, Any]:
        """トラックポイントを解析

        Args:
            trkpt: トラックポイント要素
            ns: 名前空間の辞書

        Returns:
            Dict[str, Any]: トラックポイントの辞書
        """
        point = {
            'lat': trkpt.get('lat'),
            'lon': trkpt.get('lon'),
            'ele': None,
            'time': None,
            'extensions': {}
        }
        
        # 標高
        ele_elem = trkpt.find('.//{{{0}}}ele'.format(ns['gpx']))
        if ele_elem is not None:
            point['ele'] = ele_elem.text
        
        # 時間
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
                
                # Garmin拡張の場合は特別処理
                if 'TrackPointExtension' in ext.tag:
                    for child in ext:
                        child_tag = child.tag.split('}')[-1]
                        point['extensions'][child_tag] = child.text
        
        return point

    def detect_service(self, gpx_data: Dict[str, Any]) -> str:
        """GPXデータからサービスを検出

        Args:
            gpx_data: GPXデータの辞書

        Returns:
            str: 検出されたサービス名
        """
        creator = gpx_data.get('creator', '').lower()
        
        if 'runkeeper' in creator:
            return 'runkeeper'
        elif 'yamareco' in creator:
            return 'yamareco'
        elif 'strava' in creator:
            return 'strava'
        elif 'garmin' in creator:
            return 'garmin'
        else:
            # トラック名やメタデータから推測
            for track in gpx_data.get('tracks', []):
                name = track.get('name', '').lower()
                if 'runkeeper' in name:
                    return 'runkeeper'
                elif 'yamareco' in name or 'track' == name:
                    return 'yamareco'
                elif 'strava' in name:
                    return 'strava'
            
            return 'unknown'