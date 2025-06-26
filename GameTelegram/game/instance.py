from game.core import Game

# Единственный глобальный экземпляр
_game_instance = None

def get_game():
    global _game_instance
    if _game_instance is None:
        _game_instance = Game()
    return _game_instance