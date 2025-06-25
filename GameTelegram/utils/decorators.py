from telegram import Update
from telegram.ext import ContextTypes  # Добавлен импорт ContextTypes
from database.manager import DatabaseManager
import logging


logger = logging.getLogger(__name__)
db = DatabaseManager()

def update_activity(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        try:
            user_id = update.effective_user.id
            
            # Обновляем активность
            if not db.update_activity(user_id):
                logger.warning(f"Не удалось обновить активность для {user_id}")
            
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            logger.error(f"Ошибка в декораторе активности: {str(e)}")
            return await func(update, context, *args, **kwargs)
    return wrapper