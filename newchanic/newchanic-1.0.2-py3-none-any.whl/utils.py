from math import sqrt
from typing import Union

Number = Union[int, float]


def distance_between(position, other_position):
    return sqrt((position[0] - other_position[0]) ** 2 + (position[1] - other_position[1]) ** 2)
