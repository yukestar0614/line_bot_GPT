from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import json
import os
import openai

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = "alNaHWLEDvELClh0JQEfiBYkZwLjQxayEzmLqnxNvIzktVzXGpnT4/Jo9nsBtUa6W0YpArRt4AYk5yJHWXU/v72lSHYNxAdjLnldxlDtx8gS4i3b+E7630rbtqt+rqxzTBD4RaQ0JuS7WSxEPWrTtwdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "04e925a01c1322776ea0cef2d254858b"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

OPENAI_API_KEY = "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"
openai.api_key = OPENAI_API_KEY

@app.route("/webhook", methods=['POST'])
def webhook():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

def ask_chatgpt(question):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"{question}",
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.8,
    )

    answer = response.choices[0].text.strip()
    return answer

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    user_text = event.message.text  # Get the text message sent by the user
    chatgpt_response = ask_chatgpt(user_text)  # Get a response from ChatGPT

    line_bot_api.reply_message(  # Send the ChatGPT response back to the user
        event.reply_token,
        TextSendMessage(text=chatgpt_response)
    )

if __name__ == "__main__":
    app.run(port=os.environ.get('PORT', 8080), debug=True)
