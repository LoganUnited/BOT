from game.transport import TransportManager
from typing import Dict

class Player:
    def __init__(self, user_id: int, nickname: str, location: str = "LS", sub_location: str = "Downtown", money: float = 1000.0, level: int = 1):
        self.user_id = user_id
        self.nickname = nickname
        self.location = location
        self.sub_location = sub_location
        self.money = money
        self.level = level
        self.transport = "foot"
        self.owned_transports = ["foot", "bike"]  # Изначально доступные транспорты
        self.fuel = 100.0  # Процент топлива
        self.inventory: Dict[str, int] = {}  # Предметы в инвентаре
        self.experience = 0
        self.health = 100
    
    def set_transport(self, transport_name: str) -> bool:
        """Установить текущий транспорт"""
        if transport_name in self.owned_transports:
            self.transport = transport_name
            return True
        return False
    
    def buy_transport(self, transport_name: str) -> bool:
        """Купить новый транспорт"""
        transport = TransportManager.get_transport(transport_name)
        if transport and transport.price <= self.money and transport_name not in self.owned_transports:
            self.owned_transports.append(transport_name)
            self.money -= transport.price
            return True
        return False
    
    def update_fuel(self, distance: float):
        """Обновить уровень топлива после поездки"""
        transport = TransportManager.get_transport(self.transport)
        fuel_used = distance * transport.fuel_cost
        self.fuel = max(0, self.fuel - fuel_used)
    
    def refuel(self, amount: float) -> bool:
        """Заправить транспорт"""
        if self.money >= amount:
            self.fuel = min(100, self.fuel + amount)
            self.money -= amount
            return True
        return False
    
    def add_experience(self, amount: int):
        """Добавить опыт игроку"""
        self.experience += amount
        while self.experience >= self.level * 100:
            self.experience -= self.level * 100
            self.level_up()
    
    def level_up(self):
        """Повышение уровня"""
        self.level += 1
        self.health = 100  # Полное восстановление здоровья
    
    def buy_item(self, item_name: str, price: float) -> bool:
        """Купить предмет"""
        if self.money >= price:
            self.inventory[item_name] = self.inventory.get(item_name, 0) + 1
            self.money -= price
            return True
        return False
    
    def to_dict(self) -> dict:
        """Конвертировать объект игрока в словарь"""
        return {
            "user_id": self.user_id,
            "nickname": self.nickname,
            "location": self.location,
            "sub_location": self.sub_location,
            "money": self.money,
            "level": self.level,
            "transport": self.transport,
            "owned_transports": ",".join(self.owned_transports),
            "fuel": self.fuel,
            "inventory": ",".join(f"{k}:{v}" for k, v in self.inventory.items()),
            "experience": self.experience,
            "health": self.health
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Player':
        """Создать объект игрока из словаря"""
        player = cls(
            user_id=data["user_id"],
            nickname=data["nickname"],
            location=data.get("location", "LS"),
            sub_location=data.get("sub_location", "Downtown"),
            money=data.get("money", 1000.0),
            level=data.get("level", 1)
        )
        
        player.transport = data.get("transport", "foot")
        player.owned_transports = data.get("owned_transports", "foot,bike").split(",")
        player.fuel = float(data.get("fuel", 100.0))
        player.experience = int(data.get("experience", 0))
        player.health = int(data.get("health", 100))
        
        # Восстановление инвентаря
        inventory_data = data.get("inventory", "")
        if inventory_data:
            for item_str in inventory_data.split(","):
                if ":" in item_str:
                    item, count = item_str.split(":")
                    player.inventory[item] = int(count)
        
        return player