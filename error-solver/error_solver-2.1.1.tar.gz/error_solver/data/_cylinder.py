"""
Created by Error Solver on 2019-04-14 22:39:06

0: area - pi*radius**2
1: -area*height + volume
"""

from math import *


# Equation 0
def eq0(area, radius, **kwargs):
    return area - pi*radius**2


def eq0_area(area, radius, **kwargs):
    return 1


def eq0_radius(area, radius, **kwargs):
    return -2*pi*radius


# Equation 1
def eq1(area, height, volume, **kwargs):
    return -area*height + volume


def eq1_area(area, height, volume, **kwargs):
    return -height


def eq1_height(area, height, volume, **kwargs):
    return -area


def eq1_volume(area, height, volume, **kwargs):
    return 1


# Assembled functions
EQUATIONS = [
    eq0,
    eq1
]


PARTIALS = [
    {'area': eq0_area, 'radius': eq0_radius},
    {'area': eq1_area, 'height': eq1_height, 'volume': eq1_volume}
]


COMBOS = {

}
