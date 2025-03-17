#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ヤマレコサービス固有モジュール

このモジュールは、ヤマレコのGPXファイルに関する固有の処理を行う機能を提供します。
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# ロギング設定
logger = logging.getLogger(__name__)

class YamarecoService:
    """ヤマレコサービスに関する処理を行うクラス"""

    def __init__(self):
        """初期化"""
        pass

    def detect(self, gpx_data: Dict[str, Any]) -> bool:
        """GPXデータがヤマレコ形式かどうかを判定

        Args:
            gpx_data: GPXデータ

        Returns:
            bool: ヤマレコ形式かどうか
        """
        creator = gpx_data.get('creator', '').lower()
        if 'yamareco' in creator:
            return True
        
        # トラック名が「track」で、トラック番号が設定されている場合もヤマレコの可能性が高い
        for track in gpx_data.get('tracks', []):
            if track.get('name') == 'track' and track.get('number'):
                return True
        
        return False

    def extract_metadata(self, gpx_data: Dict[str, Any]) -> Dict[str, Any]:
        """ヤマレコ固有のメタデータを抽出

        Args:
            gpx_data: GPXデータ

        Returns:
            Dict[str, Any]: 抽出したメタデータ
        """
        metadata = {}
        
        # ヤマレコの場合、トラック名は通常「track」で、山域情報などは含まれていない
        # 必要に応じて、ファイル名やその他の情報から推測する
        
        return metadata

    def extract_track_info(self, gpx_data: Dict[str, Any]) -> Dict[str, Any]:
        """ヤマレコ固有のトラック情報を抽出

        Args:
            gpx_data: GPXデータ

        Returns:
            Dict[str, Any]: 抽出したトラック情報
        """
        track_info = {}
        
        for track in gpx_data.get('tracks', []):
            # トラック番号
            if track.get('number'):
                track_info['number'] = track.get('number')
            
            # その他の情報があれば抽出
        
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
            
            # 緯度・経度の精度を調整（ヤマレコは小数点以下14桁と非常に精度が高い）
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
            
            # 標高の精度を調整（ヤマレコは整数値）
            if 'ele' in normalized_point and normalized_point['ele']:
                try:
                    ele = float(normalized_point['ele'])
                    normalized_point['ele'] = f"{ele:.1f}"  # 小数点以下1桁に調整
                except ValueError:
                    pass
            
            normalized_points.append(normalized_point)
        
        return normalized_points

    def convert_to_universal(self, gpx_data: Dict[str, Any]) -> Dict[str, Any]:
        """ヤマレコ形式のGPXデータを統一フォーマットに変換

        Args:
            gpx_data: ヤマレコ形式のGPXデータ

        Returns:
            Dict[str, Any]: 統一フォーマットのGPXデータ
        """
        universal_data = gpx_data.copy()
        
        # サービス情報を追加
        universal_data['service'] = 'yamareco'
        
        # メタデータを抽出・追加
        yamareco_metadata = self.extract_metadata(gpx_data)
        if yamareco_metadata:
            universal_data['metadata'].update(yamareco_metadata)
        
        # トラック情報を抽出・追加
        for i, track in enumerate(universal_data.get('tracks', [])):
            yamareco_track_info = self.extract_track_info(gpx_data)
            if yamareco_track_info:
                universal_data['tracks'][i].update(yamareco_track_info)
            
            # トラックポイントを正規化
            if 'points' in track:
                universal_data['tracks'][i]['points'] = self.normalize_trackpoints(track['points'])
        
        # 全ポイントも正規化
        if 'all_points' in universal_data:
            universal_data['all_points'] = self.normalize_trackpoints(universal_data['all_points'])
        
        return universal_data