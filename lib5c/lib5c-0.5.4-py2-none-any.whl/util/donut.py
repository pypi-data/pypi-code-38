"""
Module containing utility functions related to creating and using donut-shaped
windows in the style of Rao et al. (Cell 2014).
"""

import numpy as np


def donut_footprint(p, w):
    """
    Constructs a donut footprint matrix.

    Parameters
    ----------
    p : int
        The inner radius of the donut.
    w : int
        The outer radius of the donut.

    Returns
    -------
    np.ndarray with int dtype
        Square matrix containing 1s in the positions selected by the footprint
        and 0s in the positions ignored by the footprint.

    Notes
    -----
    This function is duplicated in lib5c.algorithms.donut_filters.donut_filt()
    to preserve easy synchronization of that inherited module.

    Examples
    --------
    >>> donut_footprint(1, 3)
    array([[1, 1, 1, 0, 1, 1, 1],
           [1, 1, 1, 0, 1, 1, 1],
           [1, 1, 0, 0, 0, 1, 1],
           [0, 0, 0, 0, 0, 0, 0],
           [1, 1, 0, 0, 0, 1, 1],
           [1, 1, 1, 0, 1, 1, 1],
           [1, 1, 1, 0, 1, 1, 1]])
    """
    return np.array([
        [1 if i != w and ((i > p + w or i < w - p) or (j < w - p or j > p + w))
         and j != w else 0
         for i in xrange(2 * w + 1)] for j in xrange(2 * w + 1)])


def lower_left_footprint(p, w):
    """
    Creates a lower left donut filter footprint.

    Parameters
    ----------
    p : int
        Inner radius of donut.
    w : int
        Outer radius of donut.

    Returns
    -------
    np.ndarray
        The desired footprint. Square array with shape `(2*w+1, 2*w+1)`.
    """
    return np.array([
        [1 if (j > w + p and i < w) or (j > w and i < w - p)
         else 0 for i in xrange(2 * w + 1)]
        for j in xrange(2 * w + 1)])


def make_donut_selector(i, j, p, w, n):
    """
    Creates a boolean selector array with a donut shape around a particular
    coordinate to be used to index into a square matrix of known size.

    Parameters
    ----------
    i : int
        The row index of the point around which the donut should be constructed.
    j : int
        The column index of the point around which the donut should be
        constructed.
    p : int
        The inner radius of the donut.
    w : int
        The outer radius of the donut.
    n : int
        The size of the target matrix.

    Returns
    -------
    np.ndarray
        The donut selector. It will have boolean dtype and shape (n, n).

    Examples
    --------
    >>> make_donut_selector(5, 4, 1, 3, 10).astype(int)
    array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 1, 1, 1, 0, 1, 1, 1, 0, 0],
           [0, 1, 1, 1, 0, 1, 1, 1, 0, 0],
           [0, 1, 1, 0, 0, 0, 1, 1, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 1, 1, 0, 0, 0, 1, 1, 0, 0],
           [0, 1, 1, 1, 0, 1, 1, 1, 0, 0],
           [0, 1, 1, 1, 0, 1, 1, 1, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])
    >>> make_donut_selector(5, 1, 1, 3, 10).astype(int)
    array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [1, 0, 1, 1, 1, 0, 0, 0, 0, 0],
           [1, 0, 1, 1, 1, 0, 0, 0, 0, 0],
           [0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
           [1, 0, 1, 1, 1, 0, 0, 0, 0, 0],
           [1, 0, 1, 1, 1, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])
    >>> make_donut_selector(5, 8, 1, 3, 10).astype(int)
    array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 1, 1, 1, 0, 1],
           [0, 0, 0, 0, 0, 1, 1, 1, 0, 1],
           [0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
           [0, 0, 0, 0, 0, 1, 1, 1, 0, 1],
           [0, 0, 0, 0, 0, 1, 1, 1, 0, 1],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])
    >>> make_donut_selector(1, 5, 1, 3, 10).astype(int)
    array([[0, 0, 1, 1, 0, 0, 0, 1, 1, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 1, 1, 0, 0, 0, 1, 1, 0],
           [0, 0, 1, 1, 1, 0, 1, 1, 1, 0],
           [0, 0, 1, 1, 1, 0, 1, 1, 1, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])
    >>> make_donut_selector(8, 5, 1, 3, 10).astype(int)
    array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 1, 1, 1, 0, 1, 1, 1, 0],
           [0, 0, 1, 1, 1, 0, 1, 1, 1, 0],
           [0, 0, 1, 1, 0, 0, 0, 1, 1, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 1, 1, 0, 0, 0, 1, 1, 0]])
    """
    footprint = donut_footprint(p, w)
    top_pad, top_crop = pad_and_crop(i, w, 0)
    bottom_pad, bottom_crop = pad_and_crop(i, w, n-1)
    left_pad, left_crop = pad_and_crop(j, w, 0)
    right_pad, right_crop = pad_and_crop(j, w, n-1)
    padded = np.pad(footprint, [[top_pad, bottom_pad], [left_pad, right_pad]],
                    mode='constant', constant_values=0)
    cropped = padded[top_crop:padded.shape[0]-bottom_crop,
                     left_crop:padded.shape[1]-right_crop]
    return cropped.astype(bool)


def pad_and_crop(x, margin, limit):
    """
    Utility function to assist in padding and cropping footprints.

    Parameters
    ----------
    x : int
        The coordinate of the point in question.
    margin : int
        The size of a buffer around x which should not be included in the
        padding. In the context of padding and cropping footprints, this is the
        outer radius of the footprint. Whatever part of the margin extends
        beyond the limit must be cropped away.
    limit : int
        The coordinate of the edge (extreme allowed index) of the desired final
        matrix.

    Returns
    -------
    int, int
        The first int is the number of pixels to pad by, the second is the
        number of pixels that must be cropped away after padding.

    Examples
    --------
    >>> pad_and_crop(0, 3, 0)
    (0, 3)
    >>> pad_and_crop(5, 3, 5)
    (0, 3)
    >>> pad_and_crop(3, 3, 0)
    (0, 0)
    >>> pad_and_crop(3, 2, 5)
    (0, 0)
    >>> pad_and_crop(5, 3, 0)
    (2, 0)
    >>> pad_and_crop(3, 3, 10)
    (4, 0)
    """
    distance = abs(limit - x)
    return max(distance - margin, 0), -min(distance - margin, 0)
