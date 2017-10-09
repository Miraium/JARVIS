# -*- coding: utf-8 -*-

import sys
# jsonの処理用
import requests
import urllib.request, urllib.parse, urllib.error
import json


from linebot.models import (
    CarouselTemplate, CarouselColumn, URITemplateAction, TemplateSendMessage
)

# import settings
# GNAVI_KEY = settings.gnavi_key
GNAVI_KEY = os.getenv('GURUNAVI_KEY', None)
MAX_SHOW = 5
MAX_TEXT = 60

# APIアクセスキー
keyid     = GNAVI_KEY
# エンドポイントURL
rooturl       = "https://api.gnavi.co.jp/RestSearchAPI/20150630/"

####
# 変数の型が文字列かどうかチェック
####
def is_str( data = None ) :
    if isinstance( data, str ) or isinstance( data, str ) :
        return True
    else :
        return False


def createURLwithQuery(freeword):
    ####
    # APIアクセス
    ####
    # URLに続けて入れるパラメータを組立
    query = [
    ( "format",    "json"    ),
    ( "keyid",     keyid     ),
    # ( "latitude",  latitude  ),
    # ( "longitude", longitude ),
    # ( "range",     range     )
    ("freeword", "池袋,カレー")
    ]
    # URL生成
    url = rooturl
    url += "?{0}".format( urllib.parse.urlencode( query ) )
    
    return url


def getJsonData(url):
    # API実行
    try :
        result = urllib.request.urlopen( url ).read()
    except ValueError :
        print("APIアクセスに失敗しました。")
        sys.exit()

    ####
    # 取得した結果を解析
    ####
    data = json.loads( result )

    # エラーの場合
    if "error" in data :
        if "message" in data :
            print("{0}".format( data["message"] ))
        else :
            print("データ取得に失敗しました。")
        sys.exit()

    return data

def parseRestaurantData(data):
    # ヒット件数取得
    total_hit_count = None
    if "total_hit_count" in data :
        total_hit_count = data["total_hit_count"]
    
    # レストランデータがなかったら終了
    if not "rest" in data :
        print("レストランデータが見つからなかったため終了します。")
        sys.exit()
    
    # レストランデータ取得
    num_of_shop = 0
    info_list = []
    for rest in data["rest"] :
        name = "No Title"
        shop_img = ""
        shop_url = ""
        text_pr = "No information"
        
        info = {}

        # 店舗名の取得
        if "name" in rest and is_str( rest["name"] ) :
            name = rest["name"]
        
        # 画像アドレスの取得(カルーセル取得用)
        if "image_url" in rest :
            image_url = rest["image_url"]
            if "shop_image1" in image_url and is_str( image_url["shop_image1"] ) :
                shop_img = image_url["shop_image1"]

        # 店舗のURL
        if "url" in rest and is_str( rest["url"] ) :
            shop_url = rest["url"]
        
        # PR文章
        if "pr" in rest: 
            pr = rest["pr"]
            if "pr_short" in pr and is_str( pr["pr_short"] ) :
                if pr["pr_short"] != "":
                    text_pr = pr["pr_short"]
                    if len(pr["pr_short"]) > MAX_TEXT:
                        text_pr = text_pr[0:MAX_TEXT]
                else:
                    text_pr = "No Information"

        info["name"] = name
        info["shop_img"] = shop_img
        info["shop_url"] = shop_url
        info["text_pr"] = text_pr

        info_list.append(info)

        num_of_shop += 1
        if(num_of_shop >= MAX_SHOW):
            break
    
    return info_list


def createCarouselTemplate(freeword):
    url = createURLwithQuery(freeword)
    data = getJsonData(url)
    info_list = parseRestaurantData(data)

    columns = []
    for info in info_list:
        carousel = CarouselColumn(
            thumbnail_image_url=info["shop_img"],
            title=info["name"],
            # title = "aa",
            text=info["text_pr"],
            # text="bb",
            actions=[
                    URITemplateAction(
                        label='URL',
                        uri=info["shop_url"]
                    )
            ]
            )
        columns.append(carousel)
    
    carousel_template_message = TemplateSendMessage(
        alt_text='Gurunavi',
        template=CarouselTemplate(columns=columns)
    )
    return carousel_template_message

