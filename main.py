
import os
import logging
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackContext
import pandas as pd
from datetime import datetime

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TOKEN)

app = Flask(__name__)
dispatcher = Dispatcher(bot, None, workers=0)

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

def get_user_file(user_id): return os.path.join(DATA_DIR, f"user_{user_id}.csv")

def save_to_csv(user_id, row):
    path = get_user_file(user_id)
    df = pd.DataFrame([row])
    if os.path.exists(path):
        df.to_csv(path, mode="a", header=False, index=False)
    else:
        df.to_csv(path, index=False)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Bot is running. Send your work log.")

def handle_message(update: Update, context: CallbackContext):
    u = update.message.from_user
    row = {
        'user_id': u.id,
        'username': u.username,
        'first_name': u.first_name,
        'last_name': u.last_name,
        'timestamp': update.message.date.isoformat(),
        'message_type': 'text',
        'content': update.message.text,
        'media_path': None
    }
    save_to_csv(u.id, row)
    update.message.reply_text("Logged.")

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

@app.route('/')
def index():
    return "Webhook bot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

if __name__ == '__main__':
    app.run(port=int(os.environ.get("PORT", 10000)), host="0.0.0.0")
