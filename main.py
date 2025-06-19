import logging
import os
from datetime import datetime
from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters,
)
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN тодорхойгүй байна. .env файл эсвэл орчны хувьсагчийг шалгана уу.")

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Set log file and image directory
TEXT_LOG = "messages_log.txt"
IMAGE_DIR = "downloaded_images"
os.makedirs(IMAGE_DIR, exist_ok=True)

# Handle text messages
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{time}] {user.username or user.first_name}: {text}\n"
    with open(TEXT_LOG, "a", encoding="utf-8") as f:
        f.write(log_entry)

# Handle photo messages
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    photo = update.message.photo[-1]  # largest resolution
    time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    file = await context.bot.get_file(photo.file_id)
    filename = f"{IMAGE_DIR}/{user.username or user.id}_{time_str}.jpg"
    await file.download_to_drive(filename)
    with open(TEXT_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{time_str}] {user.username or user.first_name}: зураг хүлээн авсан ({filename})\n")

# Main function
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("✅ Telegram бот ажиллаж эхэллээ...")
    app.run_polling()

if __name__ == '__main__':
    main()
