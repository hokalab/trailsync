#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
改良版ヤマレコ→ランキーパー変換スクリプトのテスト

このスクリプトは、元のyamareco_to_runkeeper.pyと改良版のyamareco_to_runkeeper_improved.pyを
使用して同じヤマレコGPXファイルを変換し、結果を比較します。
"""

import os
import sys
import subprocess
import xml.etree.ElementTree as ET
import difflib
import argparse
from datetime import datetime

# プロジェクトのルートディレクトリを取得
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
src_dir = os.path.join(project_root, 'src')

# スクリプトのパス
original_script = os.path.join(src_dir, 'yamareco_to_runkeeper.py')
improved_script = os.path.join(src_dir, 'yamareco_to_runkeeper_improved.py')

# テストデータのパス
test_data_dir = os.path.join(script_dir, 'test_data')
yamareco_gpx = os.path.join(test_data_dir, 'yamareco.gpx')

# 出力ファイルのパス
output_dir = os.path.join(test_data_dir, 'output')
original_output = os.path.join(output_dir, 'original_output.gpx')
improved_output = os.path.join(output_dir, 'improved_output.gpx')
improved_formatted_output = os.path.join(output_dir, 'improved_formatted_output.gpx')
diff_output = os.path.join(output_dir, 'diff_output.html')

def ensure_dir(directory):
    """ディレクトリが存在しない場合は作成する"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def run_original_converter():
    """元のスクリプトを実行"""
    print(f"元のスクリプト {original_script} を実行中...")
    cmd = [sys.executable, original_script, yamareco_gpx, '-o', original_output]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"エラー: {result.stderr}")
        return False
    print(f"元のスクリプトの実行が完了しました。出力: {original_output}")
    return True

def run_improved_converter(formatted=False):
    """改良版スクリプトを実行"""
    output_file = improved_formatted_output if formatted else improved_output
    print(f"改良版スクリプト {improved_script} を実行中...")
    cmd = [
        sys.executable, 
        improved_script, 
        yamareco_gpx, 
        '-o', 
        output_file,
        '--activity-type', 
        'hiking',
        '--track-name', 
        '京都一周トレイル2泊3日'
    ]
    
    if formatted:
        cmd.append('--format-xml')
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"エラー: {result.stderr}")
        return False
    print(f"改良版スクリプトの実行が完了しました。出力: {output_file}")
    return True

def compare_files():
    """変換結果を比較"""
    print("変換結果を比較中...")
    
    # ファイルを読み込む
    with open(original_output, 'r', encoding='utf-8') as f:
        original_content = f.readlines()
    
    with open(improved_output, 'r', encoding='utf-8') as f:
        improved_content = f.readlines()
    
    # 差分を計算
    diff = difflib.HtmlDiff().make_file(
        original_content, 
        improved_content, 
        fromdesc="元のスクリプトの出力", 
        todesc="改良版スクリプトの出力"
    )
    
    # 差分をHTMLファイルに保存
    with open(diff_output, 'w', encoding='utf-8') as f:
        f.write(diff)
    
    print(f"差分ファイルを保存しました: {diff_output}")
    
    # 主な違いを分析
    analyze_differences()

def analyze_differences():
    """変換結果の主な違いを分析"""
    try:
        # XMLを解析
        original_tree = ET.parse(original_output)
        improved_tree = ET.parse(improved_output)
        formatted_tree = ET.parse(improved_formatted_output)
        
        original_root = original_tree.getroot()
        improved_root = improved_tree.getroot()
        formatted_root = formatted_tree.getroot()
        
        # 名前空間
        ns = {'gpx': 'http://www.topografix.com/GPX/1/1'}
        
        # 違いを分析
        print("\n=== 変換結果の主な違い ===")
        
        # 1. メタデータの有無
        improved_metadata = improved_root.find('.//gpx:metadata', ns)
        if improved_metadata is not None:
            print("✓ 改良版: メタデータセクションが追加されています")
            
            # メタデータの内容
            meta_time = improved_metadata.find('.//gpx:time', ns)
            if meta_time is not None:
                print(f"  - メタデータ時間: {meta_time.text}")
            
            # 拡張データ
            extensions = improved_metadata.find('.//gpx:extensions', ns)
            if extensions is not None:
                print("  - 元のサービス情報が保持されています")
        
        # 2. アクティビティタイプの有無
        improved_type = improved_root.find('.//gpx:trk/gpx:type', ns)
        if improved_type is not None:
            print(f"✓ 改良版: アクティビティタイプが追加されています: {improved_type.text}")
        
        # 3. トラック名の違い
        original_name = original_root.find('.//gpx:trk/gpx:name', ns)
        improved_name = improved_root.find('.//gpx:trk/gpx:name', ns)
        
        if original_name is not None and improved_name is not None:
            original_name_text = original_name.text if original_name.text else "".join(original_name.itertext())
            improved_name_text = improved_name.text if improved_name.text else "".join(improved_name.itertext())
            
            if original_name_text != improved_name_text:
                print(f"✓ トラック名の違い:")
                print(f"  - 元のスクリプト: {original_name_text}")
                print(f"  - 改良版スクリプト: {improved_name_text}")
        
        # 4. XMLフォーマットの違い
        with open(improved_output, 'r', encoding='utf-8') as f:
            improved_content = f.read()
        
        with open(improved_formatted_output, 'r', encoding='utf-8') as f:
            formatted_content = f.read()
        
        if improved_content != formatted_content:
            print("✓ 改良版: XMLフォーマットの整形オプションが機能しています")
            
            # 行数の違い
            improved_lines = improved_content.count('\n')
            formatted_lines = formatted_content.count('\n')
            print(f"  - 通常出力の行数: {improved_lines}")
            print(f"  - 整形出力の行数: {formatted_lines}")
        
        # 5. トラックポイントの数
        original_points = original_root.findall('.//gpx:trkpt', ns)
        improved_points = improved_root.findall('.//gpx:trkpt', ns)
        
        print(f"✓ トラックポイント数:")
        print(f"  - 元のスクリプト: {len(original_points)}")
        print(f"  - 改良版スクリプト: {len(improved_points)}")
        
        # 6. 座標精度の違い
        if len(original_points) > 0 and len(improved_points) > 0:
            original_lat = original_points[0].get('lat')
            improved_lat = improved_points[0].get('lat')
            
            print(f"✓ 座標精度の例:")
            print(f"  - 元のスクリプト: lat=\"{original_lat}\"")
            print(f"  - 改良版スクリプト: lat=\"{improved_lat}\"")
        
        # 7. 標高データの違い
        if len(original_points) > 0 and len(improved_points) > 0:
            original_ele = original_points[0].find('./gpx:ele', ns)
            improved_ele = improved_points[0].find('./gpx:ele', ns)
            
            if original_ele is not None and improved_ele is not None:
                print(f"✓ 標高データの例:")
                print(f"  - 元のスクリプト: {original_ele.text}")
                print(f"  - 改良版スクリプト: {improved_ele.text}")
        
        print("\n=== 変換結果の分析が完了しました ===")
        
    except Exception as e:
        print(f"分析中にエラーが発生しました: {e}")

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='改良版ヤマレコ→ランキーパー変換スクリプトのテスト')
    parser.add_argument('--skip-original', action='store_true', help='元のスクリプトの実行をスキップ')
    parser.add_argument('--skip-improved', action='store_true', help='改良版スクリプトの実行をスキップ')
    
    args = parser.parse_args()
    
    # 出力ディレクトリを作成
    ensure_dir(output_dir)
    
    # 元のスクリプトを実行
    if not args.skip_original:
        if not run_original_converter():
            print("元のスクリプトの実行に失敗しました。")
            return 1
    
    # 改良版スクリプトを実行（通常版と整形版）
    if not args.skip_improved:
        if not run_improved_converter(formatted=False):
            print("改良版スクリプト（通常版）の実行に失敗しました。")
            return 1
        
        if not run_improved_converter(formatted=True):
            print("改良版スクリプト（整形版）の実行に失敗しました。")
            return 1
    
    # 変換結果を比較
    compare_files()
    
    print("\nテストが完了しました。")
    print(f"元のスクリプトの出力: {original_output}")
    print(f"改良版スクリプトの出力（通常）: {improved_output}")
    print(f"改良版スクリプトの出力（整形）: {improved_formatted_output}")
    print(f"差分ファイル: {diff_output}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())