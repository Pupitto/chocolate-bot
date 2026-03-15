import os
import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
MAMA_CHAT_ID = 2115293517

app = Flask(__name__)
application = Application.builder().token(BOT_TOKEN).build()

# chat_id клиента -> последний кто писал (для ответов мамы)
active_clients = {}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    text = update.message.text

    # Если пишет мама - пересылаем последнему клиенту
    if chat_id == MAMA_CHAT_ID:
        if active_clients:
            last_client_id = list(active_clients.keys())[-1]
            await context.bot.send_message(
                chat_id=last_client_id,
                text=text
            )
        else:
            await update.message.reply_text("Нет активных клиентов.")
        return

    # Если пишет клиент - пересылаем маме
    active_clients[chat_id] = user.first_name
    username = f"@{user.username}" if user.username else "без username"
    
    await context.bot.send_message(
        chat_id=MAMA_CHAT_ID,
        text=f"👤 {user.first_name} ({username}):\n{text}"
    )
    await update.message.reply_text("Сообщение отправлено! Ожидайте ответа.")

application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.route(f"/webhook", methods=["POST"])
async def webhook():
    data = request.get_json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return "ok"

@app.route("/ping")
def ping():
    return "alive"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
