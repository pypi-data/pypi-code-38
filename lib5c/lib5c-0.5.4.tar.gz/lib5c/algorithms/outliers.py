"""
Module for identifying and removing high spatial outliers from 5C contact
matrices.
"""

from math import ceil

import numpy as np
from scipy.ndimage.filters import generic_filter

from lib5c.algorithms.expected import \
    make_poly_log_log_binned_expected_matrix, \
    make_poly_log_log_fragment_expected_matrix
from lib5c.algorithms.express import express_normalize_matrix
from lib5c.util.parallelization import parallelize_regions


@parallelize_regions
def flag_array_high_spatial_outliers(array, size=5, fold_threshold=8.0):
    """
    Identifies which elements of an array are high spatial outliers.

    Parameters
    ----------
    array : np.ndarray
        The array to look for outliers in.
    size : int
        The size of the window to look in around each element when deciding if
        it is an outlier. Should be an odd integer.
    fold_threshold : float
        Elements will be flagged as outliers if they are greater than this
        number or greater than this many times the local median (as estimated
        using the window size in ``size``).

    Returns
    -------
    np.ndarray
        A matrix of the same size and shape as the input matrix, with 1's at
        positions flagged as high spatial outliers and 0's everywhere else.
    """
    median_filtered_array = generic_filter(array, np.nanmedian, size=size)
    flagged_indices = np.zeros_like(array)

    for i in range(len(array)):
        for j in range(i + 1):
            if array[i, j] > max(fold_threshold,
                                 fold_threshold * median_filtered_array[i, j]):
                flagged_indices[i, j] = 1
                flagged_indices[j, i] = 1

    return flagged_indices


@parallelize_regions
def remove_high_spatial_outliers(counts, size=5, fold_threshold=8.0,
                                 overwrite_value='nan', primermap=None,
                                 level='fragment'):
    """
    Convenience function for removing high spatial outliers from counts
    matrices.

    Parameters
    ----------
    counts : np.ndarray
        The matrix to remove outliers from.
    size : int
        The size of the window to look in around each element when deciding if
        it is an outlier. Should be an odd integer.
    fold_threshold : float
        Elements will be flagged as outliers if they are greater than this
        number or greater than this many times the local median (as estimated
        using the window size in ``size``).
    overwrite_value : {'nan', 'zero', 'median'}
        The value to overwrite elements flagged as outliers with.
    primermap : List[Dict[str, Any]]
        The list of fragments for this region corresponding to ``counts``.
    level : {'fragment', 'bin'}
        Whether to interpret ``counts`` as bin- or fragment-level. The
        difference is that bin-level matrices are assumed to have equal distance
        between elements.

    Returns
    -------
    np.ndarray
        The input matrix with all spatial outliers overwritten.h
    """
    # precompute expected
    if level == 'fragment' and primermap is not None:
        expected = make_poly_log_log_fragment_expected_matrix(
            counts, primermap)
    else:
        expected = make_poly_log_log_binned_expected_matrix(counts)

    # express normalize
    normalized, _, _ = express_normalize_matrix(counts, expected)
    normalized[~np.isfinite(counts)] = np.nan

    # flag outliers
    flagged_indices = flag_array_high_spatial_outliers(
        normalized, size=size, fold_threshold=fold_threshold)

    # overwrite outliers
    if overwrite_value == 'nan':
        counts[flagged_indices == 1] = np.nan
    elif overwrite_value == 'zero':
        counts[flagged_indices == 1] = 0
    elif overwrite_value == 'median':
        median_array = generic_filter(normalized, np.nanmedian, size=size)
        counts[flagged_indices == 1] = median_array[flagged_indices == 1]

    return counts


def remove_primer_primer_pairs(counts_superdict, primermap, threshold=5.0,
                               num_reps=None, fraction_reps=None,
                               all_reps=False, inplace=True):
    """
    Removes primer-primer pairs from a set of replicates according to criteria
    specified by the kwargs.

    Legacy code inherited from
    https://bitbucket.org/creminslab/primer-primer-pair-remover

    Parameters
    ----------
    counts_superdict : Dict[str, Dict[str, np.ndarray]]
        The counts superdict data structure to remove primer-primer pairs from.
    primermap : Dict[str, List[Dict[str, Any]]]
        The primermap or pixelmap describing the loci whose interaction
        frequencies are quantified in the ``counts_superdict``.
    threshold : float
        Sets the threshold. A rep passes the threshold if it is greater than or
        equal to this number.
    num_reps : Optional[int]
        Pass an int to make the condition be that this many reps must clear the
        threshold.
    fraction_reps : Optional[float]
        Pass a fraction (between 0 and 1) as a float to make the condition be
        that this fraction of the reps must clear the threshold.
    all_reps : bool
        Pass True to make the condition be that the sum across all replicates
        must clear the threshold. This is the default mode if niether
        ``num_reps`` nor ``percentage_reps`` is passed.
    inplace : bool
        Pass True to operate in-place on the passed ``counts_superdict``; pass
        False to return a new counts superdict.

    Returns
    -------
    Dict[str, Dict[str, np.ndarray]]
        The result of the primer-primer pair removal, in the form of a counts
        superdict data structure analagous to the ``counts_superdict`` passed to
        this function.
    """
    # honor inplace
    if inplace:
        new_counts_superdict = counts_superdict
    else:
        new_counts_superdict = {
            rep: {
                region: counts_superdict[rep][region].copy()
                for region in counts_superdict[rep]}
            for rep in counts_superdict}

    # resolve num_reps vs fraction_reps
    if not num_reps and fraction_reps:
        num_reps = int(
            ceil(len(new_counts_superdict) * fraction_reps))

    # fall back to all_reps
    if not num_reps and not fraction_reps:
        all_reps = True

    # set nan's
    for region in primermap:
        if all_reps:
            replicate_sum = sum([new_counts_superdict[rep][region]
                                 for rep in new_counts_superdict])
            failed = replicate_sum < threshold
        else:
            rep_failed = {rep: new_counts_superdict[rep][region] < threshold
                          for rep in new_counts_superdict}
            num_failed = sum([rep_failed[rep]
                              for rep in new_counts_superdict])
            failed = num_failed >= num_reps
        for rep in new_counts_superdict:
            new_counts_superdict[rep][region][failed] = np.nan

    return new_counts_superdict
