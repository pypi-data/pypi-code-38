"""
Module containing utility functions related to statistical transformation,
correction, or combination of p-values.
"""

import numpy as np
import scipy.stats as stats
from statsmodels.stats.multitest import multipletests


def adjust_pvalues(pvalue_matrix, method='fdr_bh'):
    """
    Performs multiple testing correction on a matrix of p-values.

    Parameters
    ----------
    pvalue_matrix : np.ndarray
        The matrix of p-values, representing many tests that were performed.
    method : str
        Method used for testing and adjustment of pvalues. Can be either the
        full name or initial letters. Available methods are ::

        `bonferroni` : one-step correction
        `sidak` : one-step correction
        `holm-sidak` : step down method using Sidak adjustments
        `holm` : step-down method using Bonferroni adjustments
        `simes-hochberg` : step-up method  (independent)
        `hommel` : closed method based on Simes tests (non-negative)
        `fdr_bh` : Benjamini/Hochberg  (non-negative)
        `fdr_by` : Benjamini/Yekutieli (negative)
        `fdr_tsbh` : two stage fdr correction (non-negative)
        `fdr_tsbky` : two stage fdr correction (non-negative)

    Returns
    -------
    np.ndarray
        The matrix of adjusted p-values. Same size and shape as pvalue_matrix.
    """
    pvalue_matrix = np.asarray(pvalue_matrix)
    padj_matrix = np.zeros_like(pvalue_matrix) * np.nan
    padj_matrix[np.isfinite(pvalue_matrix)] = \
        multipletests(pvalue_matrix[np.isfinite(pvalue_matrix)], 0.1,
                      method=method)[1]
    return padj_matrix


def stouffer(pvalue_matrix, axis=None):
    """
    Combines a matrix of p-values along a specified axis using Stouffer's
    Z-transform.

    Parameters
    ----------
    pvalue_matrix : np.ndarray
        Matrix of p-values.
    axis : int, optional
        The axis to combine p-values along. Pass None to combine all of them.

    Returns
    -------
    np.ndarray
        Array of combined p-values.

    Notes
    -----
    Element-by-element, this should be equivalent to::

        scipy.stats.combine_pvalues(pvalue_matrix, method='stouffer')[1]

    except that this function is vectorized.

    Examples
    --------
    >>> from scipy.stats import combine_pvalues
    >>> stouffer([0.1, 0.1]) == combine_pvalues([0.1, 0.1],
    ...                                         method='stouffer')[1]
    True
    >>> stouffer(np.array([[0.1, 0.1],
    ...                    [0.2, 0.2]]), axis=1)
    array([0.03496316, 0.11697758])
    """
    pvalue_matrix = np.asarray(pvalue_matrix)
    zscores = stats.norm.isf(pvalue_matrix)
    k = pvalue_matrix.size if axis is None else pvalue_matrix.shape[axis]
    scaled_zscore_sum = np.sum(zscores, axis=axis) / np.sqrt(k)
    return stats.norm.sf(scaled_zscore_sum)


def convert_to_two_tail(pvalue):
    """
    Converts a one-tail p-value to a two-tail p-value.

    Only valid for continuous distributions (otherwise I think the PMF
    evaluation at the obs value needs to be taken into account when reversing
    the test).

    Array-safe, nan-safe, position-independent.

    Parameters
    ----------
    pvalue : float
        The one-tail p-values to be folded into two-tail pvalues.

    Returns
    -------
    float
        The two-tail p-values.
    """
    idx = pvalue > 0.5
    pvalue[idx] = 1 - pvalue[idx]
    return 2 * pvalue
