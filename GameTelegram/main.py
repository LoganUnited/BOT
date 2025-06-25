import asyncio
import sys
from config import Config
from bot.handlers import HandlersManager
from game.tasks import TaskManager
from utils.logger import setup_logger
from telegram.ext import ApplicationBuilder

logger = setup_logger()

class BotApplication:
    def __init__(self):
        self.app = None
        self.task_manager = TaskManager()
        self.handlers_manager = HandlersManager()

    async def start(self):
        """Запуск бота"""
        try:
            logger.info("Инициализация бота...")
            
            self.app = ApplicationBuilder().token(Config.BOT_TOKEN).build()
            self.app.add_handlers(self.handlers_manager.get_all_handlers())
            
            # Запуск фоновой задачи через JobQueue
            self.app.job_queue.run_repeating(
                self.task_manager.auto_afk_and_income_task,
                interval=3600,
                first=10
            )
            
            logger.info("✅ Бот успешно инициализирован")
            return self.app
        
        except Exception as e:
            logger.error(f"Ошибка инициализации: {e}")
            raise

async def run_bot():
    """Основная функция запуска"""
    bot_app = BotApplication()
    app = await bot_app.start()
    
    try:
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        logger.info("Бот запущен и работает")
        await asyncio.get_event_loop().create_future()  # Бесконечное ожидание
        
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("Получен сигнал остановки")
    except Exception as e:
        logger.error(f"Ошибка в работе бота: {e}")
    finally:
        await shutdown(app)

async def shutdown(app):
    """Корректное завершение работы"""
    try:
        logger.info("Остановка бота...")
        if app.updater.running:
            await app.updater.stop()
        await app.stop()
        await app.shutdown()
        logger.info("Бот успешно остановлен")
    except Exception as e:
        logger.error(f"Ошибка при остановке: {e}")

if __name__ == "__main__":
    # Настройка event loop для Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        asyncio.run(run_bot())
    except Exception as e:
        logger.error(f"Фатальная ошибка: {e}")
    finally:
        logger.info("Приложение завершено")