from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import urllib.request
import json
import os

app = Flask(__name__)

YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():

    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    # API
    target_url = 'https://jlp.yahooapis.jp/KouseiService/V2/kousei'
    app_id = os.environ["APPID"]
    user_text = event.message.text

    # ユーザー情報取得
    user_id = profile.user_id

    # 校閲処理
    def post(query):
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Yahoo AppID: {}".format(app_id),
        }
        data = {
            "id": app_id,
            "jsonrpc" : "2.0",
            "method": "jlp.kouseiservice.kousei",
            "params" : {
                "q": query
            }
        }
        params = json.dumps(data).encode()
        req = urllib.request.Request(target_url, params, headers)

        with urllib.request.urlopen(req) as res:
            body = res.read()
        return body.decode()

    responses = post(user_text)
    ev_responses = eval(responses)
    response_data = ev_responses['result']['suggestions']

    # 複数を校正する
    if response_data == []:
        print("校正する箇所はありません")
    else:
        for response_text in response_data:
            return response_text['suggestion']
            # line_bot_api.push_message(user_id, messages=text)
            # return responses_text = response_text['suggestion']

    # messages = TextSendMessage(text=post(user_text))

    # line_bot_api.push_message(user_id, messages=messages)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=post(user_text)))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)