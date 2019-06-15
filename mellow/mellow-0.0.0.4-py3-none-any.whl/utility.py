import numpy as np

def distance(p1, p2):
    """ calculates the distance between two points in euclidean space
    :param p1: numpy.array - euclidean coordinates
    :param p2: numpy.array - euclidean coordinates
    :return: numpy.float64
    """
    return np.sum((p2 - p1) ** 2) ** .5

