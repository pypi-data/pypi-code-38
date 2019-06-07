import pandas as pd
import numpy as np


def fractionize(series):
    """Divide each element by the sum of the series

    Args:
        series (pd.Series): The self.

    Returns:
        pd.Series: The modified Series, No Side-effect.
    """
    sum = series.sum()
    return series / sum


def normalize(series):
    """Divide each element by the max of the series.

    Args:
        series (pd.Series): The self.

    Returns:
        pd.Series: The modified Series, No Side-effect.
    """
    max = series.max()
    return series / max


def unitarize(series):
    """Linearly scale the series so min -> 0 and max -> 1.

    Args:
        series (pd.Series): The self.

    Returns:
        pd.Series: The modified Series, No Side-effect.
    """
    min = series.min()
    max = series.max()
    return (series - min) / (max - min)


def zscore(series):
    """Zscoring the series.

    Args:
        series (pd.Series): The self.

    Returns:
        pd.Series: The modified Series, No Side-effect.
    """
    mean = series.mean()
    sd = np.std(series)
    return (series - mean) / sd
