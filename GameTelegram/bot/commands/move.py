from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from game.core import game
from game.world_map import world_map  # Импортируем карту мира

async def show_locations(update: Update, player):
    """Показывает доступные для перемещения локации"""
    current_location = player.location
    available_locations = world_map.get_available_locations(current_location)
    
    if not available_locations:
        await update.message.reply_text("Нет доступных направлений для перемещения!")
        return
    
    keyboard = [
        [InlineKeyboardButton(loc.name, callback_data=f"move_{loc.id}")]
        for loc in available_locations
    ]
    
    await update.message.reply_text(
        "Куда вы хотите переместиться?",
        reply_markup=InlineKeyboardMarkup(keyboard))

async def move_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /move"""
    user = update.effective_user
    player = game.get_player(user.id)
    
    if not player:
        await update.message.reply_text("❌ Вы не зарегистрированы!")
        return
    
    await show_locations(update, player)  # Теперь функция определена

async def move_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор локации для перемещения"""
    query = update.callback_query
    await query.answer()
    
    # Формат callback_data: "move_<location_id>"
    location_id = query.data.split("_")[1]
    user = query.from_user
    player = game.get_player(user.id)
    
    # Проверяем, доступна ли локация
    current_location = player.location
    available_locations = world_map.get_available_locations(current_location)
    
    if not any(loc.id == location_id for loc in available_locations):
        await query.edit_message_text("❌ Это направление недоступно!")
        return
    
    # Перемещаем игрока
    game.move_player(user.id, location_id)
    new_location = world_map.locations[location_id]
    
    await query.edit_message_text(f"✅ Вы переместились в: {new_location.name}")

def get_move_handlers():
    """Возвращает обработчики для перемещения"""
    return [
        CommandHandler("move", move_command),
        CallbackQueryHandler(move_callback, pattern="^move_")
    ]