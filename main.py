from telegram.ext import Updater, MessageHandler, Filters
import logging
import os
from datetime import datetime

import dotenv
dotenv.load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TEXT_LOG = "messages_log.txt"
IMAGE_DIR = "downloaded_images"
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

def handle_text(update, context):
    user = update.message.from_user
    text = update.message.text
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_entry = f"[{time}] {user.username or user.first_name}: {text}\n"
    with open(TEXT_LOG, "a", encoding="utf-8") as f:
        f.write(log_entry)

def handle_photo(update, context):
    user = update.message.from_user
    photo = update.message.photo[-1]
    time = datetime.now().strftime("%Y%m%d_%H%M%S")

    file = context.bot.get_file(photo.file_id)
    filename = f"{IMAGE_DIR}/{user.username or user.id}_{time}.jpg"
    file.download(filename)

    with open(TEXT_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{time}] {user.username or user.first_name}: зураг хүлээн авсан ({filename})\n")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
