"""Module containing utility functions for manipulating numpy arrays."""

import sys
from functools import wraps

import random

import numpy as np

from dtoolbioimage.util.color import pretty_color_palette, unique_color_palette

def reduce_stack(array3D, z_function):
    """Return 2D array projection of the input 3D array.

    The input function is applied to each line of an input x, y value.

    :param array3D: 3D numpy.array
    :param z_function: function to use for the projection (e.g. :func:`max`)
    """
    xmax, ymax, _ = array3D.shape
    projection = np.zeros((xmax, ymax), dtype=array3D.dtype)
    for x in range(xmax):
        for y in range(ymax):
            projection[x, y] = z_function(array3D[x, y, :])
    return projection


def map_stack(array3D, z_function):
    """Return 3D array where each z-slice has had the function applied to it.

    :param array3D: 3D numpy.array
    :param z_function: function to be mapped to each z-slice
    """
    _, _, zdim = array3D.shape
    return np.dstack([z_function(array3D[:, :, z]) for z in range(zdim)])


def color_array(array, color_dict):
    """Return RGB color array.

    Assigning a unique RGB color value to each unique element of the input
    array and return an array of shape (array.shape, 3).

    :param array: input numpy.array
    :param color_dict: dictionary with keys/values corresponding to identifiers
                       and RGB tuples respectively
    """
    output_array = np.zeros(array.shape + (3,), np.uint8)
    unique_identifiers = set(np.unique(array))
    for identifier in unique_identifiers:
        output_array[np.where(array == identifier)] = color_dict[identifier]
    return output_array


def pretty_color_array(array, keep_zero_black=True):
    """Return a RGB pretty color array.

    Assigning a pretty RGB color value to each unique element of the input
    array and return an array of shape (array.shape, 3).

    :param array: input numpy.array
    :param keep_zero_black: whether or not the background should be black
    :returns: numpy.array
    """
    unique_identifiers = set(np.unique(array))
    color_dict = pretty_color_palette(unique_identifiers, keep_zero_black)
    return color_array(array, color_dict)


def unique_color_array(array):
    """Return a RGB unique color array.

    Assigning a unique RGB color value to each unique element of the input
    array and return an array of shape (array.shape, 3).

    :param array: input numpy.array
    :returns: numpy.array
    """
    unique_identifiers = set(np.unique(array))
    color_dict = unique_color_palette(unique_identifiers)
    return color_array(array, color_dict)
