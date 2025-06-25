from game.world.navigation import WorldMap
from game.player import Player
from database.manager import DatabaseManager
from game.transport import TransportManager
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

class Game:
    def __init__(self):
        """Инициализация игрового ядра"""
        self.db = DatabaseManager()
        self.world_map = WorldMap()
        self.transport_manager = TransportManager()
        self.players: Dict[int, Player] = {}  # Кэш игроков в памяти
    
    def player_exists(self, user_id: int) -> bool:
        """Проверка существования игрока"""
        try:
            return self.db.player_exists(user_id)
        except Exception as e:
            logger.error(f"Error checking player existence: {e}")
            return False
    
    def register_player(self, user_id: int, nickname: str) -> bool:
        """Регистрация нового игрока"""
        try:
            if self.db.register_player(user_id, nickname):
                # Создаем объект игрока в кэше
                player_data = self.db.get_player(user_id)
                self.players[user_id] = Player.from_dict(player_data)
                return True
            return False
        except Exception as e:
            logger.error(f"Error registering player: {e}")
            return False
    
    def get_player(self, user_id: int) -> Optional[Player]:
        """Получение игрока с кэшированием"""
        try:
            if user_id not in self.players:
                player_data = self.db.get_player(user_id)
                if player_data:
                    self.players[user_id] = Player.from_dict(player_data)
            return self.players.get(user_id)
        except Exception as e:
            logger.error(f"Error getting player: {e}")
            return None
    
    def move_player(self, user_id: int, new_location_id: str) -> bool:
        """Перемещение игрока между локациями"""
        try:
            player = self.get_player(user_id)
            if not player:
                return False
            
            # Проверяем доступность локации
            available = self.world_map.get_available_locations(player.location)
            if not any(loc.id == new_location_id for loc in available):
                return False
            
            # Обновляем позицию
            player.location = new_location_id
            player.sub_location = None  # Сбрасываем подлокацию
            return self.db.update_player_location(user_id, new_location_id)
        except Exception as e:
            logger.error(f"Error moving player: {e}")
            return False
    
    def buy_transport(self, user_id: int, transport_name: str) -> bool:
        """Покупка транспорта с проверкой средств"""
        try:
            player = self.get_player(user_id)
            if not player:
                return False
                
            transport = self.transport_manager.get_transport(transport_name)
            if not transport or player.money < transport.price:
                return False
                
            if self.db.buy_transport(user_id, transport_name, transport.price):
                player.money -= transport.price
                return True
            return False
        except Exception as e:
            logger.error(f"Error buying transport: {e}")
            return False
    
    def set_current_transport(self, user_id: int, transport_name: str) -> bool:
        """Установка активного транспорта"""
        try:
            player = self.get_player(user_id)
            if not player:
                return False
                
            # Проверяем, есть ли транспорт у игрока
            if transport_name not in player.owned_transports:
                return False
                
            if self.db.set_current_transport(user_id, transport_name):
                player.transport = transport_name
                return True
            return False
        except Exception as e:
            logger.error(f"Error setting transport: {e}")
            return False
    
    def update_player_cache(self, user_id: int):
        """Обновление кэша игрока"""
        try:
            if user_id in self.players:
                player_data = self.db.get_player(user_id)
                if player_data:
                    self.players[user_id] = Player.from_dict(player_data)
        except Exception as e:
            logger.error(f"Error updating player cache: {e}")

# Глобальный экземпляр игры
game = Game()