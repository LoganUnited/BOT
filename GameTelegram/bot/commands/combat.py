import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from game.core import game
from game.combat import combat_system
from utils.decorators import update_activity

@update_activity
async def start_combat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = game.db.get_player(user.id)
    
    if not player:
        await update.message.reply_text("❌ Вы не зарегистрированы!")
        return
    
    location = player[5]
    combat_data = combat_system.start_combat(location)
    context.user_data["combat"] = combat_data
    
    keyboard = [
        [InlineKeyboardButton("⚔ Атаковать", callback_data="attack")],
        [InlineKeyboardButton("🏃 Бежать", callback_data="flee")]
    ]
    
    await update.message.reply_text(
        f"⚔️ На вас напал {combat_data['enemy']} (❤️ {combat_data['hp']}/{combat_data['max_hp']})!",
        reply_markup=InlineKeyboardMarkup(keyboard))

@update_activity
async def combat_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    action = query.data
    
    combat_data = context.user_data.get("combat")
    if not combat_data:
        await query.edit_message_text("❌ Бой уже завершен!")
        return
    
    player_data = game.db.get_player(user.id)
    if not player_data:
        await query.edit_message_text("❌ Игрок не найден!")
        return
    
    if action == "attack":
        player_damage = player_data[2] * 5
        result = combat_system.player_attack(player_damage, combat_data)
        
        message = f"⚔️ Вы нанесли {result['damage']} урона!"
        if result["is_critical"]:
            message += " Критический удар!"
        
        if result["enemy_defeated"]:
            message += f"\n🎉 Вы победили {combat_data['enemy']}!"
            reward = random.randint(10, 30)
            game.update_money(user.id, reward)
            message += f"\n💰 Получено {reward} монет!"
            await query.edit_message_text(message)
            del context.user_data["combat"]
            return
        
        combat_data["hp"] = result["hp"]
        context.user_data["combat"] = combat_data
        message += f"\n❤️ {combat_data['enemy']}: {combat_data['hp']}/{combat_data['max_hp']}"
        
        keyboard = [
            [InlineKeyboardButton("⚔ Атаковать", callback_data="attack")],
            [InlineKeyboardButton("🏃 Бежать", callback_data="flee")]
        ]
        
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif action == "flee":
        success = random.random() > 0.3
        if success:
            await query.edit_message_text("🏃‍♂️ Вы успешно сбежали!")
        else:
            damage = random.randint(5, 15)
            new_hp = max(0, player_data[3] - damage)
            game.update_hp(user.id, new_hp)
            await query.edit_message_text(f"❌ Не удалось сбежать! Вы получили {damage} урона.\n❤️ Ваше здоровье: {new_hp}/100")
        del context.user_data["combat"]

# Добавляем эту функцию для экспорта обработчиков
def get_combat_handlers():
    return [
        CommandHandler("fight", start_combat),
        CallbackQueryHandler(combat_callback, pattern="^(attack|flee)$")
    ]

# Альтернативно можно использовать переменную (как у вас было)
combat_handlers = get_combat_handlers()