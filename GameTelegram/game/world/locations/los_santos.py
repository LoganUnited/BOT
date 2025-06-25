from game.world.locations.base import BaseLocation, SubLocation, Shop
from game.items import shop_items

class LosSantos(BaseLocation):
    def __init__(self):
        super().__init__()
        self.name = "Лос-Сантос"
        self.description = "Солнечный город с пляжами и гетто"
        
        downtown = SubLocation(
            name="Downtown",
            description="Деловой центр города",
            level_requirement=5
        )
        
        downtown.add_shop(Shop(
            id=1001,
            name="24/7 Supermarket",
            location="Downtown",
            shop_type="general",
            inventory=shop_items.GENERAL_GOODS,
            working_hours=(0, 24)
        ))
        
        self.add_sub_location(downtown)