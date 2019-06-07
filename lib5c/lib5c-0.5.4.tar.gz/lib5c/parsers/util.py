"""
Module containing utility functions for file parsing.
"""

import numpy as np


def parse_field(val):
    """
    Utility function for parsing a value that could be an int, a float, or a
    string.

    Parameters
    ----------
    val : str
        The value to parse.

    Returns
    -------
    Union[int, float, str]
        The parsed value.
    """
    try:
        return int(val)
    except ValueError:
        pass
    try:
        return float(val)
    except ValueError:
        return val


def null_value(dtype):
    """
    Utility method to get the appropriate null value given a numpy dtype.

    Pandas has some logic for this, see
    http://pandas.pydata.org/pandas-docs/stable/missing_data.html

    Parameters
    ----------
    dtype : np.dtype
        The dtype to return a null value for.

    Returns
    -------
    Any
        The default null value for this dtype.
    """
    if dtype == float:
        return np.nan
    if dtype == int:
        return 0
    if str(dtype).startswith('|S'):
        return 'NA'
    raise ValueError('no default null value exists for this dtype')
