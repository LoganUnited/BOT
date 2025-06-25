from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from game.core import game  # Убедитесь, что этот импорт есть

async def shop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает список магазинов в текущей локации"""
    player = game.get_player(update.effective_user.id)
    loc = game.world_map.locations[player.location]
    sub_loc = loc.sub_locations.get(player.sub_location)
    
    if not sub_loc or not sub_loc.shops:
        await update.message.reply_text("Здесь нет магазинов!")
        return
    
    keyboard = [
        [InlineKeyboardButton(
            f"{shop.name} ({shop.shop_type})", 
            callback_data=f"shop_{shop.id}")]
        for shop in sub_loc.shops.values()
    ]
    
    await update.message.reply_text(
        "Магазины:",
        reply_markup=InlineKeyboardMarkup(keyboard))

async def shop_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает детали магазина и его товары"""
    query = update.callback_query
    await query.answer()
    
    # Извлекаем ID магазина из callback_data (формат "shop_<id>")
    shop_id = query.data.split("_")[1]
    
    player = game.get_player(query.from_user.id)
    loc = game.world_map.locations[player.location]
    sub_loc = loc.sub_locations.get(player.sub_location)
    
    if not sub_loc or not sub_loc.shops:
        await query.edit_message_text("Магазин не найден!")
        return
    
    # Находим нужный магазин
    shop = sub_loc.shops.get(shop_id)
    if not shop:
        await query.edit_message_text("Магазин не найден!")
        return
    
    # Формируем список товаров
    items_text = "\n".join(
        f"- {item.name}: {item.price}💰" 
        for item in shop.items.values()
    )
    
    # Создаем кнопки для покупки
    buy_buttons = [
        [InlineKeyboardButton(
            f"Купить {item.name} - {item.price}💰", 
            callback_data=f"buy_{shop_id}_{item.id}")]
        for item in shop.items.values()
    ]
    
    # Добавляем кнопку "Назад"
    back_button = [[InlineKeyboardButton("← Назад к магазинам", callback_data="back_to_shops")]]
    
    await query.edit_message_text(
        f"🏪 *{shop.name}*\n\n*Товары:*\n{items_text}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buy_buttons + back_button))

async def buy_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает покупку товара"""
    query = update.callback_query
    await query.answer()
    
    # Формат callback_data: "buy_<shop_id>_<item_id>"
    _, shop_id, item_id = query.data.split("_")
    
    player = game.get_player(query.from_user.id)
    loc = game.world_map.locations[player.location]
    sub_loc = loc.sub_locations.get(player.sub_location)
    
    if not sub_loc or not sub_loc.shops:
        await query.edit_message_text("Ошибка: магазин не найден!")
        return
    
    shop = sub_loc.shops.get(shop_id)
    if not shop:
        await query.edit_message_text("Ошибка: магазин не найден!")
        return
    
    item = shop.items.get(item_id)
    if not item:
        await query.edit_message_text("Ошибка: товар не найден!")
        return
    
    # Проверяем, хватает ли денег
    if player.money < item.price:
        await query.edit_message_text(f"❌ Недостаточно денег! Нужно {item.price}💰")
        return
    
    # Совершаем покупку
    game.update_money(player.id, -item.price)  # Снимаем деньги
    game.add_item_to_inventory(player.id, item.id)  # Добавляем предмет
    
    await query.edit_message_text(f"✅ Вы купили {item.name} за {item.price}💰!")

async def back_to_shops(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат к списку магазинов"""
    query = update.callback_query
    await query.answer()
    await shop_command(update, context)  # Повторно вызываем команду /shops

def get_shop_handlers():
    """Возвращает все обработчики для магазинов"""
    return [
        CommandHandler("shops", shop_command),
        CallbackQueryHandler(shop_details, pattern="^shop_"),
        CallbackQueryHandler(buy_item, pattern="^buy_"),
        CallbackQueryHandler(back_to_shops, pattern="^back_to_shops$")
    ]