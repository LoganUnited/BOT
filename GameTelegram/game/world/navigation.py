from game.world.base import BaseLocationfrom typing import Dict, List, Optional
from game.world.base import BaseLocation, SubLocation

class WorldMap:
    def __init__(self):
        self.locations: Dict[str, BaseLocation] = {}  # Ключ - ID локации
        self._setup_world()
    
    def _setup_world(self):
        # Создаем основные локации
        ls = BaseLocation("LS", "Los Santos", "Солнечный город")
        sf = BaseLocation("SF", "San Fierro", "Портовый город")
        lv = BaseLocation("LV", "Las Venturas", "Город азарта")
        
        # Добавляем подлокации
        ls.add_sub_location(SubLocation("ls_center", "Центр", "Центральная площадь"))
        sf.add_sub_location(SubLocation("sf_port", "Порт", "Морской порт"))
        
        # Устанавливаем связи
        ls.connect_to(sf, 200)
        ls.connect_to(lv, 250)
        sf.connect_to(lv, 150)
        
        # Регистрируем локации
        self.locations = {loc.id: loc for loc in [ls, sf, lv]}
    
    def get_location(self, location_id: str) -> Optional[BaseLocation]:
        return self.locations.get(location_id)
    
    def get_available_locations(self, current_location_id: str) -> List[BaseLocation]:
        current = self.get_location(current_location_id)
        if not current:
            return []
        
        return [
            self.locations[loc_id]
            for loc_id in current.connections
            if loc_id in self.locations
        ]
    
    def calculate_travel_time(self, from_loc_id: str, to_loc_id: str, speed: float) -> float:
        """Рассчитать время в пути в секундах"""
        from_loc = self.get_location(from_loc_id)
        to_loc = self.get_location(to_loc_id)
        
        if not from_loc or not to_loc:
            raise ValueError("Локация не найдена")
        
        distance = from_loc.connections.get(to_loc_id)
        if distance is None:
            raise ValueError("Нет пути между локациями")
        
        # speed - скорость в км/ч, distance - в км
        # Возвращаем время в секундах
        return (distance / speed) * 3600  # часы * 3600 = секунды

# Пример использования:
world_map = WorldMap()
print(world_map.get_available_locations("LS"))