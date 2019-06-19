
""" Shapely"""
from microlab.geometry.points import Point
from microlab.geometry.polygons import Polygon

shapely_point_type = type(Point())
shapely_polygon_type = type(Polygon())

def is_point(object):
    if type(object) == Point:
        return True
    return False

def is_polygon(object):
    if type(object) == Polygon:
        return True
    return False


""" Microlab """
from microlab.signals import Signal_1D, Signal_2D
from microlab.methods.intersection import Intersection


# Objects

Signal_1D_type = type(Signal_1D())
Signal_2D_type = type(Signal_2D())

Intersection_type = type(Intersection())


def is_1d_signal(object):
    if type(object) == Signal_1D_type:
        return True
    return False


def is_2d_signal(object):
    if type(object) == Signal_2D_type:
        return True
    return False


def is_intersection(object):
    if type(object) == Intersection:
        return True
    return False



