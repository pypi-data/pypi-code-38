from enum import Enum, auto
from wed import settings


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

def round_to_precision(value: float, precision: float) -> float:
    if precision is None:
        return value
    rest = value % precision
    value -= rest
    if rest >= precision / 2:
        value += precision
    return value

def round_coordinate(coordinate: Coordinate, type: DataType) -> Coordinate:
    """Update the coordinate considering the range"""
    range = settings.get_coordinate_range(type, settings.Settings().services[type])

    longitude = coordinate.longitude
    while longitude < range["longitude"]["min"]:
        longitude += 360
    while longitude > range["longitude"]["max"]:
        longitude -= 360
    coordinate.longitude = longitude
    return coordinate
