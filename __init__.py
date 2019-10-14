"""
__init__.py serves the application, and also tell Python that this directory should be treated as a package

Flask routing default for 'GET', import request can further identify 'GET" or 'POST'
"""
import os
import re
from flask import Flask, request

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

import my_firebase
import sbrain
import my_pattern

app = Flask(__name__)

#Original: chartermonkey.herokuapp.com/callback
line_bot_api = LineBotApi(os.environ.get('CHANNEL_TOKEN'))
handler = WebhookHandler(os.environ.get('CHANNEL_SECRET'))


@app.route('/')
def hello_silverback():
    return 'Hi I\'m Silverback!'


"""
INPUT
    date_code for example: 20191006
OUTPUT
    A dictionary, contains field data of date_code document
"""
@app.route('/list/<string:date_code>')
def playlist(date_code):
    return my_firebase.read_doc(date_code)


"""
join() checks existing date but don't check existing count for players,
if someone repeatedly changing his/her mind, the latest record is served.
"""
@app.route('/join/<string:date_code>/<string:attn_name>/<int:count>')
def join(date_code, attn_name, count):
    return sbrain.join(date_code,attn_name,count)

@app.route('/deduct/<string:date_code>/<string:attn_name>/<int:count>')
def deduct(date_code, attn_name, count):
    return sbrain.deduct(date_code,attn_name,count)


"""
LINE bot app handling: callback()  handle_message()
"""
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
    except InvalidSignatureError as e:
        print("Invalid signature. Might be channel access token/secret issue.")
        print("InvalidSignatureError error: {0}".format(e))
        abort(400)

    return 'OK'


def chitchat(message):
    if message == "恰特猴":
        return "幹嘛~"
    elif message == "list":
        return "不給你看～嘻嘻"
    else:
        return ""

"""
Message format check
"""
def is_chitchat(message):
    if (re.search(my_pattern.date, message)) or (re.search(my_pattern.week, message)) or (re.search(my_pattern.quick, message)):
        return False
    else:
        return True


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    reply_message = ""
    profile = line_bot_api.get_profile(event.source.user_id)

    """
    Checking for meaningful message, ignore message if is_chitchat == True
    """
    if is_chitchat(event.message.text) == True:
        reply_message = chitchat(event.message.text)
    else:
        reply_message = sbrain.reply(event.message.text, profile.display_name) #event.source.user_id
        # reply_message = "in development..."

    try:
        line_bot_api.reply_message(
            event.reply_token,
            # TextSendMessage(text=event.message.text))
            TextSendMessage(text=reply_message))
    except LineBotApiError as e:
        print("LineBotApiError error: {0}".format(e))
        TextSendMessage(text="UH...Something went wrong now...")


"""
Run Flask app
"""
app.run()