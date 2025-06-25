import os
from pathlib import Path
from typing import List, Final
import logging

# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    """Класс для хранения конфигурации приложения"""
    
    # Пути
    BASE_DIR: Final[Path] = Path(__file__).parent.resolve()
    DB_PATH: Final[Path] = BASE_DIR / "database" / "game.db"
    EXPORT_FOLDER: Final[Path] = BASE_DIR / "exports"
    LOGS_FOLDER: Final[Path] = BASE_DIR / "logs"
    
    # Настройки бота
    BOT_TOKEN: Final[str] = "7578255189:AAEkOcP-BmvZnOWXz39iYCop7PgDVMllSMQ"
    ADMIN_IDS: Final[List[int]] = [123456789]
    
    # Игровые настройки
    ALLOWED_LOCATIONS: Final[List[str]] = ["LS", "SF", "LV"]
    DEFAULT_LOCATION: Final[str] = "LS"
    MAX_NICKNAME_LENGTH: Final[int] = 20
    MIN_NICKNAME_LENGTH: Final[int] = 2
    
    @classmethod
    def initialize(cls) -> None:
        """Инициализация необходимых директорий"""
        try:
            for folder in [cls.EXPORT_FOLDER, cls.LOGS_FOLDER, cls.DB_PATH.parent]:
                folder.mkdir(exist_ok=True, parents=True)
            logger.info("Директории успешно инициализированы")
        except Exception as e:
            logger.error(f"Ошибка при создании директорий: {e}")
            raise

# Инициализация директорий
Config.initialize()

# Явный экспорт всех необходимых переменных
BOT_TOKEN = Config.BOT_TOKEN
ADMIN_IDS = Config.ADMIN_IDS
ALLOWED_LOCATIONS = Config.ALLOWED_LOCATIONS
DEFAULT_LOCATION = Config.DEFAULT_LOCATION
DB_PATH = Config.DB_PATH
EXPORT_FOLDER = Config.EXPORT_FOLDER
LOGS_FOLDER = Config.LOGS_FOLDER