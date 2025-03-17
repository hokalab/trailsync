#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GPXパーサーのテスト
"""

import os
import sys
import unittest
from datetime import datetime
from pathlib import Path

# テスト対象のモジュールをインポート
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.universal_gpx_converter.parser import GPXParser

class TestGPXParser(unittest.TestCase):
    """GPXパーサーのテストクラス"""

    def setUp(self):
        """テスト前の準備"""
        self.parser = GPXParser()
        
        # テスト用のGPXファイルパス
        self.test_dir = Path(__file__).parent / "test_data"
        self.test_dir.mkdir(exist_ok=True)
        
        # テスト用のGPXファイルが存在しない場合は作成
        self.runkeeper_gpx = self.test_dir / "runkeeper_test.gpx"
        self.yamareco_gpx = self.test_dir / "yamareco_test.gpx"
        self.strava_gpx = self.test_dir / "strava_test.gpx"
        
        self._create_test_files()

    def _create_test_files(self):
        """テスト用のGPXファイルを作成"""
        # Runkeeper形式のGPXファイル
        if not self.runkeeper_gpx.exists():
            with open(self.runkeeper_gpx, "w", encoding="utf-8") as f:
                f.write("""<?xml version="1.0" encoding="UTF-8"?>
<gpx
  version="1.1"
  creator="Runkeeper - http://www.runkeeper.com"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns="http://www.topografix.com/GPX/1/1"
  xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd"
  xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1">
<trk>
  <name><![CDATA[Hiking 31/1/25 8:32 am]]></name>
  <time>2025-01-30T23:32:36Z</time>
<trkseg>
<trkpt lat="34.932940000" lon="135.765692000"><ele>35.2</ele><time>2025-01-30T23:32:36Z</time></trkpt>
<trkpt lat="34.933004000" lon="135.766165000"><ele>35.4</ele><time>2025-01-30T23:33:29Z</time></trkpt>
</trkseg>
</trk>
</gpx>""")
        
        # ヤマレコ形式のGPXファイル
        if not self.yamareco_gpx.exists():
            with open(self.yamareco_gpx, "w", encoding="utf-8") as f:
                f.write("""<?xml version="1.0" encoding="UTF-8"?>
<gpx xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.topografix.com/GPX/1/1" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd" creator="Yamareco iOS 7.22 - www.yamareco.com">
<trk><name>track</name><number>1</number><trkseg>
<trkpt lat="34.93293983529206" lon="135.76569236945932"><ele>30</ele><time>2025-01-30T23:32:36Z</time></trkpt>
<trkpt lat="34.933004458708005" lon="135.76616544961826"><ele>31</ele><time>2025-01-30T23:33:29Z</time></trkpt>
</trkseg>
</trk>
</gpx>""")
        
        # Strava形式のGPXファイル
        if not self.strava_gpx.exists():
            with open(self.strava_gpx, "w", encoding="utf-8") as f:
                f.write("""<?xml version="1.0" encoding="UTF-8"?>
<gpx xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd" creator="StravaGPX" version="1.1" xmlns="http://www.topografix.com/GPX/1/1">
 <metadata>
  <time>2025-01-30T23:32:36Z</time>
 </metadata>
 <trk>
  <name>京都一周トレイル</name>
  <type>hiking</type>
  <trkseg>
   <trkpt lat="34.9329400" lon="135.7656920">
    <ele>30.4</ele>
    <time>2025-01-30T23:32:36Z</time>
   </trkpt>
   <trkpt lat="34.9330040" lon="135.7661650">
    <ele>32.0</ele>
    <time>2025-01-30T23:33:29Z</time>
   </trkpt>
  </trkseg>
 </trk>
</gpx>""")

    def test_parse_runkeeper_file(self):
        """Runkeeper形式のGPXファイルを解析するテスト"""
        gpx_data = self.parser.parse_file(str(self.runkeeper_gpx))
        
        self.assertIsNotNone(gpx_data)
        self.assertEqual(gpx_data['creator'], 'Runkeeper - http://www.runkeeper.com')
        self.assertEqual(len(gpx_data['tracks']), 1)
        self.assertEqual(gpx_data['tracks'][0]['name'], 'Hiking 31/1/25 8:32 am')
        self.assertEqual(gpx_data['tracks'][0]['time'], '2025-01-30T23:32:36Z')
        self.assertEqual(len(gpx_data['tracks'][0]['points']), 2)
        self.assertEqual(gpx_data['tracks'][0]['points'][0]['lat'], '34.932940000')
        self.assertEqual(gpx_data['tracks'][0]['points'][0]['lon'], '135.765692000')
        self.assertEqual(gpx_data['tracks'][0]['points'][0]['ele'], '35.2')
        self.assertEqual(gpx_data['tracks'][0]['points'][0]['time'], '2025-01-30T23:32:36Z')

    def test_parse_yamareco_file(self):
        """ヤマレコ形式のGPXファイルを解析するテスト"""
        gpx_data = self.parser.parse_file(str(self.yamareco_gpx))
        
        self.assertIsNotNone(gpx_data)
        self.assertEqual(gpx_data['creator'], 'Yamareco iOS 7.22 - www.yamareco.com')
        self.assertEqual(len(gpx_data['tracks']), 1)
        self.assertEqual(gpx_data['tracks'][0]['name'], 'track')
        self.assertEqual(gpx_data['tracks'][0]['number'], '1')
        self.assertEqual(len(gpx_data['tracks'][0]['points']), 2)
        self.assertEqual(gpx_data['tracks'][0]['points'][0]['lat'], '34.93293983529206')
        self.assertEqual(gpx_data['tracks'][0]['points'][0]['lon'], '135.76569236945932')
        self.assertEqual(gpx_data['tracks'][0]['points'][0]['ele'], '30')
        self.assertEqual(gpx_data['tracks'][0]['points'][0]['time'], '2025-01-30T23:32:36Z')

    def test_parse_strava_file(self):
        """Strava形式のGPXファイルを解析するテスト"""
        gpx_data = self.parser.parse_file(str(self.strava_gpx))
        
        self.assertIsNotNone(gpx_data)
        self.assertEqual(gpx_data['creator'], 'StravaGPX')
        self.assertEqual(len(gpx_data['tracks']), 1)
        self.assertEqual(gpx_data['tracks'][0]['name'], '京都一周トレイル')
        self.assertEqual(gpx_data['tracks'][0]['type'], 'hiking')
        self.assertEqual(len(gpx_data['tracks'][0]['points']), 2)
        self.assertEqual(gpx_data['tracks'][0]['points'][0]['lat'], '34.9329400')
        self.assertEqual(gpx_data['tracks'][0]['points'][0]['lon'], '135.7656920')
        self.assertEqual(gpx_data['tracks'][0]['points'][0]['ele'], '30.4')
        self.assertEqual(gpx_data['tracks'][0]['points'][0]['time'], '2025-01-30T23:32:36Z')
        self.assertEqual(gpx_data['metadata']['time'], '2025-01-30T23:32:36Z')

    def test_detect_service(self):
        """サービスを検出するテスト"""
        runkeeper_data = self.parser.parse_file(str(self.runkeeper_gpx))
        yamareco_data = self.parser.parse_file(str(self.yamareco_gpx))
        strava_data = self.parser.parse_file(str(self.strava_gpx))
        
        self.assertEqual(self.parser.detect_service(runkeeper_data), 'runkeeper')
        self.assertEqual(self.parser.detect_service(yamareco_data), 'yamareco')
        self.assertEqual(self.parser.detect_service(strava_data), 'strava')

if __name__ == '__main__':
    unittest.main()