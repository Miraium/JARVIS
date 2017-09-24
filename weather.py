# -*- coding: utf-8 -*-

import sys
# jsonの処理用
import requests

def getWeatherData():
    # 横浜の天気を取得する(livedoor webapiを使用)
    # cityID: 140010
    # cityID:1413000 (川崎?) APIでは呼び出せないぽい
    # http://weather.livedoor.com/forecast/webservice/json/v1

    # Ref. http://www.lifewithpython.com/2015/07/handling-json-web-api.html
    url = "http://weather.livedoor.com/forecast/webservice/json/v1?city=140010"
    r = requests.get(url)
    # 無事レスポンスが返ってきたら中身を出力
    if r.status_code == 200:
        # json を取得
        j = r.json()

        # キーを表示(取得したjsonオブジェクトは辞書型)
        keys = j.keys() 
        print(keys)

        # 各エントリのタイトルを一覧で表示
        for k in keys:
            entry = j[k]
            print(k)
            print(entry)
        
        description = j["description"]["text"]
        loc_list = j["pinpointLocations"]
        for loc_info in loc_list:
            # loc_infoはdict型の情報(linkとnameを保持)
            if loc_info["name"] == "川崎市":
                link = loc_info["link"]
                break
            else:
                link = "None."

        print("=======================")
        print(description)
        print(link)
    return description,link