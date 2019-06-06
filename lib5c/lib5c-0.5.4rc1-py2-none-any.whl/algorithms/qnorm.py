"""
Module for quantile normalization.

Original author of :func:`qnorm()`, :func:`_rank_data()`,
:func:`_average_rows()`, and :func:`_sub_in_normed_val()`: Dan Gillis

Note: data matrices in these functions are typically expected to be arranged
with each column representing one replicate, except for the functions
:func:`_rank_data()`, :func:`_average_rows()`, and :func:`_sub_in_normed_val()`,
which expect them to be arranged with each row representing one replicate.

The exposed functions are :func:`qnorm`, :func:`qnorm_parallel`,
:func:`qnorm_fast`, :func:`qnorm_fast_parallel`, and the convenience function
:func:`qnorm_counts_superdict`.
"""

import numpy as np

from lib5c.util.sorting import rankdata_plus
from lib5c.util.parallelization import parallelize_regions
from lib5c.util.counts_superdict import counts_superdict_to_matrix
from lib5c.util.counts import unflatten_counts_from_list,\
    flatten_regional_counts, unflatten_regional_counts


def _rank_data(data):
    """
    Sorts data, finds rank, and finds all ties in each column.
    Accepted inputs are dicts and lists of lists - data should be n x m
    structure.
    Returns ranked data, list of ranks, and start and end point of all ties.

    Parameters
    ----------
    data : 2d numpy array
        The data to rank.

    Returns
    -------
    tuple of (list of 1d array, 2d array, list of list of numeric)
        The first element of the tuple is a column-sorted representation of
        ``data``. The second element of the tuple contains the column ranks of
        the entries of ``data``. The third element of the tuple contains the
        indices that separate runs of ranks that have the same value.
    """
    sorted_data = []
    tied_rank_idx = []
    ranks = np.zeros((len(data), len(data[0])))

    col_num = -1
    # sort data and find ties in each column
    for column in data:
        col_num += 1
        sort_idx = np.argsort(column)
        # get indices to revert sorted back to unsorted order
        rev_sort_idx = np.zeros(len(column), dtype='int32')
        rev_sort_idx[sort_idx] = np.arange(len(column), dtype='int32')
        sorted_col = np.asarray(column)
        sorted_col = sorted_col[sort_idx]

        sorted_data.append(list(sorted_col))

        # find ties by seeing how many consecutive sorted entries have same
        # value
        # get start site and end site, where end site is first entry that does
        # not have the same value as previous entry (or entries)
        # note: even entries with unique values are considered ties for these
        # purposes (i.e. a tie between one object)
        ind_start = 0  # start of current value
        ind_value = sorted_col[0]  # current value
        tied_rank_idx.append([])
        final_idx = len(column)-1
        for i in range(1, final_idx):
            if sorted_col[i] != ind_value:
                # assign all tied entries the same value
                ranks[col_num][ind_start:i] = ind_start
                # add start site of current tie
                tied_rank_idx[col_num].append(ind_start)
                ind_value = sorted_col[i]
                ind_start = i
        # handle final case separately
        if sorted_col[final_idx] != ind_value:
            ranks[col_num][ind_start:final_idx] = ind_start
            ranks[col_num][final_idx] = final_idx
            tied_rank_idx[col_num].append(ind_start)
            tied_rank_idx[col_num].append(final_idx)  # final value start site
            tied_rank_idx[col_num].append(final_idx+1)  # final value end site
        else:
            ranks[col_num][ind_start:final_idx+1] = ind_start
            tied_rank_idx[col_num].append(ind_start)
            tied_rank_idx[col_num].append(final_idx+1)

        # gives order of ranks for original column
        ranks[col_num] = ranks[col_num][rev_sort_idx]

    return sorted_data, ranks, tied_rank_idx


def _average_rows(data, reference_index=None):
    """
    Find average value for each row of sorted data.

    Parameters
    ----------
    data : list of 1d numpy array
        The data to average.
    reference_index : Optional[int]
        Pass an index into the outer list of ``data`` to serve as the reference
        distribution instead of averaging.

    Returns
    -------
    1d array
        The average of each row of data.
    """
    data_mat = np.zeros((len(data[0]), len(data)))
    # put data into numpy 2-D array
    for col_num in range(0, len(data)):
        data_mat[:, col_num] = data[col_num]
    # find average of rows
    if reference_index is None:
        average_col = np.mean(data_mat, 1)
    else:
        average_col = data_mat[:, reference_index]
    return average_col


def _sub_in_normed_val(data, ranks, average_col, tied_rank_idx, tie):
    """
    Returns data matrix with normalized values. Handles ties according to the
    value passed in the ``tie`` kwarg.

    Parameters
    ----------
    data : list of list of numeric
        The column-sorted data to sub in values for.
    ranks : 2d array
        The original ranks of the values in ``data``.
    average_col : 1d array
        The average of each row of data.
    tied_rank_idx : list of list of numeric
        The indices that separate runs of ranks that have the same values.
    tie : {'lowest', 'average'}, optional
        Pass ``'lowest'`` to set all tied entries to the value of the lowest
        rank. Pass ``'average'`` to set all tied entries to the average value
        across the tied ranks.

    Returns
    -------
    list of 1d array
        The normalized data.
    """
    sorted_norm_data = np.zeros((len(data), len(data[0])))
    normed_data = []
    for col_num in range(0, len(data)):
        # find all values of shared rank
        for rank_num in range(len(tied_rank_idx[col_num])-1):
            start_idx = tied_rank_idx[col_num][rank_num]
            end_idx = tied_rank_idx[col_num][rank_num + 1]
            if tie == 'lowest':
                # give all of these entries the value of lowest rank
                sorted_norm_data[col_num][start_idx:end_idx] =\
                    average_col[start_idx]
            else:  # tie type is average
                # give all of these entries average value of their ranks
                average_val = np.mean(average_col[start_idx:end_idx])
                sorted_norm_data[col_num][start_idx:end_idx] = average_val
        # sort data back to original order
        rev_sort_ord = np.array(ranks[col_num], dtype='int32')
        normed_data.append(sorted_norm_data[col_num][rev_sort_ord])

    return normed_data


def qnorm(data, tie='lowest', reference_index=None):
    """
    Quantile normalizes a data set.

    Parallelizable if ``data`` is a 2d np.ndarray; see
    ``lib5c.algorithms.qnorm.qnorm_parallel()``.

    Parameters
    ----------
    data : 2d numeric structure, or dict of 1d numeric structure
        Anything that can be cast to array. Should be passed as row-major.
        Quantile normalization will performed on the columns of ``data``.
    tie : {'lowest', 'average'}, optional
        Pass ``'lowest'`` to set all tied entries to the value of the lowest
        rank. Pass ``'average'`` to set all tied entries to the average value
        across the tied ranks.
    reference_index : int or str, optional
        If ``data`` is a row-major array, pass a column index to serve as a
        reference distribution. If ``data`` is a dict, pass a key of that dict
        that should serve as the reference distribution. Pass None to use the
        average of all distributions as the target distribution.

    Returns
    -------
    2d numpy array, or dict of 1d numpy array
        The quantile normalized data. If ``data`` was passed as a dict, then a
        dict with the same keys is returned.

    Notes
    -----
    This function is nan-safe. As long as each column of the input data
    contains the same number of nan's, nan's will only get averaged with other
    nan's, and they will get substituted back into their original positions. See
    the Examples section for an example of this.

    Examples
    --------
    >>> import numpy as np
    >>> from lib5c.algorithms.qnorm import qnorm
    >>> qnorm(np.array([[5,    4,    3],
    ...                 [2,    1,    4],
    ...                 [3,    4,    6],
    ...                 [4,    2,    8]]))
    ...
    array([[5.66666667, 4.66666667, 2.        ],
           [2.        , 2.        , 3.        ],
           [3.        , 4.66666667, 4.66666667],
           [4.66666667, 3.        , 5.66666667]])
    >>> qnorm(np.array([[     5, np.nan,      3],
    ...                 [     2,      1,      4],
    ...                 [np.nan,      4,      6],
    ...                 [     4,      2, np.nan]]))
    ...
    array([[5.        ,        nan, 2.        ],
           [2.        , 2.        , 3.33333333],
           [       nan, 5.        , 5.        ],
           [3.33333333, 3.33333333,        nan]])
    >>> qnorm(np.array([[     5, np.nan,      3],
    ...                 [     2,      1,      4],
    ...                 [np.nan,      4,      6],
    ...                 [     4,      2, np.nan]]), reference_index=1)
    ...
    array([[ 4., nan,  1.],
           [ 1.,  1.,  2.],
           [nan,  4.,  4.],
           [ 2.,  2., nan]])
    >>> qnorm({'A': [5, 2, 3, 4],
    ...        'B': [4, 1, 4, 2],
    ...        'C': [3, 4, 6, 8]})
    ...
    {'A': array([5.66666667, 2.        , 3.        , 4.66666667]),
     'C': array([2.        , 3.        , 4.66666667, 5.66666667]),
     'B': array([4.66666667, 2.        , 4.66666667, 3.        ])}
    >>> qnorm({'A': [5, 2, 3, 4],
    ...        'B': [4, 1, 4, 2],
    ...        'C': [3, 4, 6, 8]}, reference_index='C')
    ...
    {'A': array([8., 3., 4., 6.]),
     'C': array([3., 4., 6., 8.]),
     'B': array([6., 3., 6., 4.])}
    >>> qnorm({'A': [5, 2, 3, 4],
    ...        'B': [4, 1, 4, 2],
    ...        'C': [3, 4, 6, 8]}, reference_index='C', tie='average')
    ...
    {'A': array([8., 3., 4., 6.]),
     'C': array([3., 4., 6., 8.]),
     'B': array([7., 3., 7., 4.])}
    """
    # handle input types
    if type(data) == dict:
        # convert dict to array, storing replicate names for later
        replicate_order = data.keys()
        data_array = np.array([data[rep] for rep in replicate_order])
        if reference_index is not None:
            reference_index = replicate_order.index(reference_index)
    else:
        # make sure we have a numpy array otherwise
        data_array = np.array(data, dtype=float).T

    # quantile normlize.
    sorted_data, ranks, tied_rank_idx = _rank_data(data_array)
    average_col = _average_rows(sorted_data, reference_index=reference_index)
    normed_data = _sub_in_normed_val(sorted_data, ranks, average_col,
                                     tied_rank_idx, tie)

    # handle output types
    if type(data) == dict:
        # if data was a dict then return a dict
        normed_data = np.array(normed_data, dtype=float).T
        normed_data = {replicate_order[i]: normed_data[:, i]
                       for i in range(len(replicate_order))}
    else:
        # coerce the output to a numpy array
        normed_data = np.array(normed_data, dtype=float).T

    return normed_data


qnorm_parallel = parallelize_regions(qnorm)


def qnorm_fast(data, reference_index=None):
    """
    Quantile normalizes a data set.

    Simpler, faster implementation compared to ``lib5c.algorithms.qnorm()``, but
    only supports ``tie='lowest'`` behavior and only takes an ``np.ndarray``
    as input. This approach was developed and timed in
    `this repsitory <https://bitbucket.org/creminslab/qnorm-sandbox/>`_.

    Parallelizable if ``data`` is a 2d np.ndarray; see
    ``lib5c.algorithms.qnorm.qnorm_fast_parallel()``.

    Parameters
    ----------
    data : np.ndarray
        Two dimensional, with the columns representing the replicates to be
        qnormed. Quantile normalization will performed on the columns of
        ``data``.
    reference_index : int or str, optional
        Pass a column index to serve as a reference distribution. Pass None to
        use the average of all distributions as the target distribution.

    Returns
    -------
    np.ndarray
        The quantile normalized data.

    Notes
    -----
    This function is nan-safe. As long as each column of the input data contains
    the same number of nan's, nan's will only get averaged with other nan's, and
    they will get substituted back into their original  positions. See the
    Examples section for an example of this.

    Examples
    --------
    >>> import numpy as np
    >>> from lib5c.algorithms.qnorm import qnorm_fast
    >>> qnorm_fast(np.array([[5,    4,    3],
    ...                      [2,    1,    4],
    ...                      [3,    4,    6],
    ...                      [4,    2,    8]]))
    ...
    array([[5.66666667, 4.66666667, 2.        ],
           [2.        , 2.        , 3.        ],
           [3.        , 4.66666667, 4.66666667],
           [4.66666667, 3.        , 5.66666667]])
    >>> qnorm_fast(np.array([[     5, np.nan,      3],
    ...                      [     2,      1,      4],
    ...                      [np.nan,      4,      6],
    ...                      [     4,      2, np.nan]]))
    ...
    array([[5.        ,        nan, 2.        ],
           [2.        , 2.        , 3.33333333],
           [       nan, 5.        , 5.        ],
           [3.33333333, 3.33333333,        nan]])
    >>> qnorm_fast(np.array([[     5, np.nan,      3],
    ...                      [     2,      1,      4],
    ...                      [np.nan,      4,      6],
    ...                      [     4,      2, np.nan]]), reference_index=1)
    ...
    array([[ 4., nan,  1.],
           [ 1.,  1.,  2.],
           [nan,  4.,  4.],
           [ 2.,  2., nan]])
    """
    ranks, sorters = zip(*[rankdata_plus(data[:, i], method='min')
                           for i in range(data.shape[1])])
    workspace = np.array([data[:, i][sorters[i]]
                          for i in range(data.shape[1])], dtype=float).T
    if reference_index is not None:
        averages = np.copy(workspace[:, reference_index])
    else:
        averages = np.mean(workspace, axis=1)
    for i in range(data.shape[1]):
        workspace[:, i] = averages[ranks[i] - 1]
    return workspace


qnorm_fast_parallel = parallelize_regions(qnorm_fast)


def qnorm_counts_superdict(counts_superdict, primermap, tie='lowest',
                           regional=False, condition_on=None, reference=None):
    """
    Convenience function for quantile normalizing a counts superdict data
    structure.

    Parameters
    ----------
    counts_superdict : Dict[Dict[np.ndarray]]
        The keys of the outer dict are replicate names, the keys of the inner
        dict are region names, the values are square symmetric arrays of counts
        for the specified replicate and region.
    primermap : Dict[str, List[Dict[str, Any]]]
        The primermap describing the loci whose interaction counts are described
        in the ``counts_superdict``.
    tie : {'lowest', 'average'}
        Pass ``'lowest'`` to set all tied entries to the value of the lowest
        rank. Pass ``'average'`` to set all tied entries to the average value
        across the tied ranks.
    regional : bool
        Pass True to quantile normalize regions separately. Pass False to
        quantile normalize all regions together.
    condition_on : Optional[str]
        Pass a string key into the inner dicts of ``primermap`` to condition on
        that quantity. Current limitations: only works with ``regional=True``
        and can only condition with exact equality (does not support
        conditioning on strata of a quantity). Pass None to not do conditional
        quantile normalization.
    reference : Optional[str]
        Pass a string key into the ``counts_superdict`` to indicate a replicate
        that should be used as a reference distribution to quantile normalize
        to.

    Returns
    -------
    Dict[Dict[np.ndarray]]
        The keys of the outer dict are replicate names, the keys of the inner
        dict are region names, the values are square symmetric arrays of the
        quantile normalized counts for the specified replicate and region.
    """
    # determine rep order and region order
    rep_order = counts_superdict.keys()
    region_order = counts_superdict[rep_order[0]].keys()
    ref_index = rep_order.index(reference) if reference is not None else None

    if regional:
        if condition_on is None:
            # construct matrices for each region
            matrices = {
                region: np.array(
                    [flatten_regional_counts(counts_superdict[rep][region])
                     for rep in rep_order]).T
                for region in region_order}

            # propagate nan's
            for region in region_order:
                matrices[region][(~np.isfinite(matrices[region])).any(axis=1)] \
                    = np.nan

            # qnorm matrices
            if tie == 'lowest':
                qnormed_matrices = qnorm_fast_parallel(
                    matrices, reference_index=ref_index)
            else:
                qnormed_matrices = qnorm_parallel(
                    matrices, tie=tie, reference_index=ref_index)

            # unpack qnormed data
            qnormed_counts_superdict = {
                rep_order[i]: {
                    region: unflatten_regional_counts(
                        qnormed_matrices[region][:, i])
                    for region in region_order}
                for i in range(len(rep_order))}
        else:
            # collect locus property information
            properties = {region: np.array(
                [primermap[region][i][condition_on]
                 for i in range(len(primermap[region]))])
                for region in primermap}
            unique_values = np.unique(np.concatenate(
                [properties[region] for region in region_order]))

            # enforce non-inplace operation
            qnormed_counts_superdict = {
                rep: {region: np.copy(counts_superdict[rep][region])
                      for region in region_order}
                for rep in rep_order}

            # overwrite with conditionally qnormed values
            for i in range(len(unique_values)):
                for j in range(i + 1):
                    for region in region_order:
                        sel = np.outer(
                            properties[region] == unique_values[i],
                            properties[region] == unique_values[j]
                        )
                        sel = sel | sel.T
                        if np.sum(sel):
                            matrix = np.array(
                                [qnormed_counts_superdict[rep][region][sel]
                                 for rep in rep_order]).T
                            matrix[(~np.isfinite(matrix)).any(axis=1)] = np.nan
                            if tie == 'lowest':
                                qnormed_matrix = qnorm_fast(
                                    matrix, reference_index=ref_index)
                            else:
                                qnormed_matrix = qnorm(
                                    matrix, tie=tie, reference_index=ref_index)
                            for k in range(len(rep_order)):
                                qnormed_counts_superdict[rep_order[k]][region][
                                    sel] = qnormed_matrix[:, k]
    else:
        # construct matrix
        matrix = counts_superdict_to_matrix(
            counts_superdict, rep_order=rep_order, region_order=region_order).T

        # propagate nan's
        matrix[(~np.isfinite(matrix)).any(axis=1)] = np.nan

        # qnorm matrix
        if tie == 'lowest':
            qnormed_matrix = qnorm_fast(matrix, reference_index=ref_index)
        else:
            qnormed_matrix = qnorm(matrix, tie=tie, reference_index=ref_index)

        # unpack qnormed data
        qnormed_counts_superdict = {
            rep_order[i]: unflatten_counts_from_list(qnormed_matrix[:, i],
                                                     region_order, primermap)
            for i in range(len(rep_order))}

    return qnormed_counts_superdict
