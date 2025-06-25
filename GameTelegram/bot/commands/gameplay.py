import random
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from bot.commands.combat import start_combat
from utils.decorators import update_activity

@update_activity
async def explore_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    events = [
        "Вы нашли 10 монет! 💰",
        "Ничего интересного не произошло...",
        "Встретили дружелюбного торговца 🧔",
        "На вас напал разбойник! ⚔️"
    ]
    event = random.choice(events)
    
    if "напал" in event:
        return await start_combat(update, context)
    
    await update.message.reply_text(event)

gameplay_handlers = [
    CommandHandler("explore", explore_command)
]