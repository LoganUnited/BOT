import asyncio
from datetime import datetime
from utils.logger import setup_logger
from database.manager import DatabaseManager
from config import Config
from telegram import Bot
from telegram.error import TelegramError

logger = setup_logger()
db = DatabaseManager()

class TaskManager:
    def __init__(self):
        self.bot = Bot(token=Config.BOT_TOKEN)
        self.is_running = False

    async def auto_afk_and_income_task(self, context):
        """Фоновая задача для обработки AFK статуса и начисления дохода"""
        if self.is_running:
            logger.warning("Задача уже запущена")
            return

        self.is_running = True
        logger.info("Задача auto_afk_and_income_task запущена")

        try:
            while self.is_running:
                try:
                    await self._process_players()
                except Exception as e:
                    logger.error(f"Ошибка обработки игроков: {str(e)}")
                finally:
                    await asyncio.sleep(3600)  # Пауза 1 час между проверками
        except asyncio.CancelledError:
            logger.info("Задача отменена")
        finally:
            self.is_running = False

    async def _process_players(self):
        """Основная логика обработки игроков"""
        with db.conn.cursor() as cursor:
            cursor.execute("""
                SELECT user_id, level, last_active, is_afk 
                FROM players
                WHERE last_active IS NOT NULL
            """)
            players = cursor.fetchall()
            
            now = datetime.now()
            processed = 0
            afk_count = 0
            income_count = 0

            for user_id, level, last_active_str, is_afk in players:
                try:
                    processed += 1
                    last_active = datetime.strptime(last_active_str, "%Y-%m-%d %H:%M:%S")
                    hours_inactive = (now - last_active).total_seconds() / 3600

                    # Обработка AFK статуса
                    if hours_inactive >= 24:
                        if not is_afk:
                            await self._handle_afk(user_id)
                            afk_count += 1
                        continue

                    # Начисление дохода активным игрокам
                    if not is_afk:
                        await self._handle_income(user_id, level)
                        income_count += 1

                except Exception as e:
                    logger.error(f"Ошибка обработки игрока {user_id}: {str(e)}")

            db.conn.commit()
            logger.info(
                f"Обработано игроков: {processed}, "
                f"переведено в AFK: {afk_count}, "
                f"начислено доходов: {income_count}"
            )

    async def _handle_afk(self, user_id):
        """Обработка перевода в AFK"""
        db.set_afk_status(user_id, True)
        try:
            await self.bot.send_message(
                chat_id=user_id,
                text="🔴 Вы перешли в режим AFK из-за неактивности! Используйте /back чтобы вернуться."
            )
            logger.info(f"Пользователь {user_id} переведен в AFK")
        except TelegramError as e:
            logger.warning(f"Не удалось отправить AFK-уведомление {user_id}: {str(e)}")

    async def _handle_income(self, user_id, level):
        """Начисление дохода игроку"""
        income = level * 10
        db.update_money(user_id, income)
        try:
            await self.bot.send_message(
                chat_id=user_id,
                text=f"🔄 Автоначисление: +{income} монет за активность!"
            )
            logger.debug(f"Начислено {income} монет пользователю {user_id}")
        except TelegramError as e:
            logger.warning(f"Не удалось отправить уведомление о начислении {user_id}: {str(e)}")

    async def shutdown(self):
        """Корректное завершение задачи"""
        self.is_running = False
        try:
            await self.bot.close()
        except Exception as e:
            logger.error(f"Ошибка при закрытии бота: {str(e)}")