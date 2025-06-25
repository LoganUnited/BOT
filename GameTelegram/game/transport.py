from dataclasses import dataclass
from enum import Enum

class TransportType(Enum):
    FOOT = 1
    BIKE = 2
    CAR = 3
    SPORT_CAR = 4
    AIRPLANE = 5

@dataclass
class Transport:
    name: str
    speed: float
    type: TransportType
    fuel_cost: float = 0
    owned: bool = False
    price: float = 0

class TransportManager:
    TRANSPORTS = {
        "foot": Transport("Пешком", 5, TransportType.FOOT),
        "bike": Transport("Велосипед", 15, TransportType.BIKE, 0, True, 200),
        "sedan": Transport("Седан", 60, TransportType.CAR, 0.1, False, 15000),
        "sport": Transport("Спортивный автомобиль", 120, TransportType.SPORT_CAR, 0.3, False, 75000),
        "plane": Transport("Самолет", 500, TransportType.AIRPLANE, 1.5, False, 500000)
    }

    @classmethod
    def get_transport(cls, transport_name: str) -> Transport:
        return cls.TRANSPORTS.get(transport_name.lower())