import os

from fastapi import FastAPI, Request, BackgroundTasks, Header
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextSendMessage
from linebot.exceptions import InvalidSignatureError
from starlette.exceptions import HTTPException

from chatGPT_handler import ChatGPTHandler

load_dotenv(".env")

CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.environ.get("CHANNEL_SECRET")


app = FastAPI()
chatGPT = ChatGPTHandler()

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


@app.get("/")
def root():
    return {"Status": "Successful"}


@app.post("/callback")
async def callback(request: Request,
                   background_tasks: BackgroundTasks,
                   x_line_signature=Header(None)):
    body = await request.body()

    try:
        background_tasks.add_task(
                handler.handle, body.decode("utf-8"), x_line_signature
            )
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    return "ok"


@handler.add(MessageEvent)
def handle_message(event):
    if event.type != "message" or event.message.type != "text":
        return

    input_message = event.message.text

    line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=chatGPT.get_content_and_parse(input_message))
        )
