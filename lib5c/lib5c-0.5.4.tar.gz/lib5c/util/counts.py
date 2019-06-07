"""
Module containing utilities for manipulating 5C counts.
"""

import numpy as np
from scipy import stats
from scipy.ndimage.filters import generic_filter

from lib5c.util.parallelization import parallelize_regions
from lib5c.util.statistics import convert_to_two_tail
from lib5c.util.mathematics import symmetrize


def flatten_counts(counts, discard_nan=False):
    """
    Flattens each region in a counts dictionary into a flat, nonredundant list.

    Parameters
    ----------
    counts : dict of 2d numpy arrays
        The keys are the region names. The values are the arrays of counts
        values for that region. These arrays are square and symmetric.
    discard_nan : bool
        If True, nan's will not be present in the returned lists.

    Returns
    -------
    dict of lists of floats
        The keys are the region names. The values are flat, nonredundant lists
        of counts for that region. The ``(i, j)`` th element of the counts for a
        region (for ``i >= j`` ) ends up at the ``(i*(i+1)/2 + j)`` th index of
        the flattened list for that region. If discard_nan is True, then the nan
        elements will be missing and this specific indexing will not be
        preserved.

    Examples
    --------
    >>> import numpy as np
    >>> from lib5c.util.counts import flatten_counts
    >>> counts = {'a': np.array([[1, 2], [2, 3.]]),
    ...           'b': np.array([[np.nan, 4], [4, 5.]])}
    >>> flatten_counts(counts)
    {'a': array([1., 2., 3.]), 'b': array([nan,  4.,  5.])}
    >>> flatten_counts(counts, discard_nan=True)
    {'a': array([1., 2., 3.]), 'b': array([4., 5.])}
    """
    return {region: flatten_regional_counts(regional_counts,
                                            discard_nan=discard_nan)
            for region, regional_counts in counts.iteritems()}


def flatten_counts_to_list(counts, region_order=None, discard_nan=False):
    """
    Flattens counts for all regions into a single, flat, nonredudant list.

    Parameters
    ----------
    counts : dict of 2d numpy arrays
        The keys are the region names. The values are the arrays of counts
        values for that region. These arrays are square and symmetric.
    region_order : list of str
        List of string reference to region names in the order the regions should
        be concatenated when constructing the flat list. If None, the regions
        will be concatenated in arbitrary order.
    discard_nan : bool
        If True, nan's will not be present in the returned list.

    Returns
    -------
    1d numpy array
        The concatenated flattened regional counts. For information on the order
        in which flattened regional counts are created in, see
        ``lib5c.util.counts.flatten_regional_counts()``. If discard_nan is True,
        then the nan elements will be missing and this specific indexing will
        not be preserved.

    Examples
    --------
    >>> import numpy as np
    >>> from lib5c.util.counts import flatten_counts_to_list
    >>> counts = {'a': np.array([[1, 2], [2, 3.]]),
    ...           'b': np.array([[np.nan, 4], [4, 5.]])}
    >>> flatten_counts_to_list(counts, region_order=['a', 'b'])
    array([  1.,   2.,   3.,  nan,   4.,   5.])
    >>> flatten_counts_to_list(counts, region_order=['b', 'a'])
    array([nan,  4.,  5.,  1.,  2.,  3.])
    >>> flatten_counts_to_list(counts, region_order=['a', 'b'],
    ...                        discard_nan=True)
    array([1., 2., 3., 4., 5.])
    """
    if not region_order:
        region_order = counts.keys()
    return np.concatenate(
        [flatten_regional_counts(counts[region], discard_nan=discard_nan)
         for region in region_order])


def unflatten_counts_from_list(flattened_counts_array, region_order, pixelmap):
    """
    Unflattens a single list of flattened counts from many regions into a
    standard counts dict structure.

    Parameters
    ----------
    flattened_counts_array : 1d numpy array
        The list of flattened counts to be unflattened. See
        ``lib5c.util.counts.flatten_counts_to_list()``.
    region_order : list of str
        The list of region names in the order that the regions were concatenated
        in when making the ``flattened_counts_list`` See
        ``lib5c.util.counts.flatten_counts_to_list()``.
    pixelmap : dict of list of dict
        A pixelmap or primermap. This will be used to determine the size of each
        region. See ``lib5c.parsers.primers.get_pixelmap()`` or
        ``lib5c.parsers.primers.get_primermap()``.

    Returns
    -------
    dict of 2d numpy arrays
        The keys are the region names. The values are the arrays of counts
        values for that region. These arrays are square and symmetric.

    Examples
    --------
    >>> import numpy as np
    >>> from lib5c.util.counts import unflatten_counts_from_list
    >>> flat_counts = np.array([1, 2, 3., np.nan, 4, 5.])
    >>> pixelmap = {'a': [{}, {}], 'b': [{}, {}]}
    >>> unflatten_counts_from_list(flat_counts, ['a', 'b'], pixelmap)
    {'a': array([[1., 2.],
                 [2., 3.]]),
     'b': array([[nan,  4.],
                 [ 4.,  5.]])}
    """
    # the dict we will put the unflattened counts into
    counts = {}

    # keeps track of where we are in the flattened_counts_list
    # counts with indices lower than this number have already been unflattened
    # into counts
    index_pointer = 0

    for region in region_order:
        # get the size of this region
        region_size = len(pixelmap[region])

        # calculate the length of a flattened_regional_counts list for a region
        # of this size
        flattened_size = region_size*(region_size+1) / 2

        # assume that the next region_size entries in the flattened_counts_list
        # belong to this region
        counts[region] = unflatten_regional_counts(
            flattened_counts_array[index_pointer:index_pointer+flattened_size])

        # increment the index_pointer
        index_pointer += flattened_size

    return counts


def flatten_regional_counts(regional_counts, discard_nan=False):
    """
    Flattens the counts for a single region into a flat, nonredundant list.

    Parameters
    ---------
    regional_counts : 2d numpy array
        The square, symmetric array of counts for one region.
    discard_nan : bool
        If True, nan's will not be present in the returned list.

    Returns
    -------
    1d numpy array
        A flat, nonredundant lists of counts. The ``(i, j)`` th element of the
        ``regional_counts`` array (for ``i >= j`` ) ends up at the
        ``(i*(i+1)/2 + j)`` th index of the flattened array. If ``discard_nan``
        was True, these indices will not necessarily match up and it will not be
        possible to unflatten the array.

    Examples
    --------
    >>> import numpy as np
    >>> from lib5c.util.counts import flatten_regional_counts
    >>> a = np.array([[ 1, 4, -7], [4, 5, np.nan], [-7, np.nan, 9.]])
    >>> a
    array([[ 1.,  4., -7.],
           [ 4.,  5., nan],
           [-7., nan,  9.]])
    >>> flatten_regional_counts(a)
    array([  1.,   4.,   5.,  -7.,  nan,   9.])
    >>> flatten_regional_counts(a, discard_nan=True)
    array([ 1.,  4.,  5., -7.,  9.])
    """
    flattened_array = regional_counts[np.tril(np.ones_like(regional_counts,
                                                           dtype=bool))]
    if discard_nan:
        return flattened_array[np.isfinite(flattened_array)]
    return flattened_array


def unflatten_regional_counts(flat_regional_counts):
    """
    Turn a list of flattened counts back into a square symmetric array.

    Parameters
    ----------
    flat_regional_counts : 1d numpy array
        A flat, nonredundant array of counts. The ``(i*(i+1)/2 + j)`` th element
        of this list will end up at both the ``(i, j)`` th and the ``(j, i)`` th
        element of the returned array.

    Returns
    -------
    2d numpy array
        A square, symmetric array representation of the counts. The
        ``(i*(i+1)/2 + j)`` th element of ``flat_regional_counts`` will end up
        at both the ``(i, j)`` th and the ``(j, i)`` th element of this array.

    Examples
    --------
    >>> import numpy as np
    >>> from lib5c.util.counts import unflatten_regional_counts
    >>> b = np.array([ 1, 4, 5, -7, np.nan, 9.])
    >>> b
    array([  1.,   4.,   5.,  -7.,  nan,   9.])
    >>> unflatten_regional_counts(b)
    array([[ 1.,  4., -7.],
           [ 4.,  5., nan],
           [-7., nan,  9.]])
    """
    size = int((np.sqrt(1 + 8 * flat_regional_counts.shape[0]) - 1) / 2)
    unflattened_tril = np.zeros((size, size), dtype=flat_regional_counts.dtype)
    unflattened_tril[np.tril(np.ones_like(unflattened_tril, dtype=bool))] =\
        flat_regional_counts
    # symmetrize and return
    return symmetrize(unflattened_tril)


def unflatten_counts(flat_counts):
    """
    Apply ``unflatten_regional_counts()`` in parallel to a dict of flat regional
    counts to get back the original counts dict.

    Parameters
    ----------
    flat_counts : Dict[str, List[float]]
        The keys are region names as strings. The values are flat, nonredundant
        lists of counts for that region. The ``(i*(i+1)/2 + j)`` th element of
        each list will end up at both the ``(i, j)`` th and the ``(j, i)`` th
        element of the returned array for that region.

    Returns
    -------
    Dict[str, np.ndarray]
        The keys are region names as strings. The values are square, symmetric
        array representations of the counts for that region. The
        ``(i*(i+1)/2 + j)`` th element of flat_regional_counts will end up at
        both the ``(i, j)`` th and the ``(j, i)`` th element of this array.

    Examples
    --------
    >>> import numpy as np
    >>> from lib5c.util.counts import unflatten_counts
    >>> flattened_counts = {'a': np.array([1, 2, 3.]),
    ...                     'b': np.array([np.nan, 4, 5.])}
    >>> unflatten_counts(flattened_counts)
    {'a': array([[1., 2.],
                 [2., 3.]]),
     'b': array([[nan,  4.],
                 [ 4.,  5.]])}
    """
    return {region: unflatten_regional_counts(flat_regional_counts)
            for region, flat_regional_counts in flat_counts.iteritems()}


def calculate_regional_pvalues(regional_counts, distribution=stats.norm,
                               params=None, percentile_threshold=None):
    """
    Models the distribution of counts within a region as a normal distribution
    with mean mu and standard deviation sigma, then returns an array of p-values
    for each pairwise interaction assuming that normal distribution.

    Parameters
    ----------
    regional_counts : 2d numpy array
        The square, symmetric array of counts for one region.
    distribution : subclass of scipy.stats.rv_continuous
        The distribution to use to model the data.
    params : tuple of floats or None
        The parameters to plug into the distribution specified by the
        ``distribution`` kwarg when modeling the data. If None is passed, the
        parameters will be automatically calculated using
        ``rv_continuous.fit()``. The number and order of the floats should match
        the return value of ``rv_continuous.fit()`` for the particular
        distribution specified by the ``distribution`` kwarg.
    percentile_threshold : float between 0 and 100 or None
        If passed, the distribution and params kwargs are ignored and p-value
        modeling is skipped. Instead, the returned data struture will contain
        dummy p-values, which will be 0.0 whenever the peak passes the
        percentile threshold, and 1.0 otherwise.

    Returns
    -------
    (tuple of floats or None, 2d numpy array) tuple
        The tuple of floats contains the values of the parameters used to model
        the distribution. If ``percentile_threshold was passed``, this tuple
        will contain only one float, which will be the value used for
        thresholding. The 2d numpy array is the p-value for each count.
    """
    # empty array to store the p-values
    regional_pvalues = np.zeros_like(regional_counts)

    if not percentile_threshold:
        # calculate params if not passed
        if not params:
            params = distribution.fit(flatten_regional_counts(regional_counts,
                                                              discard_nan=True))

        # distribution to model the data
        frozen_distribution = distribution(*params[:-2],
                                           loc=params[-2],
                                           scale=params[-1])

        # calculate regional_pvalues
        for i in range(len(regional_counts)):
            for j in range(len(regional_counts)):
                regional_pvalues[i, j] = \
                    1 - frozen_distribution.cdf(regional_counts[i, j])
    else:
        # calculate dummy p-values
        threshold = np.percentile(
            flatten_regional_counts(regional_counts, discard_nan=True),
            percentile_threshold)
        for i in range(len(regional_counts)):
            for j in range(len(regional_counts)):
                if regional_counts[i, j] >= threshold:
                    regional_pvalues[i, j] = 0.0
                else:
                    regional_pvalues[i, j] = 1.0

        # package params
        params = (threshold,)

    return params, regional_pvalues


def calculate_pvalues(counts, distribution=stats.norm,
                      percentile_threshold=None):
    """
    Applies lib5c.util.counts.calculate_regional_pvalues() to each region in a
    counts dict independently and returns the results as a parallel counts dict
    containing the p-value information.

    Parameters
    ----------
    counts : dict of 2d numpy arrays
        The keys are the region names. The values are the arrays of counts
        values for that region. These arrays are square and symmetric.
    distribution : subclass of scipy.stats.rv_continuous
        The distribution to use to model the data.
    percentile_threshold : float between 0 and 100 or None
        If passed, the ``distribution`` kwarg is ignored and p-value modeling is
        skipped. Instead, the returned data struture will contain dummy
        p-values, which will be 0.0 whenever the peak passes the percentile
        threshold, and 1.0 otherwise. This percentile threshold is applied
        independently for each region.

    Returns
    -------
    (dict of 2d numpy arrays, dict of tuples of floats) tuple
        The first element of the tuple is a counts dict containing p-values for
        each region. The keys are the region names. The values are the arrays of
        p-values for that region. These arrays are square and symmetric. The
        second element of the tuple is a dict containing information about the
        values of the parameters used when modeling each region's counts. The
        keys of this dict are region names, and its values are tuples of floats
        describing these parameters for that region with the following
        structure. The number and order of the floats will match the return
        value of ``rv_continuous.fit()`` for the particular distribution
        specified by the ``distribution`` kwarg.

    Notes
    -----
    If you only need the p-values and don't care about the stats, you can also
    just do a dict comprehension as shown here::

        {
            region: calculate_regional_pvalues(counts[region])[2]
            for region in counts.keys()
        }

    """
    pvalues = {}
    stats_dict = {}
    for region in counts.keys():
        stats_dict[region], pvalues[region] = calculate_regional_pvalues(
            counts[region], distribution=distribution,
            percentile_threshold=percentile_threshold)
    return pvalues, stats_dict


@parallelize_regions
def extract_queried_counts(regional_counts, regional_primermap):
    """
    Starting from a square, symmetric counts matrix containing primer-level
    contact information, return a non-square, non-symmetric matrix where the
    5'-oriented fragments sit in the rows of the matrix while the 3'-oriented
    fragments sit in the columns. This restricts the input matrix to only the
    pairwise contacts that were actually queried by the 5C assay.

    Parameters
    ----------
    regional_counts : np.ndarray
        The classic square, symmetric counts matrix for this region.
    regional_primermap : List[Dict[str, Any]]
        The primermap describing the fragments in this region. It must contain a
        'orientation' metadata key so that
        ``regional_primermap[i]['orientation']`` is ``"5'"`` when the fragment
        was targeted by a 5'-oriented primer and ``"3'"`` otherwise.

    Returns
    -------
    np.ndarray, list of dict, list of dict
        The np.ndarray is the queried counts matrix, as described above. The two
        lists of dicts are lists of the primers corresponding to the rows and
        columns, respectively, of the queried counts matrix.
    """
    # fill in forward and reverse primer lists
    fiveprime_primer_indices = []
    fiveprime_primers = []
    threeprime_primer_indices = []
    threeprime_primers = []
    for i in range(len(regional_primermap)):
        if regional_primermap[i]['orientation'] == "5'":
            fiveprime_primer_indices.append(i)
            fiveprime_primers.append(regional_primermap[i])
        else:
            threeprime_primer_indices.append(i)
            threeprime_primers.append(regional_primermap[i])

    # initialize queried counts matrix for this region to all zeros
    queried_counts = np.zeros([len(fiveprime_primer_indices),
                               len(threeprime_primer_indices)],
                              dtype=regional_counts.dtype)

    # fill in queried counts matrix for this region
    for i in range(len(fiveprime_primer_indices)):
        for j in range(len(threeprime_primer_indices)):
            queried_counts[i, j] = regional_counts[fiveprime_primer_indices[i],
                                                   threeprime_primer_indices[j]]

    return queried_counts, fiveprime_primers, threeprime_primers


@parallelize_regions
def flip_pvalues(regional_counts):
    """
    To some approximation, convert counts matrices containing left-tail p-values
    to right-tail p-values or vice-versa.

    Parameters
    ----------
    regional_counts : np.ndarray
        The counts matrix containing p-values to flip.

    Returns
    -------
    np.ndarray
        The flipped p-values.
    """
    return 1.0 - regional_counts


@parallelize_regions
def queried_counts_to_pvalues(queried_counts):
    """
    Convert a queried counts matrix to a matrix of equivalent right-tail
    p-values using the emprical CDF.

    Parameters
    ----------
    queried_counts : np.ndarray
        The matrix of queried counts for this region. See
        ``lib5c.util.counts.extract_queried_counts()``.

    Returns
    -------
    np.ndarray
        The empirical p-value queried counts matrix for this region.
    """
    flattened_counts = queried_counts.flatten()
    flat_pvalues = 1.0 - (stats.rankdata(flattened_counts, 'min') - 1.0) / \
        np.isfinite(flattened_counts).sum()
    flat_pvalues[flat_pvalues <= 0] = np.nan
    return np.reshape(flat_pvalues, queried_counts.shape)


@parallelize_regions
def regional_counts_to_pvalues(regional_counts):
    """
    Convert a counts matrix to a matrix of equivalent right-tail p-values using
    the emprical CDF.

    Parameters
    ----------
    regional_counts : np.ndarray
        The counts matrix for this region.

    Returns
    -------
    np.ndarray
        The empirical p-value counts matrix for this region.
    """
    flattened_counts = flatten_regional_counts(regional_counts)
    flat_pvalues = 1.0 - (stats.rankdata(flattened_counts, 'min') - 1.0) / \
        np.isfinite(flattened_counts).sum()
    flat_pvalues[flat_pvalues <= 0] = np.nan
    return unflatten_regional_counts(flat_pvalues)


@parallelize_regions
def propagate_nans(regional_counts_a, regional_counts_b):
    """
    Propagate nan values between two matrices.

    Parameters
    ----------
    regional_counts_a, regional_counts_b : np.ndarray
        The matrices to propagate nan's between. These should have the same
        shape.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        The nan-propagated versions of the input matrices, in the order they
        were passed.
    """
    regional_counts_a[~np.isfinite(regional_counts_b)] = np.nan
    regional_counts_b[~np.isfinite(regional_counts_a)] = np.nan
    return regional_counts_a, regional_counts_b


@parallelize_regions
def impute_values(regional_counts, size=5):
    """
    Impute missing (nan) values in a counts matrix using a local median
    estimate.

    Parameters
    ----------
    regional_counts : np.ndarray
        The counts matrix to imupte.
    size : int
        The size of the window used to compute the local median. Should be an
        odd integer.

    Returns
    -------
    np.ndarray
        The counts matrix with missing values filled in with the local median
        estimates.
    """
    imputed_matrix = np.copy(regional_counts)
    if size > 0:
        median_filtered_matrix = generic_filter(
            regional_counts, np.nanmedian, size=size)
        imputed_matrix[~np.isfinite(regional_counts)] = \
            median_filtered_matrix[~np.isfinite(regional_counts)]
    else:
        imputed_matrix[~np.isfinite(regional_counts)] = 0.0
    return imputed_matrix


def divide_regional_counts(*list_of_regional_counts):
    """
    Perform element-wise serial division on a list of regional counts matrices.

    Parallelizable; see ``lib5c.util.counts.parallel_divide_counts()``.

    Propagates nan's. Emits nan's when dividing by zero.

    Parameters
    ----------
    list_of_regional_counts : List[np.ndarray]
        The list of regional counts matrices to divide.

    Returns
    -------
    np.ndarray
        The quotient.
    """
    return reduce(np.divide, list_of_regional_counts)


parallel_divide_counts = parallelize_regions(divide_regional_counts)


def subtract_regional_counts(*list_of_regional_counts):
    """
    Perform element-wise serial subtraction on a list of regional counts
    matrices.

    Parallelizable; see ``lib5c.util.counts.parallel_subtract_counts()``.

    Propagates nan's.

    Parameters
    ----------
    list_of_regional_counts : List[np.ndarray]
        The list of regional counts matrices to divide.

    Returns
    -------
    np.ndarray
        The quotient.
    """
    return reduce(np.subtract, list_of_regional_counts)


parallel_subtract_counts = parallelize_regions(subtract_regional_counts)


def log_regional_counts(regional_counts, pseudocount=1.0, base='e'):
    """
    Logs a regional counts matrix.

    Parallelizable; see ``lib5c.util.counts.parallel_log_counts()``.

    Emits nan when logging a negative number, and -inf when logging zero.

    Parameters
    ----------
    regional_counts : np.ndarray
        The counts matrix to log.
    pseudocount : float
        Psuedocount to add before logging.
    base : str or float
        The base to use when logging. Acceptable string values are 'e', '2', or
        '10'.

    Returns
    -------
    np.ndarray
        The logged counts matrix.

    Examples
    --------
    >>> import numpy as np
    >>> from lib5c.util.counts import log_regional_counts
    >>> a = np.exp(np.array([[1, 2], [2, 4.]]))
    >>> log_regional_counts(a, pseudocount=0)
    array([[1., 2.],
           [2., 4.]])
    >>> a -= 1 #  the default pseudocount will add this back before logging
    >>> a[0, 0] = -2  # what happens to negative values?
    >>> log_regional_counts(a)
    array([[nan,  2.],
           [ 2.,  4.]])
    >>> b = np.power(42, np.array([[1, 2], [2, 4.]]))
    >>> log_regional_counts(b, base=42, pseudocount=0)
    array([[1., 2.],
           [2., 4.]])
    """
    log_fns = {'e': np.log, '2': np.log2, '10': np.log10}
    if str(base) not in log_fns.keys():
        def log_fn(x):
            return np.log(x) / np.log(float(base))
    else:
        log_fn = log_fns[str(base)]
    return log_fn(regional_counts + pseudocount)


parallel_log_counts = parallelize_regions(log_regional_counts)


def unlog_regional_counts(regional_counts, pseudocount=1.0, base='e'):
    """
    Unlogs a regional counts matrix.

    Parallelizable; see ``lib5c.util.counts.parallel_unlog_counts()``.

    Emits nan's when the input counts are nan.

    Parameters
    ----------
    regional_counts : np.ndarray
        The counts matrix to unlog.
    pseudocount : float
        Psuedocount to subtract after unlogging.
    base : str or float
        The base to use when unlogging. Acceptable string values are 'e', '2',
        or '10'.

    Returns
    -------
    np.ndarray
        The unlogged counts matrix.

    Examples
    --------
    >>> import numpy as np
    >>> from lib5c.util.counts import log_regional_counts, unlog_regional_counts
    >>> a = np.array([[1, 2], [2, 4.]])
    >>> log_regional_counts(unlog_regional_counts(a))
    array([[1., 2.],
           [2., 4.]])
    >>> log_regional_counts(unlog_regional_counts(a, base=42), base=42)
    array([[1., 2.],
           [2., 4.]])
    """
    unlog_fns = {'e': np.exp, '2': np.exp2, '10': lambda x: np.power(x, 10)}
    if str(base) not in unlog_fns.keys():
        def unlog_fn(x):
            return np.power(float(base), x)
    else:
        unlog_fn = unlog_fns[str(base)]
    return unlog_fn(regional_counts) - pseudocount


parallel_unlog_counts = parallelize_regions(unlog_regional_counts)


def abs_diff_counts(a, b):
    """
    Computes the absolute value of the difference between two counts matrices in
    parallel across regions.

    Parameters
    ----------
    a, b : Dict[str, np.ndarray]
        The two counts dicts to take the absolute difference between.

    Returns
    -------
    Dict[str, np.ndarray]
        The absolute value of the difference between two counts dicts.
    """
    return {region: np.abs(a[region] - b[region]) for region in a.keys()}


def norm_counts(counts, order=1):
    """
    Attempt at defining a "norm" for counts dicts by simply summing a matrix
    p-norm over the regions.

    Parameters
    ----------
    counts : Dict[str, np.ndarray]
        The counts dict to compute a norm for.
    order : int
        The order of the matrix norm, as described by ``numpy.linalg.norm``.

    Returns
    -------
    float
        The norm of the counts dict.
    """
    return np.sum([np.linalg.norm(counts[region][np.isfinite(counts[region])],
                                  ord=order)
                   for region in counts.keys()])


@parallelize_regions
def convert_pvalues_to_interaction_scores(pvalues):
    """
    Calculates interaction scores from p-values.

    Parameters
    ----------
    pvalues : np.ndarray
        An array of p-values for a single region

    Returns
    -------
    np.ndarray
        An array of interaction scores for a single region
    """
    return -10 * np.log2(pvalues)


@parallelize_regions
def fold_pvalues(regional_counts):
    """
    Folds one-tail p-values into two-tail p-values using
    ``convert_to_two_tail()``. Only valid for p-values called using continuous
    distributions.

    Parameters
    ----------
    regional_counts : np.ndarray
        An array of one-tail p-values for a single region.

    Returns
    -------
    np.ndarray
        An array of the corresponding two-tail p-values.
    """
    return convert_to_two_tail(regional_counts)


def flatten_obs_and_exp(obs, exp, discard_nan=True, log=False):
    """
    Convenience function for flattening observed and expected counts together.

    Parameters
    ----------
    obs, exp : np.ndarray or dict of np.ndarray
        Regional matrices of observed and expected values, respectively. Pass
        counts dicts to redirect the call to ``flatten_obs_and_exp_counts()``.
    discard_nan : bool
        Pass True to discard nan's from the returned vectors.
    log : bool
        Pass True to log the returned vectors.

    Returns
    -------
    np.ndarray, np.ndarray
        The flattened vectors of obsereved and expected values, respectively.
    """
    if isinstance(obs, dict):
        return flatten_obs_and_exp_counts(obs, exp, discard_nan=discard_nan,
                                          log=log)
    obs = flatten_regional_counts(obs)
    exp = flatten_regional_counts(exp)
    if log:
        obs = np.log(obs + 1)
        exp = np.log(exp + 1)
    if discard_nan:
        idx = np.isfinite(obs) & np.isfinite(exp)
        return obs[idx], exp[idx]
    return obs, exp


def flatten_obs_and_exp_counts(obs_counts, exp_counts, discard_nan=True,
                               log=False):
    """
    Convenience function for flattening observed and expected counts together.

    Parameters
    ----------
    obs_counts, exp_counts : dict of np.ndarray
        Counts dicts of observed and expected values, respectively.
    discard_nan : bool
        Pass True to discard nan's from the returned vectors.
    log : bool
        Pass True to log the returned vectors.

    Returns
    -------
    np.ndarray, np.ndarray
        The flattened vectors of obsereved and expected values,
        respectively.
    """
    region_order = obs_counts.keys()
    obs = flatten_counts_to_list(obs_counts, region_order=region_order)
    exp = flatten_counts_to_list(exp_counts, region_order=region_order)
    if log:
        obs = np.log(obs + 1)
        exp = np.log(exp + 1)
    if discard_nan:
        idx = np.isfinite(obs) & np.isfinite(exp)
        return obs[idx], exp[idx]
    return obs, exp


def flatten_and_filter_counts(counts, min_filters=None, max_filters=None):
    """
    Flattens and filters multiple counts dicts (typically containing different
    types or stages of data) in parallel, applying customizable filters.

    Parameters
    ----------
    counts : dict of dict of np.ndarray or dict of np.ndarray
        Outer keys are always names of the types of count dicts. Inner keys are
        optional and represent region names. If this level of the dict is
        omitted this function will flatten all the regional counts matrices.
        Values are always square symmetric counts matrices.
    min_filters, max_filters : dict of numeric
        Map outer keys of ``counts`` to minimum or maximum values for that type
        of counts.

    Returns
    -------
    dict of np.ndarray, np.ndarray, list of str
        The dict's values are the parallel flattened and filtered count vectors.
        It has an extra 'dist' key for interaction distance in bin units. The
        array is a boolean index into the original flattened counts shape
        representing which positions have been filtered. The list is the order
        the regions were flattened in, or None if ``counts`` had only one level
        of keys.

    Notes
    -----
    To separately flatten each region, you can do:

        flat, idx, _ = parallelize_regions(flatten_and_filter_counts)(
            {r: {t: counts[t][r] for t in types} for r in regions})

    where ``flat`` will be a dict of dict of flattened vectors (outer keys are
    regions, inner keys are types) and ``idx`` will be a dict of boolean indices
    (keys are regions).
    """
    # check first key
    k = counts.keys()[0]

    if hasattr(counts[k], 'keys'):
        region_order = counts[k].keys()
        dist_counts = {
            region: np.array([[np.abs(i - j)
                               for i in range(len(counts[k][region]))]
                              for j in range(len(counts[k][region]))])
            for region in region_order}

        def flat_fn(x):
            return flatten_counts_to_list(x, region_order=region_order)
    else:
        region_order = None
        dist_counts = np.array([[np.abs(i - j)
                                 for i in range(len(counts[k]))]
                                for j in range(len(counts[k]))])
        flat_fn = flatten_regional_counts

    # flatten
    flattened_counts = {k: flat_fn(counts[k]) for k in counts}
    flattened_counts['dist'] = flat_fn(dist_counts)

    # decide what to filter
    idx = np.all(np.isfinite(np.stack(flattened_counts.values())), axis=0)
    if min_filters is not None:
        for k, v in min_filters.items():
            idx = idx & (flattened_counts[k] >= v)
    if max_filters is not None:
        for k, v in max_filters.items():
            idx = idx & (flattened_counts[k] <= v)

    # apply the filter
    for k in flattened_counts:
        flattened_counts[k] = flattened_counts[k][idx]

    return flattened_counts, idx, region_order


def apply_nonredundant(func, counts, primermap=None):
    """
    Applies a function to some counts over the non-redundant elements of the
    matrix or matrices.

    Parameters
    ----------
    func : callable
        The function to apply.
    counts : np.ndarray or dict of np.ndarray
        The counts to apply the function to.
    primermap : primermap, optional
        If counts is a dict, pass a primermap to reconstruct the resulting
        counts dict.

    Returns
    -------
    np.ndarray or dict of np.ndarray
        The result of the operation.
    """
    if type(counts) == np.ndarray:
        flat = flatten_regional_counts(counts)
        result = func(flat)
        return unflatten_regional_counts(result)
    else:
        if primermap is None:
            raise ValueError('primermap must be passed when applying over a'
                             'counts dict')
        region_order = counts.keys()
        flat = flatten_counts_to_list(counts, region_order)
        result = func(flat)
        return unflatten_counts_from_list(result, region_order, primermap)


apply_nonredundant_parallel = parallelize_regions(apply_nonredundant)


@parallelize_regions
def distance_filter(matrix, k=5):
    """
    Wipes the first `k` off-diagonals of `matrix` with `np.nan`.

    Parameters
    ----------
    matrix : np.ndarray
        The matrix to distance filter.
    k : int
        The number of off-diagonals to wipe.

    Returns
    -------
    np.ndarray
        The wiped matrix.
    """
    result = np.copy(matrix)
    result[np.triu(np.tril(np.ones_like(matrix), k=k), k=-k).astype(bool)] = \
        np.nan
    return result
