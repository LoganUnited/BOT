import random

class CombatSystem:
    def __init__(self):
        self.enemies = {
            "Лес": ["Волк", "Медведь", "Разбойник"],
            "Пещера": ["Гоблин", "Тролль", "Летучая мышь"],
            "Город": ["Вор", "Пьяный моряк", "Стражник"]
        }
    
    def start_combat(self, location: str) -> dict:
        enemy = random.choice(self.enemies.get(location, ["Бродяга"]))
        enemy_hp = random.randint(20, 50)
        return {
            "enemy": enemy,
            "hp": enemy_hp,
            "max_hp": enemy_hp,
            "damage": random.randint(5, 15)
        }
    
    def player_attack(self, player_damage: int, enemy: dict) -> dict:
        damage = random.randint(player_damage - 3, player_damage + 3)
        new_hp = max(0, enemy["hp"] - damage)
        
        return {
            "damage": damage,
            "is_critical": random.random() < 0.2,
            "enemy_defeated": new_hp <= 0,
            "hp": new_hp
        }

# Глобальный экземпляр для использования в командах
combat_system = CombatSystem()