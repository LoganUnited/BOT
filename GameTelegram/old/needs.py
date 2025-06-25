import sqlite3
from datetime import datetime, timedelta
from typing import Optional

MAX_NEED = 100
FOOD_DECAY_RATE = 1
WATER_DECAY_RATE = 1
SLEEP_DECAY_RATE = 8.3

def update_needs(user_id: int) -> None:
    with sqlite3.connect('game.db', timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT food, water, sleep, last_need_update 
            FROM users WHERE user_id = ?
        ''', (user_id,))
        result = cursor.fetchone()

        if not result:
            return

        food, water, sleep, last_need_update_str = result
        last_need_update = datetime.strptime(last_need_update_str, "%Y-%m-%d %H:%M:%S")
        now = datetime.now()
        time_diff = now - last_need_update

        minutes_passed = time_diff.total_seconds() / 60
        hours_passed = time_diff.total_seconds() / 3600

        food = max(0, food - (minutes_passed // 5) * FOOD_DECAY_RATE)
        water = max(0, water - (minutes_passed // 10) * WATER_DECAY_RATE)
        sleep = max(0, sleep - hours_passed * SLEEP_DECAY_RATE)

        cursor.execute('''
            UPDATE users 
            SET food=?, water=?, sleep=?, last_need_update=?
            WHERE user_id=?
        ''', (food, water, sleep, now.strftime("%Y-%m-%d %H:%M:%S"), user_id))
        conn.commit()

def get_needs(user_id: int) -> Optional[dict]:
    with sqlite3.connect('game.db', timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT food, water, sleep FROM users WHERE user_id=?', (user_id,))
        result = cursor.fetchone()
        return {"food": result[0], "water": result[1], "sleep": result[2]} if result else None

def restore_need(user_id: int, need_type: str, amount: int) -> bool:
    if need_type not in ["food", "water", "sleep"]: return False
    
    with sqlite3.connect('game.db', timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute(f'''
            UPDATE users 
            SET {need_type}=LEAST({need_type}+?, {MAX_NEED}) 
            WHERE user_id=?
        ''', (amount, user_id))
        conn.commit()
        return cursor.rowcount > 0