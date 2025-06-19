import logging
import os
from datetime import datetime

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

import dotenv
dotenv.load_dotenv()

BOT_TOKEN = os.getenv("8151783107:AAG_43d57lT33n8RYAnRppA0yejg9H4a7U8
")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

TEXT_LOG = "messages_log.txt"
IMAGE_DIR = "downloaded_images"
os.makedirs(IMAGE_DIR, exist_ok=True)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_entry = f"[{time}] {user.username or user.first_name}: {text}\n"
    with open(TEXT_LOG, "a", encoding="utf-8") as f:
        f.write(log_entry)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    photo = update.message.photo[-1]
    time_str = datetime.now().strftime("%Y%m%d_%H%M%S")

    file = await context.bot.get_file(photo.file_id)
    filename = f"{IMAGE_DIR}/{user.username or user.id}_{time_str}.jpg"
    await file.download_to_drive(filename)

    with open(TEXT_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{time_str}] {user.username or user.first_name}: зураг хүлээн авсан ({filename})\n")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Бот ажиллаж байна...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
