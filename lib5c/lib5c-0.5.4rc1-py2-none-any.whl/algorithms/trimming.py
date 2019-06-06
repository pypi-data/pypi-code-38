"""
Module for trimming low or "dead" 5C fragments away from 5C datasets.
"""

import numpy as np

from lib5c.util.parallelization import parallelize_regions


@parallelize_regions
def trim_primers(primermap, counts_superdict, min_sum=100.0, min_frac=0.5):
    """
    Trim a primermap using counts information from many replicates.

    Parameters
    ----------
    primermap : List[Dict[str, Any]]
        The primermap to trim. See ``lib5c.parsers.primers.get_primermap()``.
    counts_superdict : Dict[str, np.ndarray]
        The keys are replicate names, the values are the counts for that rep.
    min_sum : Optional[float]
        Primers with a total cis sum lower than this value will be trimmed.
    min_frac : Optional[float]
        Primers with fewer than this fraction of nonzero interactions out of all
        their finite interactions will be trimmed.

    Returns
    -------
    Tuple[List[Dict[str, Any]], Set[int]]
        The first element is the trimmed primermap, the second is the set of
        indices of the original primermap which were removed.
    """
    # keep track of removed indices
    removed_indices = set()

    # each replicate gets its own chance to remove each primer
    for rep in counts_superdict.keys():
        # check min_sum
        if min_sum:
            for i in range(len(primermap)):
                column_sum = np.nansum(counts_superdict[rep][:, i])
                if column_sum < min_sum:
                    removed_indices.add(i)
        # check min_frac
        if min_frac:
            for i in range(len(primermap)):
                column = counts_superdict[rep][:, i]
                total_interactions = np.count_nonzero(~np.isnan(column))
                nonzero_interactions = np.count_nonzero(
                    column[np.isfinite(column)])
                fraction = nonzero_interactions / float(total_interactions)
                if fraction < min_frac:
                    removed_indices.add(i)

    # construct trimmed primermap
    trimmed_primermap = [primermap[i]
                         for i in range(len(primermap))
                         if i not in removed_indices]

    return trimmed_primermap, removed_indices


@parallelize_regions
def wipe_counts(counts, indices, wipe_value=np.nan):
    """
    Wipes specified rows and columns of the counts matrix with a specified
    value.

    Parameters
    ----------
    counts : np.ndarray
        The square symmetric counts matrix to wipe.
    indices : Iterable[int]
        The indices of the rows and columns to wipe.
    wipe_value : Optional[float]
        The value to wipe the selected indices with.

    Returns
    -------
    np.ndarray
        The wiped counts matrix.
    """
    for i in indices:
        counts[:, i] = wipe_value
        counts[i, :] = wipe_value
    return counts


@parallelize_regions
def trim_counts(counts, indices):
    """
    Removes specified rows and columns from the counts matrix.

    Parameters
    ----------
    counts : np.ndarray
        The square symmetric counts matrix to trim.
    indices : Iterable[int]
        The indices to wipe

    Returns
    -------
    np.ndarray
        The trimmed counts matrix.
    """
    indices = list(indices)
    counts = np.delete(counts, indices, axis=0)
    counts = np.delete(counts, indices, axis=1)
    return counts


def wipe_counts_superdict(counts_superdict, indices, wipe_value=np.nan):
    """
    Applies ``wipe_counts()`` to each replicate in a ``counts_superdict``.

    Parameters
    ----------
    counts_superdict : Dict[str, np.ndarray]
        The keys are replicate names, the values are the counts for that rep.
    indices : Iterable[int]
        The indices to wipe
    wipe_value : Optional[float]
        The value to wipe the selected indices with.

    Returns
    -------
    Dict[str, np.ndarray]
        The keys are replicate names, the values are the wiped counts for that
        rep.
    """
    return {rep: wipe_counts(counts_superdict[rep], indices, wipe_value)
            for rep in counts_superdict.keys()}


def trim_counts_superdict(counts_superdict, indices):
    """
    Applies ``trim_counts()`` to each replicate in a ``counts_superdict``.

    Parameters
    ----------
    counts_superdict : Dict[str, np.ndarray]
        The keys are replicate names, the values are the counts for that rep.
    indices : Iterable[int]
        The indices to trim.

    Returns
    -------
    Dict[str, np.ndarray]
        The keys are replicate names, the values are the trimmed counts for that
        rep.
    """
    return {rep: trim_counts(counts_superdict[rep], indices)
            for rep in counts_superdict.keys()}
