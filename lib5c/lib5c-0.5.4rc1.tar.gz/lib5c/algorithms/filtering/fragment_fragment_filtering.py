"""
Module for smoothing fragment-level 5C interaction matrices.
"""

import numpy as np

from lib5c.algorithms.filtering.util import filter_selector
from lib5c.util.bed import get_midpoint
from lib5c.util.parallelization import parallelize_regions


def find_nearby_fragments(index, regional_primermap, threshold, midpoint=False):
    """
    Finds the fragments near a target fragment as specified by an index.

    Parameters
    ----------
    index : int
        The index of the bin to look near.
    regional_primermap : List[Dict[str, Any]]
        The list of fragments in this region.
    threshold : int
        The threshold for deciding if a fragment is "nearby" or not,  as a
        distance in base pairs.
    midpoint : bool
        Pass True to restore legacy behavior when distances to fragments were
        based on their midpoints. The new behavior (with this kwarg set to
        False) is to compute distances to fragments based on their closest
        endpoint.

    Returns
    -------
    List[Dict[str, int]]
        A list of nearby fragments, where each nearby bin is represented as a
        dict of the following form::

            {
                'index': int,
                'distance': int
            }

        where 'index' is the index of the fragment within the region and
        'distance' is the distance between this fragment and the target
        fragment.
    """
    # define distance
    if midpoint:
        def left_distance(coord, frag):
            return coord - get_midpoint(frag)

        def right_distance(coord, frag):
            return get_midpoint(frag) - coord
    else:
        def left_distance(coord, frag):
            return coord - frag['end']

        def right_distance(coord, frag):
            return frag['start'] - coord

    # establish key fragment
    key_fragment = regional_primermap[index]

    # establish coordinates
    coordinate = get_midpoint(key_fragment)

    # list of indices that are nearby
    nearby_fragments = [{'index': index, 'distance': 0}]

    # step left, starting from the original index
    i = index
    distance = 0
    while distance < threshold:
        i -= 1
        if i < 0:
            break
        distance = left_distance(coordinate, regional_primermap[i])
        nearby_fragments.append({'index': i, 'distance': distance})

    # step right
    i = index
    distance = 0
    while distance < threshold:
        i += 1
        if i >= len(regional_primermap):
            break
        distance = right_distance(coordinate, regional_primermap[i])
        nearby_fragments.append({'index': i, 'distance': distance})

    return nearby_fragments


@parallelize_regions
def fragment_fragment_filter(array, filter_function, regional_primermap,
                             threshold, filter_kwargs=None, midpoint=False):
    """
    Convenience function for filtering a fragment-level matrix to a
    fragment-level matrix.

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
    regional_primermap : List[Dict[str, Any]]
        The list of fragments in this region.
    threshold : int
        The threshold for defining the size of the neighborhood passed to the
        filter function, in base pairs.
    filter_kwargs : Optional[Dict[str, Any]]
        Kwargs to be passed to the ``filter_function``.
    midpoint : bool
        Pass True to restore legacy behavior when distances to fragments were
        based on their midpoints. The new behavior (with this kwarg set to
        False) is to compute distances to fragments based on their closest
        endpoint.

    Returns
    -------
    np.ndarray
        The filtered matrix.
    """
    # resolve function_kwargs
    if filter_kwargs is None:
        filter_kwargs = {}

    output = np.array(array)

    nearby_fragments = [find_nearby_fragments(i, regional_primermap, threshold,
                                              midpoint=midpoint)
                        for i in range(len(output))]

    for i in range(len(output)):
        for j in range(i + 1):
            value = filter_function(filter_selector(
                array, nearby_fragments[i], nearby_fragments[j]),
                **filter_kwargs)
            output[i, j] = value
            output[j, i] = value

    return output


def fragment_fragment_filter_counts(counts, function, primermap, threshold,
                                    function_kwargs=None, midpoint=False):
    """
    Non-parallel wrapper for ``fragment_fragment_filter()``. Deprecated now that
    ``fragment_fragment_filter()`` is decorated with ``@parallelize_regions``.

    Parameters
    ----------
    counts : Dict[str, np.ndarray]
        The counts dict to filter.
    function : Callable[[List[Dict[str, Any]]], float]
        The filter function to use for filtering. See the description of the
        ``filter_function`` arg in ``fragment_fragment_filter()``.
    primermap : Dict[str, List[Dict[str, Any]]]
        The primermap describing the fragments for ``counts``.
    threshold : int
        The threshold for defining the size of the neighborhood passed to the
        filter function, in base pairs.
    function_kwargs : Optional[Dict[str, Any]]
        Kwargs to be passed to the ``function``.
    midpoint : bool
        Pass True to restore legacy behavior when distances to fragments were
        based on their midpoints. The new behavior (with this kwarg set to
        False) is to compute distances to fragments based on their closest
        endpoint.

    Returns
    -------
    Dict[str, np.ndarray]
        The dict of filtered counts.
    """
    return {region: fragment_fragment_filter(
        counts[region], function, primermap[region], threshold,
        filter_kwargs=function_kwargs, midpoint=midpoint)
        for region in counts.keys()}
