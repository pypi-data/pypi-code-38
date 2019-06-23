import numpy as np


def distance(self, p1, p2):
    """
    It is used to calculate the distance bewteen two points in Eucilidean Space
    :param p1: coordinate of point one in Eucilidean Space
    :param p2: coordinate of point two in Eucilidean Space
    :return: distance between p1 and p2 float value
    """
    return np.sum((p2 - p1) ** 2) ** .5