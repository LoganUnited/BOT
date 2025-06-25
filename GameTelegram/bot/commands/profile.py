from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from game.core import game
from config import Config
from utils.logger import setup_logger

logger = setup_logger()

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать профиль игрока"""
    try:
        user = update.effective_user
        player = game.get_player(user.id)
        
        if not player:
            await update.message.reply_text("❌ Вы не зарегистрированы! Используйте /start")
            return
        
        # Формируем информацию о профиле
        profile_info = (
            f"👤 Профиль: {player.nickname}\n"
            f"🏅 Уровень: {player.level}\n"
            f"❤️ Здоровье: {player.health}/100\n"
            f"💰 Деньги: ${player.money:.2f}\n"
            f"📍 Локация: {player.location}\n"
            f"🚗 Транспорт: {player.transport}\n"
            f"⛽ Топливо: {player.fuel:.1f}%"
        )
        
        await update.message.reply_text(profile_info)
    
    except Exception as e:
        logger.error(f"Ошибка в profile_command: {str(e)}")
        await update.message.reply_text("⚠️ Произошла ошибка при загрузке профиля.")

async def move_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Перемещение между локациями"""
    try:
        user = update.effective_user
        player = game.get_player(user.id)
        
        if not player:
            await update.message.reply_text("❌ Вы не зарегистрированы! Используйте /start")
            return
        
        if not context.args:
            locations = "\n".join(Config.ALLOWED_LOCATIONS)
            await update.message.reply_text(
                f"❌ Укажите локацию после команды!\n\nДоступные локации:\n{locations}")
            return
        
        location = " ".join(context.args).upper()
        if location not in Config.ALLOWED_LOCATIONS:
            await update.message.reply_text("❌ Недопустимая локация!")
            return
        
        if game.move_player(user.id, location):
            await update.message.reply_text(f"✅ Вы переместились в {location}!")
        else:
            await update.message.reply_text("❌ Ошибка перемещения!")
    
    except Exception as e:
        logger.error(f"Ошибка в move_command: {str(e)}")
        await update.message.reply_text("⚠️ Произошла ошибка при перемещении.")

async def back_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Вернуться из AFK"""
    try:
        user = update.effective_user
        player = game.get_player(user.id)
        
        if not player:
            await update.message.reply_text("❌ Вы не зарегистрированы! Используйте /start")
            return
        
        if game.db.set_afk_status(user.id, False):
            await update.message.reply_text("✅ Вы вернулись в игру!")
        else:
            await update.message.reply_text("❌ Вы и так активны!")
    
    except Exception as e:
        logger.error(f"Ошибка в back_command: {str(e)}")
        await update.message.reply_text("⚠️ Произошла ошибка при возвращении в игру.")

def get_profile_handlers():
    """Возвращает обработчики команд профиля"""
    return [
        CommandHandler("profile", profile_command),
        CommandHandler("move", move_command),
        CommandHandler("back", back_command)
    ]