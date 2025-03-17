#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TrailSync - Webアプリケーション

このスクリプトは、DashとStreamlitの両方に対応したTrailSyncのWebアプリケーションを提供します。
Renderでのデプロイに対応しています。
"""

import os
import tempfile
import base64
from io import BytesIO
from datetime import datetime
import xml.etree.ElementTree as ET

# Dash関連のインポート
import dash
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

# Folium関連のインポート（地図表示用）
import folium

# プロジェクトのモジュールをインポート
try:
    from src.trailsync.parser import GPXParser
    from src.trailsync.converter import GPXConverter
    from src.trailsync.services.yamareco import YamarecoService
    from src.trailsync.services.strava import StravaService
    from src.trailsync.services.runkeeper import RunkeeperService
except ImportError:
    # ローカル開発環境用のフォールバック
    print("Warning: Unable to import from src.trailsync. Using local imports.")
    # ローカルインポートを設定
    from src.universal_gpx_converter.parser import GPXParser
    from src.universal_gpx_converter.converter import GPXConverter
    from src.universal_gpx_converter.services.yamareco import YamarecoService
    from src.universal_gpx_converter.services.strava import StravaService
    from src.universal_gpx_converter.services.runkeeper import RunkeeperService

# サービスのマッピング
service_classes = {
    "yamareco": YamarecoService,
    "strava": StravaService,
    "runkeeper": RunkeeperService,
    "auto": None,
}

# Dashアプリケーションの初期化
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)
server = app.server  # Renderデプロイ用にserverを公開

# アプリケーションのタイトルを設定
app.title = "TrailSync"

# レイアウトの定義
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("TrailSync", className="text-center my-4"),
            html.P(
                "様々なアクティビティログサービス（ヤマレコ、Strava、Runkeeper等）の"
                "GPXファイルを統一フォーマットに変換し、相互運用性を高めるツールです。",
                className="text-center mb-4"
            ),
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("GPXファイルをアップロード"),
                dbc.CardBody([
                    dcc.Upload(
                        id='upload-gpx',
                        children=html.Div([
                            'ドラッグ＆ドロップまたは ',
                            html.A('ファイルを選択')
                        ]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                        multiple=False
                    ),
                    html.Div(id='upload-output'),
                ])
            ], className="mb-4"),
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("変換オプション"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("サービスを選択"),
                            dcc.Dropdown(
                                id='service-dropdown',
                                options=[
                                    {'label': '自動検出', 'value': 'auto'},
                                    {'label': 'Yamareco', 'value': 'yamareco'},
                                    {'label': 'Strava', 'value': 'strava'},
                                    {'label': 'Runkeeper', 'value': 'runkeeper'}
                                ],
                                value='auto',
                                clearable=False
                            ),
                        ], width=6),
                        dbc.Col([
                            html.Label("アクティビティタイプ"),
                            dcc.Dropdown(
                                id='activity-type-dropdown',
                                options=[
                                    {'label': 'ハイキング', 'value': 'hiking'},
                                    {'label': 'ランニング', 'value': 'running'},
                                    {'label': 'サイクリング', 'value': 'cycling'},
                                    {'label': 'ウォーキング', 'value': 'walking'},
                                    {'label': 'スイミング', 'value': 'swimming'},
                                    {'label': 'その他', 'value': 'other'}
                                ],
                                value='hiking',
                                clearable=False
                            ),
                        ], width=6)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            html.Label("トラック名"),
                            dbc.Input(id='track-name-input', type='text', placeholder='トラック名を入力'),
                        ], width=12, className="mt-3")
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Button("統一フォーマットに変換", id='convert-button', color="primary", className="mt-3", disabled=True),
                        ], width=12, className="text-center")
                    ])
                ])
            ], className="mb-4"),
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            html.Div(id='gpx-info-output'),
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            html.Div(id='map-output'),
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            html.Div(id='conversion-output'),
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            html.Hr(),
            html.Footer([
                html.P("© 2025 HōkaLabs. All rights reserved.", className="text-center"),
                html.P([
                    "開発者をサポートする: ",
                    html.A("Buy me a coffee", href="https://www.buymeacoffee.com/mump0nd", target="_blank", className="coffee-btn")
                ], className="text-center"),
                html.P([
                    "詳細については、",
                    html.A("GitHub", href="https://github.com/mump0nd/trailsync", target="_blank"),
                    "を参照してください。"
                ], className="text-center")
            ])
        ], width=12)
    ])
], fluid=True)

# カスタムCSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            .coffee-btn {
                display: inline-block;
                padding: 5px 15px;
                background-color: #FFDD00;
                color: #000000 !important;
                font-weight: bold;
                text-decoration: none;
                border-radius: 5px;
                margin: 5px;
                text-align: center;
                transition: all 0.3s ease;
            }
            .coffee-btn:hover {
                background-color: #FFCC00;
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# コールバック関数
@app.callback(
    [Output('upload-output', 'children'),
     Output('convert-button', 'disabled'),
     Output('service-dropdown', 'value'),
     Output('track-name-input', 'value')],
    [Input('upload-gpx', 'contents')],
    [State('upload-gpx', 'filename')]
)
def update_output(contents, filename):
    if contents is None:
        return html.Div("ファイルをアップロードしてください"), True, 'auto', ''
    
    if not filename.endswith('.gpx'):
        return html.Div("GPXファイルのみアップロード可能です"), True, 'auto', ''
    
    try:
        # ファイルの内容をデコード
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        # 一時ファイルとして保存
        with tempfile.NamedTemporaryFile(delete=False, suffix=".gpx") as tmp_file:
            tmp_file.write(decoded)
            tmp_file_path = tmp_file.name
        
        # GPXファイルを解析
        parser = GPXParser()
        gpx_data = parser.parse_file(tmp_file_path)
        
        if gpx_data:
            # サービスを検出
            detected_service = parser.detect_service(gpx_data)
            
            # トラック名を取得
            track_name = gpx_data['tracks'][0].get('name', '') if gpx_data['tracks'] else ""
            
            # 一時ファイルを削除
            os.unlink(tmp_file_path)
            
            return html.Div([
                html.P(f"ファイル名: {filename}"),
                html.P(f"検出されたサービス: {detected_service.capitalize() if detected_service else '不明'}")
            ]), False, detected_service if detected_service else 'auto', track_name
        else:
            # 一時ファイルを削除
            os.unlink(tmp_file_path)
            return html.Div("GPXファイルの解析に失敗しました"), True, 'auto', ''
    
    except Exception as e:
        return html.Div(f"エラーが発生しました: {str(e)}"), True, 'auto', ''

@app.callback(
    [Output('gpx-info-output', 'children'),
     Output('map-output', 'children')],
    [Input('upload-gpx', 'contents')],
    [State('upload-gpx', 'filename')]
)
def display_gpx_info(contents, filename):
    if contents is None:
        return html.Div(), html.Div()
    
    if not filename.endswith('.gpx'):
        return html.Div(), html.Div()
    
    try:
        # ファイルの内容をデコード
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        # 一時ファイルとして保存
        with tempfile.NamedTemporaryFile(delete=False, suffix=".gpx") as tmp_file:
            tmp_file.write(decoded)
            tmp_file_path = tmp_file.name
        
        # GPXファイルを解析
        parser = GPXParser()
        gpx_data = parser.parse_file(tmp_file_path)
        
        if gpx_data:
            # サービスを検出
            detected_service = parser.detect_service(gpx_data)
            
            # GPXデータの概要を表示
            info_card = dbc.Card([
                dbc.CardHeader("GPXデータの概要"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H5("ファイル情報"),
                            html.P(f"作成者: {gpx_data['creator']}"),
                            html.P(f"サービス: {detected_service.capitalize() if detected_service else '不明'}"),
                            html.P(f"トラック数: {len(gpx_data['tracks'])}"),
                            
                            html.H5("メタデータ", className="mt-3") if gpx_data['metadata'] else html.Div(),
                            html.Div([
                                html.P(f"{key}: {value}") for key, value in gpx_data['metadata'].items()
                            ]) if gpx_data['metadata'] else html.Div(),
                        ], width=6),
                        dbc.Col([
                            html.H5("トラック情報"),
                            html.Div([
                                html.Div([
                                    html.P(f"トラック {i+1}:"),
                                    html.P(f"名前: {track.get('name', 'なし')}"),
                                    html.P(f"タイプ: {track.get('type', 'なし')}"),
                                    html.P(f"ポイント数: {len(track['points'])}")
                                ]) for i, track in enumerate(gpx_data['tracks'])
                            ])
                        ], width=6)
                    ])
                ])
            ], className="mb-4")
            
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
            map_card = html.Div()
            if not df.empty and 'lat' in df.columns and 'lon' in df.columns:
                # Plotlyを使用して地図を表示
                fig = px.line_mapbox(
                    df, 
                    lat='lat', 
                    lon='lon', 
                    hover_name=df.index,
                    mapbox_style="open-street-map",
                    zoom=10
                )
                
                # 開始点と終了点にマーカーを追加
                fig.add_scattermapbox(
                    lat=[df['lat'].iloc[0]],
                    lon=[df['lon'].iloc[0]],
                    mode='markers',
                    marker=dict(size=10, color='green'),
                    name='開始点'
                )
                
                fig.add_scattermapbox(
                    lat=[df['lat'].iloc[-1]],
                    lon=[df['lon'].iloc[-1]],
                    mode='markers',
                    marker=dict(size=10, color='red'),
                    name='終了点'
                )
                
                # レイアウトの調整
                fig.update_layout(
                    margin={"r":0,"t":0,"l":0,"b":0},
                    height=500,
                    legend=dict(
                        yanchor="top",
                        y=0.99,
                        xanchor="left",
                        x=0.01
                    )
                )
                
                map_card = dbc.Card([
                    dbc.CardHeader("トラックの地図表示"),
                    dbc.CardBody([
                        dcc.Graph(figure=fig)
                    ])
                ], className="mb-4")
            
            # 一時ファイルを削除
            os.unlink(tmp_file_path)
            
            return info_card, map_card
        else:
            # 一時ファイルを削除
            os.unlink(tmp_file_path)
            return html.Div(), html.Div()
    
    except Exception as e:
        return html.Div(f"エラーが発生しました: {str(e)}"), html.Div()

@app.callback(
    Output('conversion-output', 'children'),
    [Input('convert-button', 'n_clicks')],
    [State('upload-gpx', 'contents'),
     State('service-dropdown', 'value'),
     State('activity-type-dropdown', 'value'),
     State('track-name-input', 'value')]
)
def convert_gpx(n_clicks, contents, service, activity_type, track_name):
    if n_clicks is None or contents is None:
        return html.Div()
    
    try:
        # ファイルの内容をデコード
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        # 一時ファイルとして保存
        with tempfile.NamedTemporaryFile(delete=False, suffix=".gpx") as tmp_file:
            tmp_file.write(decoded)
            tmp_file_path = tmp_file.name
        
        # GPXファイルを解析
        parser = GPXParser()
        gpx_data = parser.parse_file(tmp_file_path)
        
        if gpx_data:
            # サービス固有の処理
            if service != "auto":
                service_class = service_classes[service]
                service_instance = service_class()
                gpx_data = service_instance.convert_to_universal(gpx_data)
            else:
                # 自動検出の場合
                detected_service = parser.detect_service(gpx_data)
                service_class = service_classes.get(detected_service)
                if service_class:
                    service_instance = service_class()
                    gpx_data = service_instance.convert_to_universal(gpx_data)
            
            # 統一フォーマットに変換
            converter = GPXConverter()
            output_file = os.path.join(tempfile.gettempdir(), "converted.gpx")
            
            if converter.convert_to_universal_format(gpx_data, output_file, track_name, activity_type):
                # 変換結果を読み込む
                with open(output_file, "r", encoding="utf-8") as f:
                    converted_data = f.read()
                
                # Base64エンコード
                b64 = base64.b64encode(converted_data.encode()).decode()
                
                # 変換結果を表示
                return dbc.Card([
                    dbc.CardHeader("変換結果"),
                    dbc.CardBody([
                        html.P("変換が完了しました！"),
                        html.A(
                            "変換されたGPXファイルをダウンロード",
                            href=f"data:application/gpx+xml;base64,{b64}",
                            download="converted.gpx",
                            className="btn btn-success mb-3"
                        ),
                        dbc.Card([
                            dbc.CardHeader("変換結果のプレビュー"),
                            dbc.CardBody([
                                html.Pre(converted_data, style={"max-height": "400px", "overflow": "auto"})
                            ])
                        ])
                    ])
                ])
            else:
                return dbc.Alert("変換に失敗しました。", color="danger")
        else:
            return dbc.Alert("GPXファイルの解析に失敗しました。", color="danger")
    
    except Exception as e:
        return dbc.Alert(f"エラーが発生しました: {str(e)}", color="danger")
    
    finally:
        # 一時ファイルを削除
        if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)

# Streamlitとの互換性のためのエントリーポイント
if __name__ == '__main__':
    app.run_server(debug=True)