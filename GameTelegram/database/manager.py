import sqlite3
import json
from datetime import datetime
from config import Config

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect(Config.DB_PATH)
        self._create_tables()
    
    def _create_tables(self):
        cursor = self.conn.cursor()
        
        # Таблица игроков с расширенными полями
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                user_id INTEGER PRIMARY KEY,
                nickname TEXT NOT NULL UNIQUE,
                level INTEGER DEFAULT 1,
                health INTEGER DEFAULT 100,
                money REAL DEFAULT 1000.0,
                location TEXT DEFAULT 'LS',
                sub_location TEXT DEFAULT 'Downtown',
                transport TEXT DEFAULT 'foot',
                owned_transports TEXT DEFAULT 'foot,bike',
                fuel REAL DEFAULT 100.0,
                inventory TEXT,
                experience INTEGER DEFAULT 0,
                is_afk BOOLEAN DEFAULT 0,
                last_active TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица предметов в магазинах
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shop_items (
                shop_id INTEGER,
                item_name TEXT NOT NULL,
                price REAL NOT NULL,
                PRIMARY KEY (shop_id, item_name)
            )
        """)
        
        # Таблица расстояний между локациями
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS location_distances (
                from_location TEXT,
                to_location TEXT,
                distance INTEGER,
                PRIMARY KEY (from_location, to_location)
            )
        """)
        
        self.conn.commit()
    
    def player_exists(self, user_id: int) -> bool:
        """Проверяет, существует ли игрок"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM players WHERE user_id = ?", (user_id,))
        return cursor.fetchone() is not None
    
    def register_player(self, user_id: int, nickname: str) -> bool:
        """Регистрирует нового игрока"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO players (user_id, nickname) VALUES (?, ?)",
                (user_id, nickname)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_player(self, user_id: int) -> dict:
        """Получает данные игрока"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM players WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            columns = [col[0] for col in cursor.description]
            return dict(zip(columns, row))
        return None
    
    def update_player_location(self, user_id: int, location: str, sub_location: str = None):
        """Обновляет локацию игрока"""
        cursor = self.conn.cursor()
        if sub_location:
            cursor.execute(
                "UPDATE players SET location = ?, sub_location = ? WHERE user_id = ?",
                (location, sub_location, user_id)
            )
        else:
            cursor.execute(
                "UPDATE players SET location = ? WHERE user_id = ?",
                (location, user_id)
            )
        self.conn.commit()
    
    def update_money(self, user_id: int, amount: float) -> bool:
        """Обновляет количество денег игрока"""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE players SET money = money + ? WHERE user_id = ?",
            (amount, user_id)
        )
        self.conn.commit()
        return cursor.rowcount > 0
    
    def update_health(self, user_id: int, new_health: int) -> bool:
        """Обновляет здоровье игрока"""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE players SET health = ? WHERE user_id = ?",
            (new_health, user_id)
        )
        self.conn.commit()
        return cursor.rowcount > 0
    
    def update_activity(self, user_id: int) -> bool:
        """Обновляет время последней активности"""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE players SET last_active = CURRENT_TIMESTAMP, is_afk = 0 WHERE user_id = ?",
            (user_id,)
        )
        self.conn.commit()
        return cursor.rowcount > 0
    
    def set_afk_status(self, user_id: int, status: bool) -> bool:
        """Устанавливает статус AFK"""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE players SET is_afk = ? WHERE user_id = ?",
            (int(status), user_id)
        )
        self.conn.commit()
        return cursor.rowcount > 0
    
    def get_afk_players(self) -> list:
        """Получает игроков, перешедших в AFK"""
        cursor = self.conn.cursor()
        try:
            # Используем datetime для точного расчета времени
            cursor.execute("""
                SELECT user_id, nickname 
                FROM players 
                WHERE last_active < datetime('now', '-24 hours') 
                AND is_afk = 0
            """)
            return cursor.fetchall()
        except sqlite3.OperationalError as e:
            print(f"Ошибка в get_afk_players: {str(e)}")
            return []
    
    def get_all_players(self) -> list:
        """Получает всех игроков"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM players")
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def buy_transport(self, user_id: int, transport_name: str, price: float) -> bool:
        """Покупка транспорта"""
        cursor = self.conn.cursor()
        
        # Проверяем, есть ли уже этот транспорт
        cursor.execute(
            "SELECT owned_transports FROM players WHERE user_id = ?",
            (user_id,)
        )
        transports = cursor.fetchone()[0].split(',')
        
        if transport_name in transports:
            return False  # Транспорт уже куплен
        
        # Обновляем список транспорта и деньги
        transports.append(transport_name)
        new_transports = ','.join(transports)
        
        cursor.execute(
            "UPDATE players SET owned_transports = ?, money = money - ? WHERE user_id = ?",
            (new_transports, price, user_id)
        )
        self.conn.commit()
        return cursor.rowcount > 0
    
    def set_current_transport(self, user_id: int, transport_name: str) -> bool:
        """Устанавливает текущий транспорт"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT owned_transports FROM players WHERE user_id = ?",
            (user_id,)
        )
        transports = cursor.fetchone()[0].split(',')
        
        if transport_name not in transports:
            return False  # Транспорт не куплен
        
        cursor.execute(
            "UPDATE players SET transport = ? WHERE user_id = ?",
            (transport_name, user_id)
        )
        self.conn.commit()
        return cursor.rowcount > 0
    
    def update_fuel(self, user_id: int, fuel_used: float) -> bool:
        """Обновляет уровень топлива"""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE players SET fuel = fuel - ? WHERE user_id = ?",
            (fuel_used, user_id)
        )
        self.conn.commit()
        return cursor.rowcount > 0
    
    def refuel(self, user_id: int, amount: float, cost: float) -> bool:
        """Заправляет транспорт"""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE players SET fuel = fuel + ?, money = money - ? WHERE user_id = ?",
            (amount, cost, user_id)
        )
        self.conn.commit()
        return cursor.rowcount > 0
    
    def add_experience(self, user_id: int, amount: int) -> bool:
        """Добавляет опыт игроку"""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE players SET experience = experience + ? WHERE user_id = ?",
            (amount, user_id)
        )
        self.conn.commit()
        return cursor.rowcount > 0
    
    def level_up(self, user_id: int) -> bool:
        """Повышает уровень игрока"""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE players SET level = level + 1, health = 100, experience = 0 WHERE user_id = ?",
            (user_id,)
        )
        self.conn.commit()
        return cursor.rowcount > 0
    
    def add_item_to_inventory(self, user_id: int, item_name: str) -> bool:
        """Добавляет предмет в инвентарь"""
        cursor = self.conn.cursor()
        
        # Получаем текущий инвентарь
        cursor.execute(
            "SELECT inventory FROM players WHERE user_id = ?",
            (user_id,)
        )
        inventory_str = cursor.fetchone()[0] or ""
        inventory = {}
        
        if inventory_str:
            for item in inventory_str.split(','):
                name, count = item.split(':')
                inventory[name] = int(count)
        
        # Обновляем количество предмета
        inventory[item_name] = inventory.get(item_name, 0) + 1
        
        # Формируем новую строку инвентаря
        new_inventory = ','.join([f"{k}:{v}" for k, v in inventory.items()])
        
        cursor.execute(
            "UPDATE players SET inventory = ? WHERE user_id = ?",
            (new_inventory, user_id)
        )
        self.conn.commit()
        return cursor.rowcount > 0
    
    def remove_money(self, user_id: int, amount: float) -> bool:
        """Снимает деньги со счета игрока"""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE players SET money = money - ? WHERE user_id = ? AND money >= ?",
            (amount, user_id, amount)
        )
        self.conn.commit()
        return cursor.rowcount > 0
    
    def save_location_distances(self, distances: dict):
        """Сохраняет расстояния между локациями"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM location_distances")
        
        for (from_loc, to_loc), distance in distances.items():
            cursor.execute(
                "INSERT INTO location_distances (from_location, to_location, distance) VALUES (?, ?, ?)",
                (from_loc, to_loc, distance)
            )
        
        self.conn.commit()
    
    def get_distance(self, from_loc: str, to_loc: str) -> int:
        """Получает расстояние между локациями"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT distance FROM location_distances WHERE from_location = ? AND to_location = ?",
            (from_loc, to_loc)
        )
        result = cursor.fetchone()
        return result[0] if result else 0

    def buy_transport(self, user_id: int, transport_name: str, price: float) -> bool:
        """Покупка транспорта"""
        cursor = self.conn.cursor()
        
        # Получаем текущий список транспорта
        cursor.execute(
            "SELECT owned_transports FROM players WHERE user_id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        transports = row[0].split(',') if row and row[0] else []
        
        # Добавляем новый транспорт
        if transport_name not in transports:
            transports.append(transport_name)
            new_transports = ','.join(transports)
            
            cursor.execute(
                "UPDATE players SET owned_transports = ?, money = money - ? WHERE user_id = ?",
                (new_transports, price, user_id)
            )
            self.conn.commit()
            return cursor.rowcount > 0
        return False
    
    def set_current_transport(self, user_id: int, transport_name: str) -> bool:
        """Устанавливает текущий транспорт"""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE players SET transport = ? WHERE user_id = ?",
            (transport_name, user_id)
        )
        self.conn.commit()
        return cursor.rowcount > 0