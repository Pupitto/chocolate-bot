import os
import asyncio
import logging
from flask import Flask, request
from telegram import Bot

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
MAMA_CHAT_ID = 2115293517
active_clients = {}

app = Flask(__name__)

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

    bot = Bot(token=BOT_TOKEN)

    if chat_id == MAMA_CHAT_ID:
        if active_clients:
            last_client_id = list(active_clients.keys())[-1]
            asyncio.run(bot.send_message(chat_id=last_client_id, text=text))
        else:
            asyncio.run(bot.send_message(chat_id=MAMA_CHAT_ID, text="Нет активных клиентов."))
    else:
        active_clients[chat_id] = first_name
        asyncio.run(bot.send_message(
            chat_id=MAMA_CHAT_ID,
            text=f"👤 {first_name} ({username_str}):\n{text}"
        ))
        asyncio.run(bot.send_message(chat_id=chat_id, text="Сообщение отправлено! Ожидайте ответа."))

    return "ok"

@app.route("/ping")
def ping():
    return "alive"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
