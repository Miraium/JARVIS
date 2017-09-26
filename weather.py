# -*- coding: utf-8 -*-

import sys
# jsonの処理用
import requests

from linebot.models import (
    CarouselTemplate, CarouselColumn, URITemplateAction, TemplateSendMessage
)

def getWeatherDataList():
    cityID_list = [
        "140010",
        "130010",
        "110010"
    ]

    root_url = "http://weather.livedoor.com/forecast/webservice/json/v1"
    urls = []
    for cityID in cityID_list:
        urls.append(root_url+"?city="+cityID)
    
    info_list = []
    for url in urls:
        r = requests.get(url)
        if r.status_code == 200:
            # json を取得
            j = r.json()

            # dict型のinfoを定義して，返り値となるlistに追加しておく
            # Carouselに追加する情報だけをjsonから抜き出してきている．
            info = {}
            info["link"] = j["link"]
            info["forecasts"] = j["forecasts"]
            info["loc_pref"] = j["location"]["prefecture"]
            info["loc_city"] = j["location"]["city"]
            info_list.append(info)
            # print(info)
            
    return info_list

def createCarouselTemplate(info_list):
    columns = []
    for info in info_list:
        weather_text = ""
        for forecast in info["forecasts"]:
            weather_text += "{0}: {1}\n".format(forecast["dateLabel"],forecast["telop"])
        
        carousel = CarouselColumn(
            # thumbnail_image_url="https://example.com/item2.jpg",
            title=info["loc_pref"]+" "+info["loc_city"],
            text=weather_text,
            actions=[
                    URITemplateAction(
                        label='Detail',
                        uri=info["link"]
                    )
            ]
            )
        columns.append(carousel)

    carousel_template_message = TemplateSendMessage(
        alt_text='Weather Information',
        template=CarouselTemplate(columns=columns)
    )
    return carousel_template_message


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