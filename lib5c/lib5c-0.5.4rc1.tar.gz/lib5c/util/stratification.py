"""
Module containing utility functions for stratifying data.
"""

import numpy as np


def conservative_qcut(array, num_quantiles, add_zero=True,
                      pad_right_endpoint=False):
    """
    Similar to pd.qcut(), but designed for stratifying quantities with
    zero-inflation. All zeros get put into the first stratum, and then the rest
    of the data is qcut.

    Parameters
    ----------
    array : np.ndarray
        The data to stratify.
    num_quantiles : int
        How many strata to generate.
    add_zero : bool
        Pass True to include the zeros in the final stratification in their own
        bin (increasing the number of bins returned by 1). Pass False to exclude
        zeros from the stratification.
    pad_right_endpoint : False
        If the right endpoint of your last bin is interpreted as open, pass True
        here to extend this right endpoint by a small number so that the highest
        value is not excluded from the stratification.

    Returns
    -------
    np.ndarray
        The binning scheme, as a list of n+1 bin endpoints. This is the format
        expected by pd.cut() or plt.hist().
    """
    if add_zero:
        array = array[array > 0]
    bins = np.unique([np.percentile(array, i*(100./num_quantiles))
                      for i in range(num_quantiles + 1)])
    if pad_right_endpoint:
        bins[-1] += 0.001
    if add_zero:
        bins[0] = 0.0
        bins = np.concatenate([[-0.001], bins])
    return bins
