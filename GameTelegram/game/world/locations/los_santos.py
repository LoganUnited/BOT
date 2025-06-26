from game.world.locations.base import BaseLocation, SubLocation, Shop
from game.items.shop_items import health_potion, mana_potion  # Импорт экземпляров

class LosSantos(BaseLocation):
    def __init__(self):
        super().__init__("LS", "Los Santos", "Солнечный город")
        
        # Создаем подлокации
        center = SubLocation("ls_center", "Центр", "Центральная площадь")
        beach = SubLocation("ls_beach", "Пляж", "Песчаный пляж с видом на океан")
        
        # Добавляем подлокации
        self.add_sub_location(center)
        self.add_sub_location(beach)
        
        # Создаем магазины
        market = Shop("market", "Рынок", "Местный рынок с различными товарами")
        market.add_item(health_potion)
        market.add_item(mana_potion)
        
        # Добавляем магазины
        self.add_shop(market)