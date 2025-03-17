#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Runkeeperサービス固有モジュール

このモジュールは、RunkeeperのGPXファイルに関する固有の処理を行う機能を提供します。
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

# ロギング設定
logger = logging.getLogger(__name__)

class RunkeeperService:
    """Runkeeperサービスに関する処理を行うクラス"""

    def __init__(self):
        """初期化"""
        pass

    def detect(self, gpx_data: Dict[str, Any]) -> bool:
        """GPXデータがRunkeeper形式かどうかを判定

        Args:
            gpx_data: GPXデータ

        Returns:
            bool: Runkeeper形式かどうか
        """
        creator = gpx_data.get('creator', '').lower()
        if 'runkeeper' in creator:
            return True
        
        # トラックに時間要素があり、トラック名がCDATAセクションを含む場合もRunkeeperの可能性が高い
        for track in gpx_data.get('tracks', []):
            if track.get('time') and track.get('name') and ('CDATA' in track.get('name') or 'Runkeeper' in track.get('name')):
                return True
        
        return False

    def extract_metadata(self, gpx_data: Dict[str, Any]) -> Dict[str, Any]:
        """Runkeeper固有のメタデータを抽出

        Args:
            gpx_data: GPXデータ

        Returns:
            Dict[str, Any]: 抽出したメタデータ
        """
        metadata = {}
        
        # Runkeeperの場合、メタデータセクションはないが、トラックに時間情報がある
        for track in gpx_data.get('tracks', []):
            if track.get('time'):
                metadata['time'] = track.get('time')
                break
        
        return metadata

    def extract_track_info(self, gpx_data: Dict[str, Any]) -> Dict[str, Any]:
        """Runkeeper固有のトラック情報を抽出

        Args:
            gpx_data: GPXデータ

        Returns:
            Dict[str, Any]: 抽出したトラック情報
        """
        track_info = {}
        
        for track in gpx_data.get('tracks', []):
            # トラック名（CDATAセクションを処理）
            if track.get('name'):
                name = track.get('name')
                if 'CDATA' in name:
                    # CDATAセクションを処理
                    name = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', name)
                track_info['name'] = name
            
            # トラック時間
            if track.get('time'):
                track_info['time'] = track.get('time')
            
            # アクティビティタイプを推測
            if track.get('name'):
                name = track.get('name').lower()
                if 'running' in name or 'run' in name:
                    track_info['type'] = 'running'
                elif 'walking' in name or 'walk' in name:
                    track_info['type'] = 'walking'
                elif 'hiking' in name or 'hike' in name:
                    track_info['type'] = 'hiking'
                elif 'cycling' in name or 'bike' in name or 'biking' in name:
                    track_info['type'] = 'cycling'
        
        return track_info

    def normalize_trackpoints(self, points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """トラックポイントを正規化

        Args:
            points: トラックポイントのリスト

        Returns:
            List[Dict[str, Any]]: 正規化したトラックポイントのリスト
        """
        normalized_points = []
        
        for point in points:
            normalized_point = point.copy()
            
            # 緯度・経度の精度を調整（Runkeeperは小数点以下9桁）
            if 'lat' in normalized_point:
                try:
                    lat = float(normalized_point['lat'])
                    normalized_point['lat'] = f"{lat:.9f}"  # 小数点以下9桁に調整
                except ValueError:
                    pass
            
            if 'lon' in normalized_point:
                try:
                    lon = float(normalized_point['lon'])
                    normalized_point['lon'] = f"{lon:.9f}"  # 小数点以下9桁に調整
                except ValueError:
                    pass
            
            # 標高の精度を調整（Runkeeperは小数点以下1桁）
            if 'ele' in normalized_point and normalized_point['ele']:
                try:
                    ele = float(normalized_point['ele'])
                    normalized_point['ele'] = f"{ele:.1f}"  # 小数点以下1桁に調整
                except ValueError:
                    pass
            
            normalized_points.append(normalized_point)
        
        return normalized_points

    def convert_to_universal(self, gpx_data: Dict[str, Any]) -> Dict[str, Any]:
        """Runkeeper形式のGPXデータを統一フォーマットに変換

        Args:
            gpx_data: Runkeeper形式のGPXデータ

        Returns:
            Dict[str, Any]: 統一フォーマットのGPXデータ
        """
        universal_data = gpx_data.copy()
        
        # サービス情報を追加
        universal_data['service'] = 'runkeeper'
        
        # メタデータを抽出・追加
        runkeeper_metadata = self.extract_metadata(gpx_data)
        if runkeeper_metadata:
            if 'metadata' not in universal_data:
                universal_data['metadata'] = {}
            universal_data['metadata'].update(runkeeper_metadata)
        
        # トラック情報を抽出・追加
        for i, track in enumerate(universal_data.get('tracks', [])):
            runkeeper_track_info = self.extract_track_info(gpx_data)
            if runkeeper_track_info:
                universal_data['tracks'][i].update(runkeeper_track_info)
            
            # トラックポイントを正規化
            if 'points' in track:
                universal_data['tracks'][i]['points'] = self.normalize_trackpoints(track['points'])
        
        # 全ポイントも正規化
        if 'all_points' in universal_data:
            universal_data['all_points'] = self.normalize_trackpoints(universal_data['all_points'])
        
        return universal_data