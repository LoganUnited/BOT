from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from config import ADMIN_IDS

def admin_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in ADMIN_IDS:
            await update.message.reply_text("❌ Команда только для админов!")
            return
        return await func(update, context)
    return wrapper

@admin_only
async def give_money_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = int(context.args[0])
        amount = int(context.args[1])
        await update.message.reply_text(f"✅ Игроку {user_id} выдано {amount} монет!")
    except (ValueError, IndexError):
        await update.message.reply_text("❌ Используйте: /give_money <user_id> <amount>")

admin_handlers = [
    CommandHandler("give_money", give_money_command)
]