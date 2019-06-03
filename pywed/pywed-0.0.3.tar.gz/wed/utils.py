from enum import Enum, auto


class DataType(Enum):
    WIND = auto()
    WAVE = auto()
    CURRENT = auto()

    def __str__(self):
        return self.name.lower()

class Service(Enum):
    ECMWF = auto()

    def __str__(self):
        return self.name.lower()

class Coordinate:
    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude
