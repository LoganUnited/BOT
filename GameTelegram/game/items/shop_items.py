class HealthPotion:
    def __init__(self):
        self.name = "Зелье здоровья"
        self.description = "Восстанавливает 50 HP"
        self.price = 50
        self.heal_amount = 50

class ManaPotion:
    def __init__(self):
        self.name = "Зелье маны"
        self.description = "Восстанавливает 30 MP"
        self.price = 75
        self.mana_amount = 30

# Создаем экземпляры предметов
health_potion = HealthPotion()
mana_potion = ManaPotion()