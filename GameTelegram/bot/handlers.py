from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CommandHandler,
    CallbackQueryHandler
)
from utils.logger import setup_logger
from typing import Dict, Any

# Импорт обработчиков команд
from bot.commands.move import get_move_handlers
from bot.commands.shop import get_shop_handlers
from bot.commands.transport import get_transport_handlers
from bot.commands.profile import get_profile_handlers
from bot.commands.combat import get_combat_handlers

logger = setup_logger()

# Состояния разговора
WAIT_NICKNAME = 1

def get_game():
    from game.core import game
    return game

class HandlersManager:
    def __init__(self):
        self.command_handlers = self._initialize_handlers()
        self.game = get_game()  # Инициализируем game здесь

    def _initialize_handlers(self) -> list:
        """Инициализация всех обработчиков"""
        return [
            # Обработчики регистрации
            self._create_registration_handler(),
            CommandHandler("help", self.help_command),
            
            # Новые системы: локации, магазины, транспорт
            *get_move_handlers(),
            *get_shop_handlers(),
            *get_transport_handlers(),
            
            # Основные игровые команды
            *get_profile_handlers(),
            *get_combat_handlers(),
        ]

    def _create_registration_handler(self) -> ConversationHandler:
        """Создает обработчик регистрации"""
        return ConversationHandler(
            entry_points=[CommandHandler("start", self.start)],
            states={
                WAIT_NICKNAME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        self.register_player
                    )
                ]
            },
            fallbacks=[
                CommandHandler("cancel", self.cancel_registration),
                CallbackQueryHandler(self.cancel_registration)
            ],
            allow_reentry=True
        )

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Обработчик команды /start"""
        user = update.effective_user
        try:
            if self.game.player_exists(user.id):
                await update.message.reply_text(
                    f"Привет, {user.username or 'игрок'}! Ты уже в игре!",
                    reply_markup=self._main_menu_markup()
                )
                return ConversationHandler.END
            
            await update.message.reply_text(
                "🎮 Добро пожаловать в игру!\n"
                "Введи никнейм (от 2 до 20 символов):",
                reply_markup=self._cancel_markup()
            )
            return WAIT_NICKNAME
        except Exception as e:
            logger.error(f"Ошибка в start: {str(e)}")
            await update.message.reply_text("⚠️ Произошла ошибка. Попробуйте позже.")
            return ConversationHandler.END

    async def register_player(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Обработка введенного никнейма"""
        user = update.effective_user
        nickname = update.message.text.strip()
        
        try:
            if not 2 <= len(nickname) <= 20:
                await update.message.reply_text(
                    "❌ Никнейм должен быть от 2 до 20 символов!",
                    reply_markup=self._cancel_markup()
                )
                return WAIT_NICKNAME
            
            if not nickname.isalnum():
                await update.message.reply_text(
                    "❌ Никнейм должен содержать только буквы и цифры!",
                    reply_markup=self._cancel_markup()
                )
                return WAIT_NICKNAME
            
            if self.game.register_player(user.id, nickname):
                await update.message.reply_text(
                    f"✅ Регистрация успешна, {nickname}!\n"
                    "Используй /help для списка команд.",
                    reply_markup=self._main_menu_markup()
                )
            else:
                await update.message.reply_text(
                    "❌ Этот никнейм уже занят. Попробуй другой:",
                    reply_markup=self._cancel_markup()
                )
                return WAIT_NICKNAME
        except Exception as e:
            logger.error(f"Ошибка регистрации: {str(e)}")
            await update.message.reply_text("⚠️ Ошибка регистрации. Попробуйте позже.")
        
        return ConversationHandler.END

    async def cancel_registration(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Отмена регистрации"""
        await update.message.reply_text(
            "Регистрация отменена. Нажми /start чтобы начать заново.",
            reply_markup=self._main_menu_markup()
        )
        return ConversationHandler.END

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /help"""
        try:
            await update.message.reply_text(
                "ℹ️ <b>Доступные команды:</b>\n"
                "/start - Начать игру\n"
                "/profile - Профиль игрока\n"
                "/inventory - Инвентарь\n"
                "/shops - Показать магазины\n"
                "/move - Переместиться в другую локацию\n"
                "/transport - Управление транспортом\n"
                "/fight - Начать бой\n"
                "/help - Помощь\n\n"
                "🔄 Используй кнопки меню для быстрого доступа!",
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Ошибка в help_command: {str(e)}")

    def _main_menu_markup(self) -> Dict[str, Any]:
        """Клавиатура основного меню"""
        return {
            "keyboard": [
                ["Профиль", "Инвентарь"],
                ["Магазины", "Транспорт"],
                ["Переместиться"],
                ["Бой", "Помощь"]
            ],
            "resize_keyboard": True
        }

    def _cancel_markup(self) -> Dict[str, Any]:
        """Клавиатура для отмены"""
        return {
            "keyboard": [["Отменить регистрацию"]],
            "resize_keyboard": True
        }

    def get_all_handlers(self) -> list:
        """Возвращает все обработчики"""
        return self.command_handlers