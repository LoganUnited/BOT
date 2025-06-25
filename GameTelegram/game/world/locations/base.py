from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class Shop:
    id: str  # Используем строковый ID
    name: str
    shop_type: str
    inventory: Dict[str, float]
    working_hours: tuple = (9, 21)

@dataclass
class SubLocation:
    id: str  # Уникальный идентификатор
    name: str
    description: str
    level_requirement: int = 1
    shops: Dict[str, Shop] = field(default_factory=dict)  # Ключ - ID магазина

    def add_shop(self, shop: Shop):
        self.shops[shop.id] = shop

class BaseLocation:
    def __init__(self, id: str, name: str, description: str):  # Добавляем ID
        self.id = id
        self.name = name
        self.description = description
        self.sub_locations: Dict[str, SubLocation] = {}  # Ключ - ID подлокации
        self.connections: Dict[str, int] = {}  # Ключ - ID связанной локации
    
    def add_sub_location(self, sub_loc: SubLocation):
        self.sub_locations[sub_loc.id] = sub_loc
    
    def connect_to(self, other_location: 'BaseLocation', distance: int):
        self.connections[other_location.id] = distance
        other_location.connections[self.id] = distance