# -*- coding: utf-8 -*-
"""
ぐるなびレストラン検索APIを使ったレストラン情報の提示用

API仕様
https://api.gnavi.co.jp/api/manual/restsearch/
"""

import os
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
# エンドポイントURL
rooturl = "https://api.gnavi.co.jp/RestSearchAPI/v3/"

class RestaurantInfo():
    def __init__(self):
        self.name = "No Title"
        self.shop_img = ""
        self.shop_url = ""
        self.text_pr = "No information"
        self.opentime = "Open :  - Close : "
        self.holiday = "-"
    
    def show(self):
        print("Name   : {0}".format(self.name))
        print("PR     : {0}".format(self.text_pr))
        print("Open   : {0}".format(self.opentime))
        print("Holiday: {0}".format(self.holiday))
        print("URL    : {0}".format(self.shop_url))

####
# 変数の型が文字列かどうかチェック
####
def is_str( data = None ) :
    if isinstance( data, str ) or isinstance( data, str ) :
        return True
    else :
        return False

def reply(bot,event,input_text):
    carousel_message = createCarouselTemplate(input_text)
    send_messages = [carousel_message]
    bot.reply_message(
        event.reply_token,
        send_messages
    )

def create_url_with_query(freeword, keyid=GNAVI_KEY):
    """
    APIアクセスのためのURL生成
    """
    # URLに続けて入れるパラメータを組立
    query = [
        ("keyid", keyid),
        ("freeword", freeword)
        # ("outret", 1) # 電源ありフラグ1
    ]
    # URL生成
    url = rooturl
    url += "?{0}".format(urllib.parse.urlencode(query))
    return url


def get_json_data(url):
    # API実行
    try :
        result = urllib.request.urlopen(url).read()
    except ValueError :
        print("APIアクセスに失敗しました。")
        sys.exit()

    ####
    # 取得した結果を解析
    ####
    data = json.loads( result )

    # エラーの場合
    if "error" in data :
        print("エラーです．")
        print(data)
        if "message" in data :
            print("エラーメッセージ")            
            print("{0}".format( data["message"] ))
        else :
            print("データ取得に失敗しました。")
            print("{0}".format(data["code"]))
        sys.exit()

    return data

def parse_restaurant_data(data):
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
    rest_info_list = []
    for rest in data["rest"] :
        rest_info = RestaurantInfo()
        

        # 店舗名の取得
        if "name" in rest and is_str( rest["name"] ) :
            rest_info.name = rest["name"]
        
        # 画像アドレスの取得(カルーセル取得用)
        if "image_url" in rest :
            image_url = rest["image_url"]
            if "shop_image1" in image_url and is_str(image_url["shop_image1"]):
                rest_info.shop_img = image_url["shop_image1"]

        # 店舗のURL
        if "url" in rest and is_str( rest["url"] ) :
            rest_info.shop_url = rest["url"]
        
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
            rest_info.text_pr = text_pr
        
        if "opentime" in rest:
            rest_info.opentime = rest["opentime"]
        
        if "holiday" in rest:
            rest_info.holiday = rest["holiday"]

        rest_info_list.append(rest_info)

        num_of_shop += 1
        if(num_of_shop >= MAX_SHOW):
            break
    
    return rest_info_list


def createCarouselTemplate(freeword):
    url = create_url_with_query(freeword)
    data = get_json_data(url)
    rest_info_list = parse_restaurant_data(data)

    columns = []
    for rest_info in rest_info_list:
        carousel = CarouselColumn(
            thumbnail_image_url=rest_info.shop_img,
            title=rest_info.name,
            # title = "aa",
            text=rest_info.text_pr,
            # text="bb",
            actions=[
                    URITemplateAction(
                        label='URL',
                        uri=rest_info.shop_url
                    )
            ]
            )
        columns.append(carousel)
    
    carousel_template_message = TemplateSendMessage(
        alt_text='Gurunavi',
        template=CarouselTemplate(columns=columns)
    )
    return carousel_template_message

def request_test():
    import settings
    keyid = settings.gnavi_key
    # freeword = "cafe".encode('utf-8')
    freeword = "自由が丘 cafe"
    url = create_url_with_query(freeword, keyid)
    data = get_json_data(url)
    rest_info_list = parse_restaurant_data(data)
    for rest_info in rest_info_list:
        rest_info.show()

if __name__ == "__main__":
    request_test()