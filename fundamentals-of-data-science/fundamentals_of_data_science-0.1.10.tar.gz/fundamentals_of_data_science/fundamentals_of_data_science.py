# -*- coding: utf-8 -*-

"""Main module."""

import os
import pandas as pd


def example2():
    """
    Returns the example dataset.

    Usage
    -----
        >>> import fundamentals_of_data_science as fun
        >>> df = fun.datasets.example()
        >>> df.head()
    """
    filename = os.path.abspath(os.path.join(os.path.dirname(__file__), 'imports-85.data.csv'))
    return(pd.read_csv(filename))