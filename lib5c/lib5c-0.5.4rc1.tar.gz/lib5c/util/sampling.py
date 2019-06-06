"""
Module providing utilities related to sampling.
"""

import numpy as np


def uniform_range_coverage_sample(data, n_points, log_space=False):
    """
    Performs a deterministic "sampling" step that draws the requested number of
    evenly-spaced samples from the data.

    Even-spacing can be defined in terms of the native space of the data, or in
    terms of log space.

    The marginal distribution of the drawn samples should be approximately
    uniform - it will not match the empirical distribution of ``data``.

    Parameters
    ----------
    data : np.ndarray
        The data to sample from.
    n_points : int
        The number of points to sample
    log_space : bool
        Pass True to space the points evenly in log space, otherwise the points
        will be spaced evenly in the native space of ``data``.
    """
    sorted_data = np.sort(data)
    if log_space:
        linspace = np.logspace(np.log10(sorted_data[0]),
                               np.log10(sorted_data[-1]),
                               n_points)
    else:
        linspace = np.linspace(sorted_data[0], sorted_data[-1], n_points)
    data_pointer = 0
    linspace_pointer = 0
    samples = []
    while data_pointer < len(sorted_data) and linspace_pointer < len(linspace):
        if sorted_data[data_pointer] >= linspace[linspace_pointer]:
            samples.append(sorted_data[data_pointer])
            linspace_pointer += 1
        else:
            data_pointer += 1
    return np.array(samples)
