"""
Module for identifying "unsmoothable columns" - sets of bins that don't contain
any non-zero fragments and are too wide to smooth over.
"""

import itertools

import numpy as np

from lib5c.algorithms.filtering.fragment_bin_filtering import (
    find_upstream_primers, find_nearby_fragments)
from lib5c.algorithms.trimming import wipe_counts
from lib5c.util.primers import guess_bin_step
from lib5c.util.parallelization import parallelize_regions


def unsmoothable_column_threshold_heuristic(window_width, bin_step):
    """
    This function defines the heuristic that determines how long a run of
    fragment-less bins must be before it is considered "unsmoothable".

    Parameters
    ----------
    window_width : int
        The width of the filtering window in base pairs.
    bin_step : int
        The "sampling rate" or "bin step".

    Returns
    -------
    int
        The maximum length of a run of fragment-less bins must be before it is
        considered "unsmoothable".
    """
    return ((window_width / 2) / bin_step) + 1


def find_unsmoothable_columns(regional_primermap, regional_pixelmap,
                              window_width, upstream_primer_mapping=None,
                              midpoint=False):
    """
    Identifies the unsmoothable columns in a region assuming that the smoothing
    was a filtering operation applied on fragment-level data.

    Parameters
    ----------
    regional_primermap : List[Dict[str, Any]]
        The primermap describing the primers for this region.
    regional_pixelmap : List[Dict[str, Any]]
        The pixelmap describing the bins for this region.
    window_width : int
        The width of the filtering window in base pairs.
    upstream_primer_mapping : Dict[int, int]
        A mapping from each bin index to the index of its nearest upstream
        primer. See ``lib5c.algorithms.filtering.fragment_bin_filtering
        .find_upstream_primers()``.
    midpoint : bool
        Pass True to restore legacy behavior when distances to fragments were
        based on their midpoints. The new behavior (with this kwarg set to
        False) is to compute distances to fragments based on their closest
        endpoint.

    Returns
    -------
    List[bool]
        A list of boolean values with length equal to the number of bins in the
        region. The ``i`` th element of this list is True if the ``i`` th bin in
        the region is an "unsmoothable column".
    """
    bin_step = guess_bin_step(regional_pixelmap)
    threshold = unsmoothable_column_threshold_heuristic(window_width, bin_step)

    if upstream_primer_mapping is None:
        upstream_primer_mapping = find_upstream_primers(regional_pixelmap,
                                                        regional_primermap)

    # a list of bool which is True if the ith "small bin" is empty
    blank_columns = [not bool(len(find_nearby_fragments(i,
                                                        regional_pixelmap,
                                                        regional_primermap,
                                                        upstream_primer_mapping,
                                                        bin_step / 2,
                                                        midpoint=midpoint)))
                     for i in range(len(regional_pixelmap))]

    # figure out which empty columns should be smoothed over
    unsmoothable_columns = []
    # group blank and nonblank columns
    for blank, run in itertools.groupby(blank_columns):
        # only write Trues if this is a group of more than threshold consecutive
        # blank columns
        run_as_list = list(run)
        if blank and len(run_as_list) > threshold:
            unsmoothable_columns.extend([True] * len(run_as_list))
        else:
            unsmoothable_columns.extend([False] * len(run_as_list))

    return unsmoothable_columns


@parallelize_regions
def wipe_unsmoothable_columns(binned_counts, primermap, pixelmap, window_width,
                              midpoint=False):
    """
    Convenience function for wiping the unsmoothable columns in a binned counts
    matrix assuming that the smoothing was a filtering operation applied on
    fragment-level data.

    Parameters
    ----------
    binned_counts : np.ndarray
        The matrix of binned counts to wipe unsmoothable columns from.
    primermap : List[Dict[str, Any]]
        The primermap describing the primers for this region.
    pixelmap : List[Dict[str, Any]]
        The pixelmap describing the bins for this region.
    window_width : int
        The width of the filtering window in base pairs.
    midpoint : bool
        Pass True to restore legacy behavior when distances to fragments were
        based on their midpoints. The new behavior (with this kwarg set to
        False) is to compute distances to fragments based on their closest
        endpoint.

    Returns
    -------
    np.ndarray
        The wiped matrix of binned counts.
    """
    unsmoothable_columns = find_unsmoothable_columns(primermap, pixelmap,
                                                     window_width,
                                                     midpoint=midpoint)
    return wipe_counts(binned_counts, np.where(unsmoothable_columns))


def find_prebinned_unsmoothable_columns(regional_counts, regional_pixelmap,
                                        window_width):
    """
    Identifies the unsmoothable columns in a region assuming that the smoothing
    was a filtering operation applied on data that was already bin-level.

    Parameters
    ----------
    regional_counts : np.ndarray
        The matrix of counts for this region.
    regional_pixelmap : List[Dict[str, Any]]
        The pixelmap describing the bins for this region.
    window_width : int
        The width of the filtering window in base pairs.

    Returns
    -------
    List[bool]
        A list of boolean values with length equal to the number of bins in the
        region. The ``i`` th element of this list is True if the ``i`` th bin in
        the region is an "unsmoothable column".
    """
    bin_step = guess_bin_step(regional_pixelmap)
    threshold = unsmoothable_column_threshold_heuristic(window_width, bin_step)

    # a list of bool which is True if the ith "small bin" is empty
    blank_columns = [not np.any(np.isfinite(regional_counts[:, i]))
                     for i in range(len(regional_counts))]

    # figure out which empty columns should be smoothed over
    unsmoothable_columns = []
    # group blank and nonblank columns
    for blank, run in itertools.groupby(blank_columns):
        # only write Trues if this is a group of more than threshold consecutive
        # blank columns
        run_as_list = list(run)
        if blank and len(run_as_list) > threshold:
            unsmoothable_columns.extend([True] * len(run_as_list))
        else:
            unsmoothable_columns.extend([False] * len(run_as_list))

    return unsmoothable_columns


@parallelize_regions
def wipe_prebinned_unsmoothable_columns(smoothed_counts, prebinned_counts,
                                        pixelmap, window_width):
    """
    Convenience function for wiping the unsmoothable columns in a binned counts
    matrix assuming that the smoothing was a filtering operation applied on
    bin-level data.

    Parameters
    ----------
    smoothed_counts : np.ndarray
        The matrix of smoothed counts to wipe unsmoothable columns from.
    prebinned_counts : np.ndarray
        The original binned counts matrix to use to identify zero-count columns.
    pixelmap : List[Dict[str, Any]]
        The pixelmap describing the bins for this region.
    window_width : int
        The width of the filtering window in base pairs.

    Returns
    -------
    np.ndarray
        The wiped matrix of binned counts.
    """
    unsmoothable_columns = find_prebinned_unsmoothable_columns(
        prebinned_counts, pixelmap, window_width)
    return wipe_counts(smoothed_counts, np.where(unsmoothable_columns))
