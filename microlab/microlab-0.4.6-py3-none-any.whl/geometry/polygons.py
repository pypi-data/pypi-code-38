from microlab.geometry.points import create_points
from microlab.signals import Signal_2D

from shapely.geometry.polygon import Polygon



def create_polygon(signal=Signal_2D(), verbose=False):
    '''
    Input:  Signal 1D , or Signal 2D
    Output: Shapely Polygon

    :param signal:
    :param verbose:
    :return:                a shapely.geometry.polygon.Polygon object
    '''
    points = create_points(signal=signal, verbose=False)
    polygon = Polygon([[p.x, p.y] for p in points])
    return polygon

