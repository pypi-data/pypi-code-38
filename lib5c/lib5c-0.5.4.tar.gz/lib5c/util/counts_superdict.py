"""
Module for creating and performing operations on ``counts_superdict`` data
structures. ``counts_superdict`` data structures areconceptually just
collections of named counts dicts. Typically, the members of the collection
correspond to replicates or conditions in a 5C experiment. ``counts_superdict``
data structures are implemented as dicts of dicts of 2D numpy arrays as shown in
this example::

    counts_superdict[replicate_name][region_name] = 2D numpy array

Here the innermost values are the square symmetric 2D numpy arrays representing
the counts for the specified replicate and region. In other words, they are a
dict whose keys are replicate names as strings and whose values are standard
counts data structures. See ``lib5c.parsers.counts.load_counts()`` or
``lib5c.parsers.counts.load_primer_counts()``.
"""

from copy import deepcopy

import numpy as np
from scipy import stats

from lib5c.util.counts import calculate_pvalues, flatten_counts_to_list,\
    unflatten_counts_from_list


def make_atlas(counts_superdict, pvalues_superdict=None,
               distribution=stats.norm, percentile_threshold=None):
    """
    Computes the maximum counts and minimum p-values for each region of a 5C
    dataset across multiple replicates or conditions.

    Parameters
    ----------
    counts_superdict : dict of counts dicts
        The counts for all replicates or conditions to be used to generate the
        atlas. The keys are the replicate or condition names, the values are
        standard counts dicts containing the counts for that replicate. See
        ``lib5c.parsers.counts.load_counts()`` or
        ``lib5c.parsers.counts.load_primer_counts()``.
    pvalues_superdict : dict of counts dicts or None
        The counts for all replicates or conditions to be used to generate the
        atlas. The keys are the replicate or condition names, the values are
        standard counts dicts containing the p-values for that replcicate. If
        None is passed, the p-values will be automatically computed using
        ``lib5c.util.counts.calculate_regional_pvalues()``.
    distribution : subclass of scipy.stats.rv_continuous
        If pvalue_superdict is None, this kwarg specifies the distribution to
        use when modeling the counts.
    percentile_threshold : float between 0 and 100 or None
        If passed, all p-value modeling kwargs are ignored and all p-value
        modeling steps are skipped. Instead, the returned atlas peaks will
        contain a dummy p-value, which will be 0.0 whenever the peak passes the
        percentile threshold, and 1.0 otherwise.

    Returns
    -------
    (counts dict, counts dict) tuple
        The first element in the tuple is the counts dict contatining the
        maximum counts observed across all replicates at each primer or bin
        combination in each region. The second element in the tuple is the
        parallel counts dict containing the corresponding minimum p-values.
    """
    # determine replicates and regions
    replicates = counts_superdict.keys()
    regions = counts_superdict[replicates[0]].keys()

    # genereate pvalues_superdict if None was passed
    if not pvalues_superdict:
        pvalues_superdict = make_pvalues_superdict(
            counts_superdict, distribution=distribution,
            percentile_threshold=percentile_threshold)

    # compute atlas
    max_counts = deepcopy(counts_superdict[replicates[0]])
    min_pvalues = deepcopy(pvalues_superdict[replicates[0]])
    for rep in replicates:
        for region in regions:
            for i in range(len(max_counts[region])):
                for j in range(len(max_counts[region])):
                    if counts_superdict[rep][region][i, j] > \
                            max_counts[region][i, j]:
                        max_counts[region][i, j] = \
                            counts_superdict[rep][region][i, j]
                        min_pvalues[region][i, j] = \
                            pvalues_superdict[rep][region][i, j]

    return max_counts, min_pvalues


def make_pvalues_superdict(counts_superdict, distribution=stats.norm,
                           percentile_threshold=None):
    """
    Makes a counts_superdict-like data structure containing automatically
    computed p-values for each replicate for each region. The counts within each
    region are modeled independently for each replicate using the distribution
    specified by the distribution kwarg. See
    ``lib5c.util.counts.calculate_regional_pvalues()``.

    Parameters
    ----------
    counts_superdict : dict of counts dicts
        The counts for all replicates or conditions for which p-values should be
        computed. The keys are the replicate or condition names, the values are
        standard counts dicts containing the counts for that replicate. See
        ``lib5c.parsers.counts.load_counts()`` or
        ``lib5c.parsers.counts.load_primer_counts()``.
    distribution : subclass of scipy.stats.rv_continuous
        The distribution to use when modeling the counts.
    percentile_threshold : float between 0 and 100 or None
        If passed, the distribution kwarg is ignored and p-value modeling is
        skipped. Instead, the returned data struture will contain dummy
        p-values, which will be 0.0 whenever the peak passes the percentile
        threshold, and 1.0 otherwise. This percentile threshold is applied
        independently for each region and each replicate.

    Returns
    -------
    dict of counts dicts
        A parallel data structure containing the corresponding p-values.
    """

    return {rep: calculate_pvalues(counts_superdict[rep], distribution,
                                   percentile_threshold)[0]
            for rep in counts_superdict.keys()}


def make_atlas_peaks(counts_superdict, pvalues_superdict=None, max_counts=None,
                     min_pvalues=None, distribution=stats.norm,
                     percentile_threshold=None):
    """
    Reshapes count and p-value information across multiple replicates into a
    peaks data structure compatible with the ``lib5c.algorithms.clustering``
    subpackage.

    Parameters
    ----------
    counts_superdict : dict of counts dicts
        The counts for all replicates or conditions to be used to generate the
        atlas. The keys are the replicate or condition names, the values are
        standard counts dicts containing the counts for that replicate. See
        ``lib5c.parsers.counts.load_counts()`` or
        ``lib5c.parsers.counts.load_primer_counts()``.
    pvalues_superdict : dict of counts dicts or None
        The p-values for all replicates or conditions to be used to generate the
        atlas. The keys are the replicate or condition names, the values are
        standard counts dicts containing the p-values for that replicate. See
        ``lib5c.parsers.counts.load_counts()`` or
        ``lib5c.parsers.counts.load_primer_counts()``. If None is passed,
        p-values will be automatically computed for each replicate for each
        region by modeling each region within each replicate independently with
        the distribution specified by the distribution kwarg. See
        ``lib5c.util.counts.calculate_regional_pvalues()``.
    max_counts : counts dict or None
        A standard counts dict containing the maximum count value observed for
        every interaction in each region across all replicates. If None is
        passed, this will be computed automatically based on the
        ``counts_superdict``. See ``lib5c.util.counts.make_atlas()``.
    min_pvalues : counts dict or None
        A standard counts dict containing the minimum p-value observed for every
        interaction in each region across all replicates. If None is passed,
        this will be computed automatically based on the ``pvalues_superdict``.
        See ``lib5c.util.counts.make_atlas()``.
    distribution : subclass of scipy.stats.rv_continuous
        If pvalue_superdict is None, this kwarg specifies the distribution to
        use when modeling the counts.
    percentile_threshold : float between 0 and 100 or None
        If passed, all p-value modeling kwargs are ignored and all p-value
        modeling steps are skipped. Instead, the returned atlas peaks will
        contain a dummy p-value, which will be 0.0 whenever the peak passes the
        percentile threshold, and 1.0 otherwise.

    Returns
    -------
    complex dict structure
        The returned peaks data structure has the following structure::

            atlas_peaks[region_name] = {
                                           'x': int,
                                           'y': int,
                                           'value': float,
                                           'pvalue': float,
                                           'replicates' : {
                                               rep_name: {
                                                   'value': float,
                                                   'pvalue': float
                                               }
                                           }
                                       }

        Here ``region_name`` is a string referring to the region name. The 'x'
        and 'y' keys describe the x- and y-coordinate of the peak, respectively.
        The 'value' and 'pvalue' keys describe the max count and minimum p-value
        observed at those coordinates within the specified region across all
        replicates. The 'replicates' key's value is a dict containing more
        information about the values and p-values observed at the specified
        coordinates in each of the replicates in the original counts_superdict
        and pvalues_superdict.

    Notes
    -----
    Only the lower-triangular and diagonal elements (those for which the
    x-coordinate is greater than or equal to the y-coordinate) of each region's
    counts are included in the returned data structure to prevent duplication of
    data.
    """

    # deduce replicates and regions
    replicates = counts_superdict.keys()
    regions = counts_superdict[replicates[0]].keys()

    # create pvalues_superdict if not present
    if not pvalues_superdict:
        pvalues_superdict = make_pvalues_superdict(
            counts_superdict, distribution=distribution,
            percentile_threshold=percentile_threshold)
    # compute max_counts and min_pvalues if not present
    if (not max_counts) or (not min_pvalues):
        max_counts, min_pvalues = make_atlas(counts_superdict,
                                             pvalues_superdict)

    # make atlas peaks
    atlas_peaks = {}
    for region in regions:
        atlas_peaks[region] = []
        for i in range(len(max_counts[region])):
            for j in range(i+1):
                peak_dict = {'x': i,
                             'y': j,
                             'value': max_counts[region][i, j],
                             'pvalue': min_pvalues[region][i, j],
                             'replicates': {}}
                for rep in replicates:
                    peak_dict['replicates'][rep] = {
                        'value' : counts_superdict[rep][region][i, j],
                        'pvalue': pvalues_superdict[rep][region][i, j]}

                atlas_peaks[region].append(peak_dict)

    return atlas_peaks


def counts_superdict_to_matrix(counts_superdict, rep_order=None,
                               region_order=None, discard_nan=False):
    """
    Convert a counts_superdict structure to a matrix.

    Parameters
    ----------
    counts_superdict : Dict[Dict[np.ndarray]]
        The keys of the outer dict are replicate names, the keys of the inner
        dict are region names, the values are square symmetric arrays of counts
        for the specified replicate and region.
    rep_order : Optional[List[str]]
        The order in which the replicates should be arranged. Pass None to use
        the order of ``counts_superdict.keys()``.
    region_order : Optional[List[str]]
        The order in which the regions should be concatenated. Pass None to use
        the order of the keys.
    discard_nan : bool
        If True, positions containing ``nan`` values will be removed.

    Returns
    -------
    np.ndarray
        Each row is a replicate, each column is a position. The order of the
        columns is described in ``lib5c.util.counts.flatten_counts_to_list()``,
        honoring the passed region order.

    Examples
    --------
    >>> import numpy as np
    >>> counts_superdict = {'Rep1': {'A': np.array([[1, 2], [2, 3]]),
    ...                              'B': np.array([[4, 8], [8, 10]])},
    ...                     'Rep2': {'A': np.array([[3, 5], [5, 6]]),
    ...                              'B': np.array([[7, 9], [9, np.nan]])}}
    >>> rep_order = ['Rep1', 'Rep2']
    >>> region_order = ['A', 'B']
    >>> counts_superdict_to_matrix(counts_superdict, rep_order, region_order)
    array([[  1.,   2.,   3.,   4.,   8.,  10.],
           [  3.,   5.,   6.,   7.,   9.,  nan]])
    >>> counts_superdict_to_matrix(counts_superdict, rep_order, region_order,
    ...                            discard_nan=True)
    array([[1., 2., 3., 4., 8.],
           [3., 5., 6., 7., 9.]])
    """
    # default rep_order
    if rep_order is None:
        rep_order = counts_superdict.keys()

    # default region_order
    if region_order is None:
        region_order = counts_superdict[rep_order[0]].keys()

    # create matrix
    matrix = np.array([flatten_counts_to_list(counts_superdict[rep],
                                              region_order=region_order,
                                              discard_nan=False)
                       for rep in rep_order])

    # discard nans
    if discard_nan:
        matrix = matrix[:, ~np.isnan(matrix).any(axis=0)]

    return matrix


def matrix_to_counts_superdict(matrix, rep_order, region_order, pixelmap):
    """
    Converts a matrix back into a counts_superdict structure.

    Parameters
    ----------
    matrix : np.ndarray
        The matrix to convert to a counts superdict. The rows are replicates,
        the columns are bin-bin pairs or FFLJs.
    rep_order : list of str
        The replicate names to use in the counts_superdict, in the order of the
        columns of ``matrix``.
    region_order : list of str
        The order in which the regions were concatenated down the rows of
        ``matrix``.
    pixelmap : pixelmap
        Needed to precompute the size of each region when preparing the
        counts_superdict.

    Returns
    -------
    counts_superdict
        The counts_superdict representation of the input matrix.

    Examples
    --------
    >>> import numpy as np
    >>> matrix = np.array([[1, 2, 3, 4, 8, 10],
    ...                    [3, 5, 6, 7, 9, np.nan]])
    >>> rep_order = ['Rep1', 'Rep2']
    >>> region_order = ['A', 'B']
    >>> pixelmap = {'A': [{}, {}], 'B': [{}, {}]}
    >>> matrix_to_counts_superdict(matrix, rep_order, region_order, pixelmap)
    {'Rep2': {'A': array([[3., 5.],
                          [5., 6.]]),
              'B': array([[ 7.,  9.],
                          [ 9., nan]])},
     'Rep1': {'A': array([[1., 2.],
                          [2., 3.]]),
              'B': array([[ 4.,  8.],
                          [ 8., 10.]])}}
    """
    counts_superdict = {}
    for i in range(len(rep_order)):
        counts_superdict[rep_order[i]] = unflatten_counts_from_list(
            matrix[i, :], region_order, pixelmap)
    return counts_superdict
