#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TrailSync - Webアプリケーション

このスクリプトは、DashベースのTrailSyncのWebアプリケーションを提供します。
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
import pandas as pd
import plotly.express as px

# 改良版スクリプトのインポート
from src.yamareco_to_runkeeper_improved import convert_gpx

# Initialize the Dash app
app = dash.Dash(__name__, title="TrailSync", external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server  # Expose the server for Render deployment

# Define the layout
app.layout = html.Div([
    html.H1("TrailSync", style={'textAlign': 'center', 'marginBottom': '30px'}),
    html.Div([
        html.H2("GPXファイル変換ツール", style={'textAlign': 'center'}),
        html.P("ヤマレコのGPXファイルをRunkeeper互換フォーマットに変換します。", style={'textAlign': 'center'}),
        
        # File Upload
        dcc.Upload(
            id='upload-gpx',
            children=html.Div([
                'ドラッグ＆ドロップまたは',
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
                'margin': '10px 0'
            },
            multiple=False
        ),
        
        # Options
        html.Div([
            html.H3("変換オプション"),
            
            # Activity Type
            html.Div([
                html.Label("アクティビティタイプ"),
                dcc.Dropdown(
                    id='activity-type',
                    options=[
                        {'label': 'ハイキング', 'value': 'hiking'},
                        {'label': 'ランニング', 'value': 'running'},
                        {'label': 'サイクリング', 'value': 'cycling'},
                        {'label': 'ウォーキング', 'value': 'walking'}
                    ],
                    value='hiking'
                )
            ], style={'marginBottom': '15px'}),
            
            # Track Name
            html.Div([
                html.Label("トラック名 (空白の場合は日時から自動生成)"),
                dcc.Input(
                    id='track-name',
                    type='text',
                    placeholder='例: 京都一周トレイル2泊3日',
                    style={'width': '100%'}
                )
            ], style={'marginBottom': '15px'}),
            
            # Format XML
            html.Div([
                dcc.Checklist(
                    id='format-xml',
                    options=[
                        {'label': 'XMLを整形する（インデントを追加）', 'value': 'format'}
                    ],
                    value=[]
                )
            ], style={'marginBottom': '15px'}),
            
            # Coordinate Precision
            html.Div([
                html.Label("座標精度（小数点以下の桁数）"),
                dcc.Slider(
                    id='coordinate-precision',
                    min=4,
                    max=8,
                    step=1,
                    value=6,
                    marks={i: str(i) for i in range(4, 9)}
                )
            ], style={'marginBottom': '15px'}),
            
            # Elevation Adjustment
            html.Div([
                html.Label("標高調整値（メートル単位）"),
                dcc.Input(
                    id='elevation-adjustment',
                    type='number',
                    value=5.2,
                    step=0.1,
                    style={'width': '100%'}
                )
            ], style={'marginBottom': '15px'}),
            
            # Add Metadata
            html.Div([
                dcc.Checklist(
                    id='add-metadata',
                    options=[
                        {'label': 'メタデータセクションを追加する', 'value': 'add'}
                    ],
                    value=['add']
                )
            ], style={'marginBottom': '15px'}),
            
            # Keep Source
            html.Div([
                dcc.Checklist(
                    id='keep-source',
                    options=[
                        {'label': '元のサービス情報を保持する', 'value': 'keep'}
                    ],
                    value=['keep']
                )
            ], style={'marginBottom': '15px'})
        ], style={'marginTop': '20px', 'marginBottom': '20px'}),
        
        # Convert Button
        html.Button('変換', id='convert-button', n_clicks=0, style={
            'backgroundColor': '#4CAF50',
            'color': 'white',
            'padding': '10px 20px',
            'border': 'none',
            'borderRadius': '4px',
            'cursor': 'pointer',
            'fontSize': '16px',
            'marginTop': '10px',
            'width': '100%'
        }),
        
        # Status and Download
        html.Div(id='conversion-status'),
        html.Div(id='download-container')
    ], style={'maxWidth': '800px', 'margin': '0 auto', 'padding': '20px', 'backgroundColor': '#f9f9f9', 'borderRadius': '10px'})
])

# Callback for file processing
@app.callback(
    [Output('conversion-status', 'children'),
     Output('download-container', 'children')],
    [Input('convert-button', 'n_clicks')],
    [State('upload-gpx', 'contents'),
     State('upload-gpx', 'filename'),
     State('activity-type', 'value'),
     State('track-name', 'value'),
     State('format-xml', 'value'),
     State('coordinate-precision', 'value'),
     State('elevation-adjustment', 'value'),
     State('add-metadata', 'value'),
     State('keep-source', 'value')]
)
def process_gpx(n_clicks, contents, filename, activity_type, track_name, format_xml, 
                coordinate_precision, elevation_adjustment, add_metadata, keep_source):
    if n_clicks == 0 or contents is None:
        return "", ""
    
    try:
        # Decode the file content
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        # Create a temporary file for the input
        with tempfile.NamedTemporaryFile(delete=False, suffix='.gpx') as temp_in:
            temp_in.write(decoded)
            input_path = temp_in.name
        
        # Create a temporary file for the output
        with tempfile.NamedTemporaryFile(delete=False, suffix='.gpx') as temp_out:
            output_path = temp_out.name
        
        # Set options
        options = {
            'activity_type': activity_type,
            'format_xml': 'format' in format_xml,
            'coordinate_precision': coordinate_precision,
            'elevation_adjustment': float(elevation_adjustment),
            'add_metadata': 'add' in add_metadata,
            'keep_source': 'keep' in keep_source
        }
        
        if track_name:
            options['track_name'] = track_name
        
        # Convert the file using the improved converter
        success = convert_gpx(input_path, output_path, **options)
        
        if success:
            # Read the converted file
            with open(output_path, 'r') as f:
                converted_data = f.read()
            
            # Create a download link
            b64 = base64.b64encode(converted_data.encode()).decode()
            href = f"data:text/xml;base64,{b64}"
            
            # Clean up temporary files
            os.unlink(input_path)
            os.unlink(output_path)
            
            return (
                html.Div([
                    html.H4("変換成功", style={'color': 'green'}),
                    html.P(f"ファイル '{filename}' を正常に変換しました。")
                ]),
                html.Div([
                    html.H4("ダウンロード"),
                    html.A(
                        "変換されたGPXファイルをダウンロード",
                        href=href,
                        download="converted.gpx",
                        style={
                            'backgroundColor': '#008CBA',
                            'color': 'white',
                            'padding': '10px 20px',
                            'textDecoration': 'none',
                            'borderRadius': '4px',
                            'display': 'inline-block',
                            'marginBottom': '20px'
                        }
                    ),
                    html.H4("プレビュー"),
                    html.Div([
                        html.Pre(converted_data, style={"max-height": "400px", "overflow": "auto"})
                    ], style={"border": "1px solid #ddd", "padding": "10px", "borderRadius": "4px"})
                ])
            )
        else:
            # Clean up temporary files
            os.unlink(input_path)
            os.unlink(output_path)
            
            return (
                html.Div([
                    html.H4("変換失敗", style={'color': 'red'}),
                    html.P("ファイルの変換中にエラーが発生しました。")
                ]),
                ""
            )
    
    except Exception as e:
        return (
            html.Div([
                html.H4("エラー", style={'color': 'red'}),
                html.P(f"エラーが発生しました: {str(e)}")
            ]),
            ""
        )

if __name__ == '__main__':
    app.run_server(debug=True)