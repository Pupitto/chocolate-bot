import os
import logging
import asyncio
from flask import Flask, request
import telegram

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
MAMA_CHAT_ID = 2115293517

app = Flask(__name__)
active_clients = {}

async def send_message(chat_id, text):
    bot = telegram.Bot(token=BOT_TOKEN)
    async with bot:
        await bot.send_message(chat_id=chat_id, text=text)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if not data or "message" not in data:
        return "ok"
    
    message = data["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "")
    user = message.get("from", {})
    first_name = user.get("first_name", "Клиент")
    username = user.get("username", "")
    username_str = f"@{username}" if username else "без username"

    if chat_id == MAMA_CHAT_ID:
        if active_clients:
            last_client_id = list(active_clients.keys())[-1]
            asyncio.run(send_message(last_client_id, text))
        else:
            asyncio.run(send_message(MAMA_CHAT_ID, "Нет активных клиентов."))
    else:
        active_clients[chat_id] = first_name
        asyncio.run(send_message(
            MAMA_CHAT_ID,
            f"👤 {first_name} ({username_str}):\n{text}"
        ))
        asyncio.run
