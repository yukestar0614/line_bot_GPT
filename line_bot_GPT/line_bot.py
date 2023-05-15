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
    print("Webhook triggered")  # Add this line
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

def ask_chatgpt(prompt):
    modified_prompt = f"アシスタント、次のメッセージに対して、ChatGPTちゃんとして、日本語で、役に立つまた関連性のある会話のレスポンスを提供してください。もし間違えを指摘されたら、しっかりと誤って訂正してください。: '{prompt}'。日本語で答えてください。"
    
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=modified_prompt,
        max_tokens=2048,
        n=1,
        stop=None,
        temperature=0.3,
    )
    message = response.choices[0].text.strip()
    return message

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    user_text = event.message.text
    print(f"Received message: {user_text}")

    try:
        chatgpt_response = ask_chatgpt(user_text)
    except openai.error.RateLimitError:
        chatgpt_response = "API rate limit exceeded. Please try again later."
    except Exception as e:
        print(f"Error: {e}")
        chatgpt_response = "An error occurred. Please try again later."

    print(f"Sending response: {chatgpt_response}")

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=chatgpt_response)
    )

if __name__ == "__main__":
    app.run(debug=True, port=8080)


