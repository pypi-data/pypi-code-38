"""
Module for computing correlations between 5C replicates.
"""

import numpy as np
from scipy.stats import spearmanr, pearsonr

from lib5c.util.counts_superdict import counts_superdict_to_matrix


def make_pairwise_correlation_matrix_from_counts_matrix(counts_matrix,
                                                        correlation='pearson'):
    """
    Computes a matrix of pairwise correlation coefficients among a set of 5C
    replicates.

    Parameters
    ----------
    counts_matrix : np.ndarray
        The rows are replicates, the columns are FFLJs.
    correlation : {'pearson', 'spearman'}
        Controls which correlation will be used.

    Returns
    -------
    np.ndarray
        The square, symmetric pairwise correlation matrix.
    """
    # resolve correlation
    corr_fn = None
    if correlation == 'pearson':
        corr_fn = pearsonr
    elif correlation == 'spearman':
        corr_fn = spearmanr

    # compute matrix of pairwise correlation coefficients
    correlation_matrix = np.zeros((len(counts_matrix), len(counts_matrix)))
    for i in range(len(correlation_matrix)):
        for j in range(i + 1):
            if i == j:
                correlation_matrix[i, j] = 1.0
            else:
                corr_value = corr_fn(counts_matrix[i], counts_matrix[j])[0]
                correlation_matrix[i, j] = corr_value
                correlation_matrix[j, i] = corr_value

    return correlation_matrix


def make_pairwise_correlation_matrix(counts_superdict, correlation='pearson',
                                     rep_order=None):
    """
    Computes a matrix of pairwise correlation coefficients among a set of 5C
    replicates.

    Parameters
    ----------
    counts_superdict : Dict[str, Dict[str, np.ndarray]]
        The keys to the outer dict are replicate names as strings. The values
        are standard "counts dicts" whose keys are region names as strings and
        whose values are square symmetric matrices of counts.
    correlation : {'pearson', 'spearman'}
        Controls which correlation will be used.
    rep_order : Optional[List[str]]
        Pass a list of strings to specify the order of the replicates in the
        rows and columns of the returned correlation matrix. If this kwarg is
        omitted the columns and rows of the returned correlation matrix will be
        arranged in the iteration order of the keys of ``counts_superdict``.

    Returns
    -------
    np.ndarray
        The square, symmetric pairwise correlation matrix.
    """
    # make a matrix of all the counts
    counts_matrix = counts_superdict_to_matrix(
        counts_superdict, rep_order=rep_order, discard_nan=True)

    return make_pairwise_correlation_matrix_from_counts_matrix(
        counts_matrix, correlation=correlation)
