from game.world.locations.base import BaseLocation

class SanFierro(BaseLocation):
    def __init__(self):
        super().__init__()
        self.name = "Сан-Фиерро"
        self.description = "Портовый город с холмами"