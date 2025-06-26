from __future__ import annotations
from typing import Dict, Optional, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from game.player import Player
    from game.world.navigation import WorldMap
    from database.manager import DatabaseManager
    from game.transport import TransportManager

logger = logging.getLogger(__name__)

class Game:
    """Основной класс игрового ядра с ленивой инициализацией компонентов"""
    
    _instance = None
    
    def __init__(self):
        self._db = None
        self._transport_manager = None
        self._world_map = None
        self.players: Dict[int, Player] = {}
        self._initialized = False

    @classmethod
    def get_instance(cls) -> Game:
        """Получение глобального экземпляра игры (синглтон)"""
        if cls._instance is None:
            cls._instance = Game()
        return cls._instance

    def initialize(self):
        """Ленивая инициализация игровых систем"""
        if not self._initialized:
            # Локальные импорты для избежания циклических зависимостей
            from database.manager import DatabaseManager
            from game.transport import TransportManager
            from game.world.navigation import WorldMap
            
            self._db = DatabaseManager()
            self._transport_manager = TransportManager()
            self._world_map = WorldMap()
            self._initialized = True

    @property
    def db(self) -> DatabaseManager:
        if not self._initialized:
            self.initialize()
        return self._db

    @property
    def transport_manager(self) -> TransportManager:
        if not self._initialized:
            self.initialize()
        return self._transport_manager

    @property
    def world_map(self) -> WorldMap:
        if not self._initialized:
            self.initialize()
        return self._world_map

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
                player_data = self.db.get_player(user_id)
                from game.player import Player  # Локальный импорт
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
                    from game.player import Player  # Локальный импорт
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
            
            available = self.world_map.get_available_locations(player.location)
            if not any(loc.id == new_location_id for loc in available):
                return False
            
            player.location = new_location_id
            player.sub_location = None
            return self.db.update_player_location(user_id, new_location_id)
        except Exception as e:
            logger.error(f"Error moving player: {e}")
            return False

    def buy_transport(self, user_id: int, transport_name: str) -> bool:
        """Покупка транспорта"""
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
                    from game.player import Player  # Локальный импорт
                    self.players[user_id] = Player.from_dict(player_data)
        except Exception as e:
            logger.error(f"Error updating player cache: {e}")