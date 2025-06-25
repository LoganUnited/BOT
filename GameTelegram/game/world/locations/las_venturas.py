from game.world.locations.base import BaseLocation

class LasVenturas(BaseLocation):
    def __init__(self):
        super().__init__()
        self.name = "Лас-Вентурас"
        self.description = "Город азарта и казино"