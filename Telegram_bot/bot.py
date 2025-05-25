import os
from io import BytesIO
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

async def tip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tip_text = "Always water your plants early in the morning or late in the evening to reduce evaporation."
    await update.message.reply_text(tip_text)

async def funfact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fact_text = "Did you know? Cows have best friends and get stressed when separated!"
    await update.message.reply_text(fact_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🌱 *AgriBot Commands:*\n"
        "/tip - Get a useful farming tip\n"
        "/funfact - Learn a fun farming fact\n"
        "/help - Show this help message\n\n"
        "You can also send an image or ask any farming-related question\n\n"
        "Our bot supports the following languages: English, Swahili, Somali, Dholuo, Kikuyu, Kikamba, and Hindi"

    )
    await update.message.reply_text(help_text, parse_mode='Markdown')


# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Your Django backend URL
DJANGO_BACKEND_URL = os.getenv("DJANGO_BACKEND_URL")

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# /start command handler


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hello! Send me a text or an image, and I'll process it for you."
    )

# Text message handler


async def process_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text
    try:
        response = requests.post(DJANGO_BACKEND_URL, data={
                                 "user_input": user_text})
        if response.status_code == 200:
            data = response.json()
            final_output = data.get(
                "final_output", "Sorry, I didn't understand that.")
            await update.message.reply_text(final_output)
        else:
            await update.message.reply_text("Sorry, I couldn't process your request.")
    except Exception as e:
        logger.error(f"Error processing text: {e}")
        await update.message.reply_text("An error occurred while processing your request.")

# Image message handler


async def process_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text
    try:
        photo = update.message.photo[-1]
        file = await photo.get_file()
        image_bytes = await file.download_as_bytearray()

        files = {'image': ('image.jpg', BytesIO(image_bytes), 'image/jpeg')}
        api_response = requests.post(
            DJANGO_BACKEND_URL, files=files, data={"user_input": user_text, None: None})

        if api_response.status_code == 200:
            data = api_response.json()
            final_output = data.get(
                "final_output", "Image processed, but no response provided.")
            await update.message.reply_text(final_output)
        else:
            await update.message.reply_text("Failed to process the image.")
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        await update.message.reply_text("An error occurred while processing the image.")

# Bot main function


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, process_text))
    app.add_handler(MessageHandler(filters.PHOTO, process_image))
    app.add_handler(CommandHandler("tip", tip))
    app.add_handler(CommandHandler("funfact", funfact))     
    app.add_handler(CommandHandler("help", help_command))
    
    app.run_polling()


if __name__ == "__main__":
    main()
