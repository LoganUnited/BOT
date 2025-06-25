from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from game.core import game
from game.transport import TransportManager
from utils.logger import setup_logger

logger = setup_logger()

async def transport_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать доступный транспорт"""
    try:
        player = game.get_player(update.effective_user.id)
        if not player:
            await update.message.reply_text("Сначала зарегистрируйтесь с помощью /start")
            return
        
        keyboard = []
        
        # Текущий транспорт
        current_transport = TransportManager.get_transport(player.transport)
        msg = f"🚗 Ваш текущий транспорт: {current_transport.name}\n\n"
        msg += "Доступный транспорт:\n"
        
        # Доступный транспорт
        for transport_name in player.owned_transports:
            transport = TransportManager.get_transport(transport_name)
            is_active = "✅ " if transport_name == player.transport else ""
            keyboard.append([
                InlineKeyboardButton(
                    f"{is_active}{transport.name}",
                    callback_data=f"select_transport_{transport_name}"
                )
            ])
            msg += f"- {transport.name} ({transport.speed} км/ч)\n"
        
        # Кнопка для покупки нового транспорта
        keyboard.append([
            InlineKeyboardButton("🛒 Купить новый транспорт", callback_data="buy_transport")
        ])
        
        msg += f"\n⛽ Топливо: {player.fuel:.1f}%"
        
        # Исправленный вызов без переноса
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
    
    except Exception as e:
        logger.error(f"Ошибка в transport_command: {str(e)}")
        await update.message.reply_text("⚠️ Произошла ошибка. Попробуйте позже.")

async def select_transport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор транспорта"""
    query = update.callback_query
    await query.answer()
    
    try:
        transport_name = query.data.split('_')[2]
        player = game.get_player(query.from_user.id)
        
        if transport_name in player.owned_transports:
            player.transport = transport_name
            game.db.set_current_transport(player.user_id, transport_name)
            await query.edit_message_text(f"✅ Вы выбрали: {transport_name}")
        else:
            await query.edit_message_text("❌ Этот транспорт вам не доступен!")
    
    except Exception as e:
        logger.error(f"Ошибка выбора транспорта: {str(e)}")
        await query.edit_message_text("⚠️ Произошла ошибка. Попробуйте позже.")

async def buy_transport_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню покупки транспорта"""
    query = update.callback_query
    await query.answer()
    
    try:
        player = game.get_player(query.from_user.id)
        keyboard = []
        
        # Доступный для покупки транспорт
        for name, transport in TransportManager.TRANSPORTS.items():
            if name not in player.owned_transports:
                keyboard.append([
                    InlineKeyboardButton(
                        f"{transport.name} - ${transport.price}",
                        callback_data=f"buy_{name}"
                    )
                ])
        
        keyboard.append([
            InlineKeyboardButton("🔙 Назад", callback_data="back_to_transport")
        ])
        
        # Исправленный вызов без переноса
        await query.edit_message_text(
            "Выберите транспорт для покупки:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    except Exception as e:
        logger.error(f"Ошибка в buy_transport_menu: {str(e)}")
        await query.edit_message_text("⚠️ Произошла ошибка. Попробуйте позже.")

async def buy_transport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Покупка транспорта"""
    query = update.callback_query
    await query.answer()
    
    try:
        transport_name = query.data.split('_')[1]
        player = game.get_player(query.from_user.id)
        transport = TransportManager.get_transport(transport_name)
        
        if not transport:
            await query.edit_message_text("❌ Такого транспорта не существует!")
            return
        
        if transport_name in player.owned_transports:
            await query.edit_message_text("❌ У вас уже есть этот транспорт!")
            return
        
        if player.money < transport.price:
            await query.edit_message_text("❌ Недостаточно денег для покупки!")
            return
        
        # Совершаем покупку
        player.money -= transport.price
        player.owned_transports.append(transport_name)
        game.db.buy_transport(player.user_id, transport_name, transport.price)
        
        # Исправленный вызов без переноса
        response = (
            f"✅ Вы купили {transport.name} за ${transport.price}!\n"
            f"Ваш баланс: ${player.money:.2f}"
        )
        await query.edit_message_text(response)
    
    except Exception as e:
        logger.error(f"Ошибка покупки транспорта: {str(e)}")
        await query.edit_message_text("⚠️ Произошла ошибка при покупке.")

def get_transport_handlers():
    """Возвращает обработчики команд транспорта"""
    return [
        CommandHandler("transport", transport_command),
        CallbackQueryHandler(select_transport, pattern="^select_transport_"),
        CallbackQueryHandler(buy_transport_menu, pattern="^buy_transport$"),
        CallbackQueryHandler(buy_transport, pattern="^buy_"),
        CallbackQueryHandler(transport_command, pattern="^back_to_transport$")
    ]