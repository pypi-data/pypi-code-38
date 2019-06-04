from enum import Enum, auto
import numpy as np


class ColorMap(Enum):
    GRAY = auto()
    PURPLE = auto()
    BLUE = auto()
    GREEN = auto()
    ORANGE = auto()
    RED = auto()
    YELLOW_BROWN = auto()
    YELLOW_RED = auto()
    ORANGE_RED = auto()
    PURPLE_RED = auto()
    RED_PURPLE = auto()
    BLUE_PURPLE = auto()
    GREEN_BLUE = auto()
    PURPLE_BLUE = auto()
    YELLOW_GREEN_BLUE = auto()
    PURPLE_BLUE_GREEN = auto()
    BLUE_GREEN = auto()
    YELLO_GREEN = auto()


class Color:
    def __init__(self, *, red: int, green: int, blue: int, alpha=1) -> None:
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha

    def to_array(self):
        return [self.red/255, self.green/255, self.blue/255, self.alpha]

    @classmethod
    def random(cls):
        red = np.random.randint(0, 256)
        blue = np.random.randint(0, 256)
        green = np.random.randint(0, 256)
        alpha = 0.5 + (np.random.random() * 0.5)  # between 0.5 and 1.0
        return Color(red=red, green=green, blue=blue, alpha=alpha)

    def __eq__(self, other):
        return self.red == other.red and self.green == other.green and self.blue == other.blue and self.alpha == other.alpha
