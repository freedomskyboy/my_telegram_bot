
import os
import logging
import pandas as pd
from datetime import datetime
from flask import Flask, send_from_directory
from threading import Thread
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

ADMIN_IDS = [7956726015]
DATA_DIR = 'data'
MEDIA_DIR = 'media'
EXPORTS_DIR = 'exports'
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MEDIA_DIR, exist_ok=True)
os.makedirs(EXPORTS_DIR, exist_ok=True)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running! Use /dashboard to view stats."

@app.route('/dashboard')
def dashboard():
    all_data = []
    for file in os.listdir(DATA_DIR):
        if file.endswith(".csv"):
            df = pd.read_csv(os.path.join(DATA_DIR, file))
            all_data.append(df)
    if not all_data:
        return "📂 No data available."

    df_all = pd.concat(all_data)
    total_users = df_all['user_id'].nunique()
    total_messages = len(df_all)
    message_types = df_all['message_type'].value_counts().to_dict()
    user_stats = df_all.groupby("username")["message_type"].value_counts().unstack(fill_value=0)
    user_stats["total"] = user_stats.sum(axis=1)
    top_users = user_stats.sort_values("total", ascending=False).head(5).to_dict(orient="index")

    html = f"<h1>📊 Dashboard</h1><p>👤 Users: {total_users}</p><p>✉️ Messages: {total_messages}</p><ul>"
    for user, stats in top_users.items():
        html += f"<li><b>{user}</b>: {stats.get('text', 0)} text, {stats.get('photo', 0)} photo</li>"
    html += "</ul>"
    html += '<br><a href="/export_dashboard"><button>📥 Export to Excel</button></a>'
    return html

@app.route('/export_dashboard')
def export_dashboard():
    all_data = []
    for file in os.listdir(DATA_DIR):
        if file.endswith(".csv"):
            df = pd.read_csv(os.path.join(DATA_DIR, file))
            all_data.append(df)
    if not all_data:
        return "No data to export."
    df_all = pd.concat(all_data, ignore_index=True)
    export_path = os.path.join(EXPORTS_DIR, f"dashboard_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
    df_all.to_excel(export_path, index=False)
    return f'<p>✅ Exported. <a href="/download/{os.path.basename(export_path)}">Download Excel</a></p>'

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(EXPORTS_DIR, filename, as_attachment=True)

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

def is_admin(user_id): return user_id in ADMIN_IDS
def get_user_file(user_id): return os.path.join(DATA_DIR, f'user_{user_id}.csv')

def save_to_csv(user_id, row):
    path = get_user_file(user_id)
    df = pd.DataFrame([row])
    if os.path.exists(path):
        df.to_csv(path, mode='a', header=False, index=False)
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

def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN not set")
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    Thread(target=run_flask, daemon=True).start()
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
