"""
Module for interfacing with the external ``iced`` Python package, which provides
access to the ICED matrix balancing algorithm.
"""

import numpy as np
try:
    from iced.normalization import ICE_normalization
except ImportError:
    ICE_normalization = None

from lib5c.util.parallelization import parallelize_regions
from lib5c.util.counts import impute_values


@parallelize_regions
def iced_balance_matrix(matrix, max_iter=3000, eps=1e-4, norm='l1',
                        imputation_size=0):
    """
    Convenience function wrapping the ``ICE_normalization`` function from the
    external ``iced`` Python package, which balances a counts matrix using the
    ICE algorithm.

    Parameters
    ----------
    matrix : np.ndarray
        The counts matrix to balance.
    max_iter : int
        The maxiumum number of iterations to try.
    eps : float
        The relative size of error before declaring convergence.
    norm : {'l1', 'l2'}
        What norm to use as a distance measure.
    imputation_size : int
        Pass an int greater than 0 to replace NaN's in the matrix with a local
        median approximation. Pass 0 to skip imputation.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        The first element of the tuple is the balanced matrix. The second
        element is the bias vector.
    """
    imputed_matrix = impute_values(matrix, size=imputation_size)
    balanced, bias = ICE_normalization(
        imputed_matrix, max_iter=max_iter, eps=eps, norm=norm, output_bias=True)
    balanced[~np.isfinite(matrix)] = np.nan
    return balanced, bias
