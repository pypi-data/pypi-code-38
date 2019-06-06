"""
Module for mathematical utility functions.
"""

import numpy as np


def gmean(array, pseudocount=1, axis=None):
    """
    Compute the geometric mean of an input array.

    Parameters
    ----------
    array : np.ndarray
        The array to take the geometric mean over.
    pseudocount : float
        The pseudocount to add to the elements of ``array`` before logging.
    axis : int, optional
        The axis to compute the mean over.

    Returns
    -------
    float
        The geometric mean.
    """
    return np.exp(np.nanmean(
        np.log(array + pseudocount), axis=axis)) - pseudocount


def zero_nans(array):
    """
    Zeros all the nan's in an array. Useful for cases where functions like
    `np.nansum()` are not available (e.g., `scipy.ndimage.convolve()`).

    Parameters
    ----------
    array : np.ndarray
        The array to zero nan's in.

    Returns
    -------
    np.ndarray
        Copy of `array` with all nan's set to zero.
    """
    array = np.copy(array)
    array[np.isnan(array)] = 0.0
    return array


def symmetrize(array, source='lower'):
    """
    Symmetrizes a square array using its lower triangular entries.

    Parameters
    ----------
    array : np.ndarray
        Array to symmetrize. Must be square.
    source : {'lower', 'upper'}
        What triangle of the matrix to symmetrize with.

    Returns
    -------
    np.ndarray
        A symmetrized copy of ``array``.
    """
    assert len(array.shape) == 2 and array.shape[0] == array.shape[1]
    array = np.copy(array)
    tril_indices = np.tril_indices(array.shape[0], k=-1)
    triu_indices = tuple(reversed(tril_indices))
    if source == 'lower':
        array[triu_indices] = array[tril_indices]
    elif source == 'upper':
        array[tril_indices] = array[triu_indices]
    else:
        raise ValueError('source must be upper or lower')
    return array
