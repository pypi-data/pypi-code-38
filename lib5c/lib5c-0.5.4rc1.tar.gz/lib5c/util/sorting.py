"""
Module providing utility functions related to sorting data.
"""

import numpy as np


def rankdata_plus(a, method='average'):
    """
    Assign ranks to data, dealing with ties appropriately.

    Slight modification of ``scipy.stats.rankdata()`` that returns the sorter in
    addition to the ranks; this allows the sort information to be re-used
    without having to sort again.

    Ranks begin at 1.  The `method` argument controls how ranks are assigned
    to equal values.  See [1]_ for further discussion of ranking methods.

    Parameters
    ----------
    a : array_like
        The array of values to be ranked.  The array is first flattened.
    method : str, optional
        The method used to assign ranks to tied elements.
        The options are 'average', 'min', 'max', 'dense' and 'ordinal'.

        'average':
            The average of the ranks that would have been assigned to
            all the tied values is assigned to each value.
        'min':
            The minimum of the ranks that would have been assigned to all
            the tied values is assigned to each value.  (This is also
            referred to as "competition" ranking.)
        'max':
            The maximum of the ranks that would have been assigned to all
            the tied values is assigned to each value.
        'dense':
            Like 'min', but the rank of the next highest element is assigned
            the rank immediately after those assigned to the tied elements.
        'ordinal':
            All values are given a distinct rank, corresponding to the order
            that the values occur in `a`.

        The default is 'average'.

    Returns
    -------
    ranks, sorter : ndarray, ndarray
         Ranks is an array of length equal to the size of `a`, containing rank
         scores. Sorter is the argsort result from the initial sorting.

    References
    ----------
    .. [1] "Ranking", http://en.wikipedia.org/wiki/Ranking

    Examples
    --------
    >>> from lib5c.util.sorting import rankdata_plus
    >>> np.array_equal(rankdata_plus([0, 2, 3, 2])[1],  # the sorter
    ...                np.array([0, 1, 3, 2]))
    True
    >>> np.array_equal(rankdata_plus([0, 2, 3, 2])[0],  # the ranks
    ...                np.array([1., 2.5, 4., 2.5]))
    True
    >>> np.array_equal(rankdata_plus([0, 2, 3, 2], 'min')[0],  # the ranks
    ...                np.array([1, 2, 4, 2]))
    True
    >>> np.array_equal(rankdata_plus([0, 2, 3, 2], 'max')[0],  # the ranks
    ...                np.array([1, 3, 4, 3]))
    True
    >>> np.array_equal(rankdata_plus([0, 2, 3, 2], 'dense')[0],  # the ranks
    ...                np.array([1, 2, 3, 2]))
    True
    >>> np.array_equal(rankdata_plus([0, 2, 3, 2], 'ordinal')[0],  # the ranks
    ...                np.array([1, 2, 4, 3]))
    True
    """
    if method not in ('average', 'min', 'max', 'dense', 'ordinal'):
        raise ValueError('unknown method "{0}"'.format(method))

    arr = np.ravel(np.asarray(a))
    algo = 'mergesort' if method == 'ordinal' else 'quicksort'
    sorter = np.argsort(arr, kind=algo)

    inv = np.empty(sorter.size, dtype=np.intp)
    inv[sorter] = np.arange(sorter.size, dtype=np.intp)

    if method == 'ordinal':
        return inv + 1, sorter

    arr = arr[sorter]
    obs = np.r_[True, arr[1:] != arr[:-1]]
    dense = obs.cumsum()[inv]

    if method == 'dense':
        return dense, sorter

    # cumulative counts of each unique value
    count = np.r_[np.nonzero(obs)[0], len(obs)]

    if method == 'max':
        return count[dense], sorter

    if method == 'min':
        return count[dense - 1] + 1, sorter

    # average method
    return .5 * (count[dense] + count[dense - 1] + 1), sorter
