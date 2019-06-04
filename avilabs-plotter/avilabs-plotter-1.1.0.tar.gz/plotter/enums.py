from enum import Enum, auto

class LegendLocation(Enum):
    BEST = auto()

    UPPER_RIGHT = auto()
    UPPER_LEFT = auto()
    UPPER_CENTER = auto()

    LOWER_RIGHT = auto()
    LOWER_LEFT = auto()
    LOWER_CENTER = auto()


class LineStyle(Enum):
    SOLID = auto()
    DASH = auto()
    DASHDOT = auto()
    DOT = auto()


class Marker(Enum):
    POINT = auto()
    PIXEL = auto()
    STAR = auto()
    PLUS = auto()
    X = auto()
    CIRCLE = auto()
    TRIANGLE = auto()
    SQAURE = auto()
    PENTAGON = auto()
    HEXAGON = auto()
    DIAMOND = auto()
    VLINE = auto()
    HLINE = auto()
