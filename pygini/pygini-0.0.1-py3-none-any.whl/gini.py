'''Compute Gini index.

This implementation is inspired by the one found in [1]_.

References
----------
.. [1] https://github.com/oliviaguest/gini/blob/master/gini.py
'''

import numpy as np

def gini(arr, eps=1e-8):
    '''Calculate the Gini coefficient of a numpy array.

    Notes
    -----
    Based on bottom eq on [2]_.

    References
    ----------
    .. [2]_ http://www.statsdirect.com/help/
            default.htm#nonparametric_methods/gini.htm
    '''

    # All values are treated equally, arrays must be 1d and > 0:
    arr = np.abs(arr).flatten() + eps

    # Values must be sorted:
    arr = np.sort(arr)

    # Index per array element:
    index = np.arange(1, arr.shape[0]+1)

    # Number of array elements:
    N = arr.shape[0]

    # Gini coefficient:
    return(np.sum((2*index - N - 1)*arr))/(N*np.sum(arr))
