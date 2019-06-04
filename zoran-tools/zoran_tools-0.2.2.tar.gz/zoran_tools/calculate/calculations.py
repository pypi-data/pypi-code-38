"""
一些小计算程序放在这里
"""

import math
from math import radians, cos, sin, asin, sqrt

import matplotlib.pyplot as plt
import numpy as np


__all__ = ['distance_on_earth', 'haversine', ]


def distance_on_earth(p1, p2, unit='m'):
    """
    calculates the distance using Haversine formula
    使用半正失公式计算地球上两点的距离
    :param p1: 要计算的两个点之一
    :param p2: 要计算的两个点之二
    :param unit: 距离的单位，m为米，km为千米，mile为英里
    """

    # get the lng and lat
    lat1, lon1 = p1[-1], p1[-2]
    lat2, lon2 = p2[-1], p2[-2]

    # convert to radians
    deltalat_radians = math.radians(lat2 - lat1)
    deltalon_radians = math.radians(lon2 - lon1)

    lat1_radians = math.radians(lat1)
    lat2_radians = math.radians(lat2)

    # apply the formula
    hav = math.sin(deltalat_radians / 2.0) ** 2 + \
          math.sin(deltalon_radians / 2.0) ** 2 * \
          math.cos(lat1_radians) * \
          math.cos(lat2_radians)

    # dist = lambda r, hav: 2 * r * math.asin(math.sqrt(hav))
    # PEP8: do not use assign a lambda expression, use a def
    def dist(r, hav):
        return 2 * r * math.asin(math.sqrt(hav))

    unit_dict = {
        'm': int(dist(r=6371 * 1000, hav=hav)),
        'km': float('%.2f' % (dist(r=6371, hav=hav))),
        'mile': float('%.2f' % (dist(r=3959, hav=hav))),
    }
    return unit_dict.get(unit)


def haversine(lon1, lat1, lon2, lat2, r=6371*1000):
    """
    半正矢公式计算球面上两点距离
    :param r: 球的半径
    """
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return c * r 
