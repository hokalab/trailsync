#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TrailSync - Streamlitアプリケーション

このスクリプトは、Streamlitを使用してTrailSyncの機能をウェブアプリケーションとして提供します。
"""

import os
import tempfile
import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
from datetime import datetime
import xml.etree.ElementTree as ET
import base64
from io import BytesIO

# プロジェクトのモジュールをインポート
from src.universal_gpx_converter.parser import GPXParser
from src.universal_gpx_converter.converter import GPXConverter
from src.universal_gpx_converter.services.yamareco import YamarecoService
from src.universal_gpx_converter.services.strava import StravaService
from src.universal_gpx_converter.services.runkeeper import RunkeeperService

# アプリケーションのタイトルと説明
st.set_page_config(
    page_title="TrailSync",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# カスタムCSS
st.markdown("""
<style>
.buy-me-coffee {
    display: inline-block;
    padding: 10px 20px;
    background-color: #FFDD00;
    color: #000000 !important;
    font-weight: bold;
    text-decoration: none;
    border-radius: 5px;
    margin: 10px 0;
    text-align: center;
    transition: all 0.3s ease;
}
.buy-me-coffee:hover {
    background-color: #FFCC00;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
.buy-me-coffee img {
    vertical-align: middle;
    margin-right: 8px;
    height: 20px;
}
</style>
""", unsafe_allow_html=True)

# サイドバー
st.sidebar.title("TrailSync")
st.sidebar.info(
    "様々なアクティビティログサービス（ヤマレコ、Strava、Runkeeper等）の"
    "GPXファイルを統一フォーマットに変換し、相互運用性を高めるツールです。"
)

# Buy Me a Coffeeボタン
st.sidebar.markdown("""
<a href="https://www.buymeacoffee.com/mump0nd" target="_blank" class="buy-me-coffee">
    <img src="https://cdn.buymeacoffee.com/buttons/bmc-new-btn-logo.svg" alt="Buy me a coffee">
    Buy me a coffee
</a>
""", unsafe_allow_html=True)

# メインコンテンツ
st.title("TrailSync")
st.markdown(
    """
    このアプリケーションは、様々なサービスのGPXファイルを解析し、統一フォーマットに変換します。
    
    1. GPXファイルをアップロード
    2. サービスを自動検出または選択
    3. 変換オプションを設定
    4. 変換結果をダウンロード
    """
)

# サービスのマッピング
service_classes = {
    "yamareco": YamarecoService,
    "strava": StravaService,
    "runkeeper": RunkeeperService,
    "auto": None,
}

# GPXファイルのアップロード
uploaded_file = st.file_uploader("GPXファイルをアップロード", type=["gpx"])

if uploaded_file is not None:
    # 一時ファイルとして保存
    with tempfile.NamedTemporaryFile(delete=False, suffix=".gpx") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name
    
    try:
        # GPXファイルを解析
        parser = GPXParser()
        gpx_data = parser.parse_file(tmp_file_path)
        
        if gpx_data:
            # サービスを検出
            detected_service = parser.detect_service(gpx_data)
            
            # 解析結果を表示
            st.success(f"GPXファイルの解析に成功しました！")
            
            # サービス選択
            service_options = ["auto", "yamareco", "strava", "runkeeper"]
            selected_service = st.selectbox(
                "サービスを選択",
                service_options,
                index=service_options.index(detected_service) if detected_service in service_options else 0,
                format_func=lambda x: "自動検出" if x == "auto" else x.capitalize(),
            )
            
            # 変換オプション
            with st.expander("変換オプション", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    track_name = st.text_input(
                        "トラック名",
                        value=gpx_data['tracks'][0].get('name', '') if gpx_data['tracks'] else "",
                    )
                
                with col2:
                    activity_types = ["hiking", "running", "cycling", "walking", "swimming", "other"]
                    detected_type = next((t.get('type', 'hiking') for t in gpx_data['tracks'] if t.get('type')), "hiking")
                    activity_type = st.selectbox(
                        "アクティビティタイプ",
                        activity_types,
                        index=activity_types.index(detected_type) if detected_type in activity_types else 0,
                    )
            
            # GPXデータの概要を表示
            with st.expander("GPXデータの概要", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("ファイル情報")
                    st.write(f"作成者: {gpx_data['creator']}")
                    st.write(f"サービス: {detected_service.capitalize()}")
                    st.write(f"トラック数: {len(gpx_data['tracks'])}")
                    
                    if gpx_data['metadata']:
                        st.subheader("メタデータ")
                        for key, value in gpx_data['metadata'].items():
                            st.write(f"{key}: {value}")
                
                with col2:
                    st.subheader("トラック情報")
                    for i, track in enumerate(gpx_data['tracks']):
                        st.write(f"トラック {i+1}:")
                        st.write(f"名前: {track.get('name', 'なし')}")
                        st.write(f"タイプ: {track.get('type', 'なし')}")
                        st.write(f"ポイント数: {len(track['points'])}")
            
            # トラックポイントをDataFrameに変換
            points_data = []
            for point in gpx_data['all_points']:
                point_dict = {
                    'lat': float(point['lat']),
                    'lon': float(point['lon']),
                    'ele': float(point['ele']) if point['ele'] else None,
                    'time': point['time'] if point['time'] else None,
                }
                points_data.append(point_dict)
            
            df = pd.DataFrame(points_data)
            
            # 地図の表示
            if not df.empty and 'lat' in df.columns and 'lon' in df.columns:
                st.subheader("トラックの地図表示")
                
                # 中心座標を計算
                center_lat = df['lat'].mean()
                center_lon = df['lon'].mean()
                
                # Foliumマップを作成
                m = folium.Map(location=[center_lat, center_lon], zoom_start=12)
                
                # トラックを追加
                points = df[['lat', 'lon']].values.tolist()
                folium.PolyLine(points, color='blue', weight=3, opacity=0.7).add_to(m)
                
                # 開始点と終了点にマーカーを追加
                folium.Marker(
                    location=[df['lat'].iloc[0], df['lon'].iloc[0]],
                    popup='開始点',
                    icon=folium.Icon(color='green', icon='play'),
                ).add_to(m)
                
                folium.Marker(
                    location=[df['lat'].iloc[-1], df['lon'].iloc[-1]],
                    popup='終了点',
                    icon=folium.Icon(color='red', icon='stop'),
                ).add_to(m)
                
                # 地図を表示
                folium_static(m)
            
            # 変換ボタン
            if st.button("統一フォーマットに変換"):
                # サービス固有の処理
                if selected_service != "auto":
                    service_class = service_classes[selected_service]
                    service = service_class()
                    gpx_data = service.convert_to_universal(gpx_data)
                else:
                    # 自動検出の場合
                    service_class = service_classes.get(detected_service)
                    if service_class:
                        service = service_class()
                        gpx_data = service.convert_to_universal(gpx_data)
                
                # 統一フォーマットに変換
                converter = GPXConverter()
                output_file = os.path.join(tempfile.gettempdir(), "converted.gpx")
                
                if converter.convert_to_universal_format(gpx_data, output_file, track_name, activity_type):
                    st.success("変換が完了しました！")
                    
                    # 変換結果をダウンロード可能にする
                    with open(output_file, "r", encoding="utf-8") as f:
                        converted_data = f.read()
                    
                    b64 = base64.b64encode(converted_data.encode()).decode()
                    href = f'<a href="data:application/gpx+xml;base64,{b64}" download="converted.gpx">変換されたGPXファイルをダウンロード</a>'
                    st.markdown(href, unsafe_allow_html=True)
                    
                    # 変換結果を表示
                    with st.expander("変換結果のプレビュー", expanded=False):
                        st.code(converted_data, language="xml")
                else:
                    st.error("変換に失敗しました。")
        else:
            st.error("GPXファイルの解析に失敗しました。")
    
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
    
    finally:
        # 一時ファイルを削除
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)

# フッター
st.markdown("---")
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center;">
    <div>
        <p>© 2025 HōkaLabs. All rights reserved.</p>
    </div>
    <div>
        <a href="https://www.buymeacoffee.com/mump0nd" target="_blank" class="buy-me-coffee">
            <img src="https://cdn.buymeacoffee.com/buttons/bmc-new-btn-logo.svg" alt="Buy me a coffee">
            Buy me a coffee
        </a>
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.info(
    "このアプリケーションは、TrailSyncのデモです。"
    "詳細については、[GitHub](https://github.com/HokaLabs/trailsync)を参照してください。"
)