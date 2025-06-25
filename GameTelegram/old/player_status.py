import time
import threading

player_status.start_timers()

while True:
    # Основной игровой цикл
    player_status.check_status()

class Player:
    def __init__(self):
        self.food = 100.0  # Еда
        self.water = 100.0  # Вода
        self.sleep = 100.0  # Сон
        self.lock = threading.Lock()  # Блокировка для безопасного доступа к данным

    def decrease_food(self):
        with self.lock:
            if self.food > 0:
                self.food -= 1
            if self.food < 0:
                self.food = 0

    def decrease_water(self):
        with self.lock:
            if self.water > 0:
                self.water -= 1
            if self.water < 0:
                self.water = 0

    def decrease_sleep(self):
        with self.lock:
            if self.sleep > 0:
                self.sleep -= 8.3
            if self.sleep < 0:
                self.sleep = 0

    def get_status(self):
        with self.lock:
            return f"Еда: {self.food}%, Вода: {self.water}%, Сон: {self.sleep}%"

    def check_status(self):
        with self.lock:
            if self.food == 0:
                print("У вас закончилась еда!")
            if self.water == 0:
                print("У вас закончилась вода!")
            if self.sleep == 0:
                print("Вам нужно поспать!")

def food_timer(player):
    while True:
        time.sleep(300)  # Ждем 5 минут (300 секунд)
        player.decrease_food()

def water_timer(player):
    while True:
        time.sleep(600)  # Ждем 10 минут (600 секунд)
        player.decrease_water()

def sleep_timer(player):
    while True:
        time.sleep(3600)  # Ждем 1 час (3600 секунд)
        player.decrease_sleep()

def main():
    player = Player()

    # Запускаем таймеры в отдельных потоках
    threading.Thread(target=food_timer, args=(player,), daemon=True).start()
    threading.Thread(target=water_timer, args=(player,), daemon=True).start()
    threading.Thread(target=sleep_timer, args=(player,), daemon=True).start()

    # Пример проверки статуса каждые несколько секунд
    while True:
        print(player.get_status())
        player.check_status()
        time.sleep(5)  # Проверяем каждые 5 секунд

if __name__ == "__main__":
    main()