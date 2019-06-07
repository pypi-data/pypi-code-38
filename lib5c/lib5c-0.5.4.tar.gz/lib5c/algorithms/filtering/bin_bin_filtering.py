"""
Module for smoothing bin-level 5C interaction matrices.
"""

import numpy as np

from lib5c.algorithms.filtering.util import filter_selector
from lib5c.util.primers import guess_bin_step
from lib5c.util.parallelization import parallelize_regions


def find_nearby_bins(index, regional_pixelmap, threshold):
    """
    Finds the bins near a target bin as specified by an index.

    Parameters
    ----------
    index : int
        The index of the bin to look near.
    regional_pixelmap : List[Dict[str, Any]]
        The list of bins in this region.
    threshold : int
        The threshold for deciding if a bin is "nearby" or not, as a distance in
        base pairs.

    Returns
    -------
    List[Dict[str, int]]
        A list of nearby bins, where each nearby bin is represented as a dict of
        the following form::

            {
                'index': int,
                'distance': int
            }

        where 'index' is the index of the bin within the region and 'distance'
        is the distance between this bin and the target bin.
    """
    # convert the threshold into units of bins
    bin_step = guess_bin_step(regional_pixelmap)
    bin_threshold = int((threshold - bin_step / 2) / bin_step)

    # a list of nearby bins to fill in
    nearby_bins = [{'index': index, 'distance': 0}]

    # fill in the nearby_bins list
    for i in range(index - bin_threshold, index + bin_threshold + 1):
        if 0 <= i < len(regional_pixelmap):
            nearby_bins.append({'index'   : i,
                                'distance': abs(index - i) * bin_step})

    return nearby_bins


@parallelize_regions
def bin_bin_filter(array, filter_function, regional_pixelmap, threshold,
                   filter_kwargs=None):
    """
    Convenience function for filtering a bin-level matrix to a bin-level matrix.

    Parameters
    ----------
    array : np.ndarray
        The matrix to filter.
    filter_function : Callable[[List[Dict[str, Any]]], float]
        The filter function to use when filtering. This function should take in
        a "neighborhood" and return the filtered value given that neighborhood.
        A neighborhood is represented as a list of "nearby points" where each
        nearby point is represented as a dict of the following form::

            {
                'value': float,
                'x_dist': int,
                'y_dist': int
            }

        where 'value' is the value at the point and 'x_dist' and 'y_dist' are
        its distances from the center of the neighborhood along the x- and
        y-axis, respectively, in base pairs. See
        ``lib5c.algorithms.filtering.filter_functions`` for examples of filter
        functions and how they can be created.
    regional_pixelmap : List[Dict[str, Any]]
        The list of bins in this region.
    threshold : int
        The threshold for defining the size of the neighborhood passed to the
        filter function, in base pairs.
    filter_kwargs : Optional[Dict[str, Any]]
        Kwargs to be passed to the ``filter_function``.

    Returns
    -------
    np.ndarray
        The filtered matrix.
    """
    # resolve function_kwargs
    if filter_kwargs is None:
        filter_kwargs = {}

    output = np.array(array)

    nearby_bins = [find_nearby_bins(i, regional_pixelmap, threshold)
                   for i in range(len(output))]

    for i in range(len(output)):
        for j in range(i + 1):
            value = filter_function(filter_selector(
                array, nearby_bins[i], nearby_bins[j]),
                **filter_kwargs)
            output[i, j] = value
            output[j, i] = value

    return output


def bin_bin_filter_counts(counts, function, pixelmap, threshold,
                          function_kwargs=None):
    """
    Non-parallel wrapper for ``bin_bin_filter()``. Deprecated now that
    ``bin_bin_filter()`` is decorated with ``@parallelize_regions``.

    Parameters
    ----------
    counts : Dict[str, np.ndarray]
        The counts dict to filter.
    function : Callable[[List[Dict[str, Any]]], float]
        The filter function to use for filtering. See the description of the
        ``filter_function`` arg in ``bin_bin_filter()``.
    pixelmap : Dict[str, List[Dict[str, Any]]]
        The pixelmap describing the bins for ``counts``.
    threshold : int
        The threshold for defining the size of the neighborhood passed to the
        filter function, in base pairs.
    function_kwargs : Optional[Dict[str, Any]]
        Kwargs to be passed to the ``function``.

    Returns
    -------
    Dict[str, np.ndarray]
        The dict of filtered counts.
    """
    return {region: bin_bin_filter(
        counts[region], function, pixelmap[region], threshold,
        filter_kwargs=function_kwargs)
        for region in counts.keys()}
