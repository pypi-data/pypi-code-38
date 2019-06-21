"""
module for generating bravais lattices.
"""
import numpy as np


def create_lattice_vector(vector, angle):
    """
    Generates the component of a lattice vector given an angle.

    Args:
        vector (np.array): the first vector
        angle  (int): the angle in degrees.
    """
    radians = np.radians(angle)
    cos, sin = np.cos(radians), np.sin(radians)
    rotation_matrix = np.array([[cos, sin], [-sin, cos]])
    a_vec = np.array(vector)
    b_vec = np.dot(rotation_matrix, a_vec)
    return b_vec, a_vec


def create_lattice(shape, lattice_vectors, slicer=None):
    """
    Generates a lattice given a shape and lattice vectors

    Args:
       shape (tuple): shape of the lattice in a grid of points
       lattice_vectors (np.array): a pair of lattice vectors
       slicer (func): takes a function that knows how to remove points from  the lattice.
    """
    # Translate along one vector to fill up the bottom row.
    x_pts = np.arange(0, shape[0])
    x_component = lattice_vectors[0][0]*x_pts
    y_component = lattice_vectors[0][1]*x_pts
    base = np.dstack((x_component, y_component))
    # now copy this array N times
    points = np.array([x*np.array(lattice_vectors[1]) +
                       base for x in range(0, shape[1])]).reshape(shape[0]*shape[1], 2)

    if slicer is not None:
        points = slicer(points)

    return points


def _centroid(points):
    """
    Finds the center of a bunch of points.

    Args:
        points (np.array): points of which we will find the center.
    """
    length = points.shape[0]
    sum_x = np.sum(points[:, 0])
    sum_y = np.sum(points[:, 1])
    return sum_x / length, sum_y / length


def radial_slicer(radius):
    """
    Wrapper for methods using a radial slicer.

    Args:
        radius (float): a float representing how far from the center to cut points
    """
    def func(points):
        """
        Function to remove points outside of a radius from the center

        Args:
            points (np.array): an array of points
        """
        center = _centroid(points)
        res = [point for point in points if np.linalg.norm(point-center) <= radius]
        return np.array(res)

    return func
