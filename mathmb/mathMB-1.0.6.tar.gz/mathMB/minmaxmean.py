"""``minmaxmean()``: Print np.min(), np.max(), np.mean() at once."""
import numpy as np


def minmaxmean(x):
    """Print np.min(), np.max(), np.mean() at once."""
    return np.nanmin(x), np.nanmax(x), np.nanmean(x)
