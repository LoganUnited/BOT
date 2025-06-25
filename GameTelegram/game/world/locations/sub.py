from .base import BaseLocation

class SubLocation(BaseLocation):
    """Класс для подлокаций (кварталов, зданий и т.д.)"""
    def __init__(self, loc_id: str, name: str, description: str):
        super().__init__(loc_id, name, description)
        self.type = "sub_location"