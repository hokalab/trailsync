#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Stravaサービス固有モジュール

このモジュールは、StravaのGPXファイルに関する固有の処理を行う機能を提供します。
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

# ロギング設定
logger = logging.getLogger(__name__)

class StravaService:
    """Stravaサービスに関する処理を行うクラス"""

    def __init__(self):
        """初期化"""
        pass

    def detect(self, gpx_data: Dict[str, Any]) -> bool:
        """GPXデータがStrava形式かどうかを判定

        Args:
            gpx_data: GPXデータ

        Returns:
            bool: Strava形式かどうか
        """
        creator = gpx_data.get('creator', '').lower()
        if 'strava' in creator:
            return True
        
        # メタデータがあり、トラックにタイプが設定されている場合もStravaの可能性が高い
        if gpx_data.get('metadata') and len(gpx_data.get('metadata', {})) > 0:
            for track in gpx_data.get('tracks', []):
                if track.get('type'):
                    return True
        
        return False

    def extract_metadata(self, gpx_data: Dict[str, Any]) -> Dict[str, Any]:
        """Strava固有のメタデータを抽出

        Args:
            gpx_data: GPXデータ

        Returns:
            Dict[str, Any]: 抽出したメタデータ
        """
        metadata = {}
        
        # Stravaの場合、メタデータセクションに時間情報が含まれている
        if gpx_data.get('metadata', {}).get('time'):
            metadata['time'] = gpx_data['metadata']['time']
        
        return metadata

    def extract_track_info(self, gpx_data: Dict[str, Any]) -> Dict[str, Any]:
        """Strava固有のトラック情報を抽出

        Args:
            gpx_data: GPXデータ

        Returns:
            Dict[str, Any]: 抽出したトラック情報
        """
        track_info = {}
        
        for track in gpx_data.get('tracks', []):
            # アクティビティタイプ
            if track.get('type'):
                track_info['type'] = track.get('type')
            
            # トラック名（Unicodeエスケープを処理）
            if track.get('name'):
                name = track.get('name')
                # Unicodeエスケープシーケンスを処理
                if '\\u' in name:
                    try:
                        # Pythonのunicode-escape機能を使用
                        name = name.encode('latin1').decode('unicode-escape')
                    except UnicodeError:
                        # エラーが発生した場合は元の名前を使用
                        pass
                track_info['name'] = name
        
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
            
            # 緯度・経度の精度を調整（Stravaは小数点以下7桁程度）
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
            
            # 標高の精度を調整（Stravaは小数点以下1桁）
            if 'ele' in normalized_point and normalized_point['ele']:
                try:
                    ele = float(normalized_point['ele'])
                    normalized_point['ele'] = f"{ele:.1f}"  # 小数点以下1桁に調整
                except ValueError:
                    pass
            
            normalized_points.append(normalized_point)
        
        return normalized_points

    def convert_to_universal(self, gpx_data: Dict[str, Any]) -> Dict[str, Any]:
        """Strava形式のGPXデータを統一フォーマットに変換

        Args:
            gpx_data: Strava形式のGPXデータ

        Returns:
            Dict[str, Any]: 統一フォーマットのGPXデータ
        """
        universal_data = gpx_data.copy()
        
        # サービス情報を追加
        universal_data['service'] = 'strava'
        
        # メタデータを抽出・追加
        strava_metadata = self.extract_metadata(gpx_data)
        if strava_metadata:
            universal_data['metadata'].update(strava_metadata)
        
        # トラック情報を抽出・追加
        for i, track in enumerate(universal_data.get('tracks', [])):
            strava_track_info = self.extract_track_info(gpx_data)
            if strava_track_info:
                universal_data['tracks'][i].update(strava_track_info)
            
            # トラックポイントを正規化
            if 'points' in track:
                universal_data['tracks'][i]['points'] = self.normalize_trackpoints(track['points'])
        
        # 全ポイントも正規化
        if 'all_points' in universal_data:
            universal_data['all_points'] = self.normalize_trackpoints(universal_data['all_points'])
        
        return universal_data