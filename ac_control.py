# coding: utf-8

import os
import sys
from linebot import (
    LineBotApi
)
# linebot用
from linebot.models import (
    TextSendMessage, TemplateSendMessage, ConfirmTemplate, MessageTemplateAction, PostbackTemplateAction
)
import thingspeak_read

channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
my_user_id = os.getenv('MY_USER_ID', None)

if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)
if my_user_id is None:
    print('Specify MY_USER_ID as environment variable.')
    sys.exit(1)


class ACControl(object):
    def __init__(self):
        self.line_bot_api = LineBotApi(channel_access_token)
    
    def push_confirm(self):
        environment_information = self.get_environment()
        information_message = TextSendMessage(environment_information)
        confirm_template_message = TemplateSendMessage(
            alt_text='エアコンつけておきますか?',
            template=ConfirmTemplate(
                text='エアコンつけておきますか?',
                actions=[
                    PostbackTemplateAction(
                        label='承認',
                        text='承認',
                        data='ac_on_approval'
                    ), 
                    PostbackTemplateAction(
                        label='否認',
                        text='否認',
                        data='ac_on_disapproval'
                    )
                ]
            )
        )
        send_messages = [information_message, confirm_template_message]
        self.line_bot_api.push_message(my_user_id, send_messages)
        return True

    def get_environment(self):
        sensor_output_text = """
        温度: {temperature}度
        湿度: {humidity}%
        気圧: {pressure}hPa
        ({time}時点での情報)
        """
        fields = thingspeak_read.get_environment_field()
        sensor_output_text = sensor_output_text.format(
            temperature=fields.get("temperature"),
            humidity=fields.get("humidity"),
            pressure=fields.get("pressure"),
            time=fields.get("time")
            )
        return sensor_output_text