# coding: utf-8

import os
import sys
from linebot import (
    LineBotApi
)
# linebot用
from linebot.models import (
    TemplateSendMessage, ConfirmTemplate, MessageTemplateAction, PostbackTemplateAction
)

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
        confirm_template_message = TemplateSendMessage(
            alt_text='Confirm template',
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
        send_messages = [confirm_template_message]
        self.line_bot_api.push_message(my_user_id, send_messages)
        return True