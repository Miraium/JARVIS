# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

import os
import sys
from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, StickerMessage, StickerSendMessage, PostbackEvent, PostbackTemplateAction, Postback
)

import weather,gurunavi
from ac_control import ACControl

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

mode = "Default"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'
@app.route("/ifttt", methods=['POST'])
def callback_ifttt():
    body = request.get_data(as_text=True)
    app.logger.info("IFTTT test")
    app.logger.info("Request body: " + body)
    ac_cont = ACControl()
    ac_cont.push_confirm()
    return 'OK'

def reactArguments(bot, event):
    global mode
    input_text = event.message.text
    
    if mode == "Gnavi":
        # carousel_message = gurunavi.createCarouselTemplate(input_text)
        # send_messages = [carousel_message]
        # bot.reply_message(
        #     event.reply_token,
        #     send_messages
        # )
        gurunavi.reply(bot,event,input_text)
    # 処理が終わったらモードを戻す
    mode = "Default"


@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    # 入力されたテキストを取り出す
    input_text = event.message.text

    # モードがデフォルトモードじゃない場合は，モードに応じた特別な処理を行って終了?
    # -->引数を受け付けるモードの場合は，特別な処理を行って終了
    global mode
    if (mode == "Gnavi") :
        reactArguments(line_bot_api,event)
        return

    # 現在Defaultモードの場合で，
    # テキストに応じてモードを切り替える
    if (input_text=="天気"):
        mode = "Weather"
    elif(input_text=="食事" or input_text=="ご飯"):
        mode = "Gnavi"
    else:
        mode = "Default"

    # Defaultモードから各モードに切り替わったときの処理
    if (mode=="Weather"):
        text_message = TextSendMessage(text="天気情報を表示します。")
        weather_info = weather.getWeatherDataList()
        carousel_message = weather.createCarouselTemplate(weather_info)
        send_messages = [text_message, carousel_message]
        line_bot_api.reply_message(
            event.reply_token,
            send_messages
        )
    elif (mode=="Gnavi"):
        text_message = TextSendMessage(text="どう検索しますか?")
        send_messages = [text_message]        
        line_bot_api.reply_message(
            event.reply_token,
            send_messages
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text+"ですね。")
        )

@handler.add(MessageEvent, message=StickerMessage)
def message_sticker(event):
    name = line_bot_api.get_profile(event.source.user_id).display_name
    line_bot_api.reply_message(
        event.reply_token,
        [TextSendMessage(text="なるほど、スタンプですか。考えましたね、"+name+"さん。"),StickerSendMessage(package_id=4,sticker_id=296)]
    )

@handler.add(PostbackEvent)
def reply_to_postback(event):
    messages = []
    if event.postback.data == "good":
        messages.append(TextSendMessage(text="それはよかったですね。引き続きその調子で！"))
    elif event.postback.data == "bad":
        messages.append(TextSendMessage(text="そうですか。。少しおやすみになっては?"))
    line_bot_api.reply_message(event.reply_token, messages)

@handler.add(PostbackEvent)
def reply_to_postback(event):
    messages = []
    if event.postback.data == "ac_on_approval":
        messages.append(TextSendMessage(text="承知いたしました。つけておきます。"))
    elif event.postback.data == "ac_on_disapproval":
        messages.append(TextSendMessage(text="そうですか。そのままにしておきます。"))
    line_bot_api.reply_message(event.reply_token, messages)

if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    # app.run(debug=options.debug, port=options.port)
    app.run(debug=True, port=options.port)