from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

async def shop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛒 Магазин:\n"
        "1. Зелье здоровья - 30💰\n"
        "2. Меч воина - 150💰\n"
        "3. Кожаный доспех - 100💰")

economy_handlers = [
    CommandHandler("shop", shop_command)
]