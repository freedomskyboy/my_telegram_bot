import os
import logging
import pandas as pd
from datetime import datetime
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# ------------------------- Config -------------------------
ADMIN_IDS = [123456789]  # Replace with your own Telegram user ID
DATA_DIR = 'data'
MEDIA_DIR = 'media'
EXPORTS_DIR = 'exports'
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MEDIA_DIR, exist_ok=True)
os.makedirs(EXPORTS_DIR, exist_ok=True)

# ------------------------- Logging -------------------------
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------------- Flask App -------------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "Telegram Work Tracking Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

# ------------------------- Helpers -------------------------
def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

def get_user_file(user_id: int) -> str:
    return os.path.join(DATA_DIR, f'user_{user_id}.csv')

def save_to_csv(user_id: int, row: dict):
    file_path = get_user_file(user_id)
    df = pd.DataFrame([row])
    if os.path.exists(file_path):
        df.to_csv(file_path, mode='a', header=False, index=False)
    else:
        df.to_csv(file_path, index=False)

# ------------------------- Handlers -------------------------
def start(update: Update, context: CallbackContext):
    update.message.reply_text('Work Tracking Bot activated! Send your work updates here.')

def get_id(update: Update, context: CallbackContext):
    update.message.reply_text(f"Your Telegram ID: {update.message.from_user.id}")

def handle_message(update: Update, context: CallbackContext):
    user = update.message.from_user
    timestamp = update.message.date

    entry = {
        'user_id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'timestamp': timestamp.isoformat(),
        'message_type': 'text',
        'content': update.message.text,
        'media_path': None
    }
    save_to_csv(user.id, entry)
    update.message.reply_text('Message logged successfully!')

def handle_photo(update: Update, context: CallbackContext):
    user = update.message.from_user
    timestamp = update.message.date
    photo_file = update.message.photo[-1].get_file()

    filename = f"photo_{user.id}_{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
    filepath = os.path.join(MEDIA_DIR, filename)
    photo_file.download(filepath)

    entry = {
        'user_id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'timestamp': timestamp.isoformat(),
        'message_type': 'photo',
        'content': update.message.caption or '',
        'media_path': filepath
    }
    save_to_csv(user.id, entry)
    update.message.reply_text('Photo logged successfully!')

def mydata(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    file_path = get_user_file(user_id)
    if not os.path.exists(file_path):
        update.message.reply_text("No data found.")
        return

    df = pd.read_csv(file_path)
    export_file = os.path.join(EXPORTS_DIR, f"mydata_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
    df.to_excel(export_file, index=False)

    with open(export_file, 'rb') as file:
        context.bot.send_document(chat_id=update.effective_chat.id, document=file, caption="Your data")

def stats(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    file_path = get_user_file(user_id)
    if not os.path.exists(file_path):
        update.message.reply_text("No data found.")
        return

    df = pd.read_csv(file_path)
    text_count = (df['message_type'] == 'text').sum()
    photo_count = (df['message_type'] == 'photo').sum()

    update.message.reply_text(
        f"Your messages:
Text: {text_count}
Photo: {photo_count}"
    )

def filter_data(update: Update, context: CallbackContext):
    try:
        user_id = update.message.from_user.id
        file_path = get_user_file(user_id)
        if not os.path.exists(file_path):
            update.message.reply_text("No data found.")
            return

        start_date = datetime.strptime(context.args[0], "%Y-%m-%d")
        end_date = datetime.strptime(context.args[1], "%Y-%m-%d")

        df = pd.read_csv(file_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        filtered = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]

        if filtered.empty:
            update.message.reply_text("No data found in this date range.")
            return

        export_file = os.path.join(EXPORTS_DIR, f"filter_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
        filtered.to_excel(export_file, index=False)

        with open(export_file, 'rb') as file:
            context.bot.send_document(chat_id=update.effective_chat.id, document=file, caption="Filtered data")
    except:
        update.message.reply_text("Usage: /filter YYYY-MM-DD YYYY-MM-DD")

def export_all(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if not is_admin(user_id):
        update.message.reply_text("Access denied. Admins only.")
        return

    all_files = [f for f in os.listdir(DATA_DIR) if f.startswith("user_")]
    all_dfs = [pd.read_csv(os.path.join(DATA_DIR, f)) for f in all_files if os.path.exists(os.path.join(DATA_DIR, f))]
    if not all_dfs:
        update.message.reply_text("No data found.")
        return

    df = pd.concat(all_dfs, ignore_index=True)
    export_file = os.path.join(EXPORTS_DIR, f"all_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
    df.to_excel(export_file, index=False)

    with open(export_file, 'rb') as file:
        context.bot.send_document(chat_id=update.effective_chat.id, document=file, caption="All user data")

def delete_all(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if not is_admin(user_id):
        update.message.reply_text("Access denied.")
        return

    for folder in [DATA_DIR, EXPORTS_DIR]:
        for f in os.listdir(folder):
            os.remove(os.path.join(folder, f))
    update.message.reply_text("All data deleted.")

# ------------------------- Main -------------------------
def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set")

    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("id", get_id))
    dp.add_handler(CommandHandler("mydata", mydata))
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_handler(CommandHandler("filter", filter_data))
    dp.add_handler(CommandHandler("export", export_all))
    dp.add_handler(CommandHandler("delete_all", delete_all))

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))

    Thread(target=run_flask, daemon=True).start()
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
