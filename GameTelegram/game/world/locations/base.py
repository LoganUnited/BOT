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
    """Базовый класс для всех локаций"""
    def __init__(self, loc_id: str, name: str, description: str):
        self.id = loc_id
        self.name = name
        self.description = description
        self.connections: Dict[str, float] = {}  # {location_id: distance}
        self.sub_locations: Dict[str, SubLocation] = {}
        self.shops: List[Shop] = []
    
    def connect_to(self, other: 'BaseLocation', distance: float):
        self.connections[other.id] = distance
        other.connections[self.id] = distance
    
    def add_sub_location(self, sub_loc: SubLocation):
        self.sub_locations[sub_loc.id] = sub_loc
    
    def add_shop(self, shop: Shop):
        self.shops.append(shop)