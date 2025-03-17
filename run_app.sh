#!/bin/bash

# 仮想環境を有効化
source venv/bin/activate

# 依存パッケージをインストール
pip install -r requirements.txt

# Streamlitアプリケーションを実行
streamlit run app.py