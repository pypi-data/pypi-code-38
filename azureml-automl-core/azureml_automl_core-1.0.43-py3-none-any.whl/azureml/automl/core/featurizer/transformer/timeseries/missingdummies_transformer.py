# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Add columns indicating corresponding numeric columns have NaN."""
import warnings
import pandas as pd

from automl.client.core.common.logging_utilities import function_debug_log_wrapped
from ..automltransformer import AutoMLTransformer

# Prevent warnings when using Jupyter
warnings.simplefilter("ignore")
pd.options.mode.chained_assignment = None


class MissingDummiesTransformer(AutoMLTransformer):
    """Add columns indicating corresponding numeric columns have NaN."""

    def __init__(self, numerical_columns, logger=None):
        """
        Construct for MissingDummiesTransformer.

        :param numerical_columns: The columns that will be marked.
        :type numerical_columns: list
        :return:
        """
        super().__init__()
        self._init_logger(logger)
        self.numerical_columns = numerical_columns

    def fit(self, x, y=None):
        """
        Fit function for MissingDummiesTransformer.

        :param x: Input data.
        :type x: TimeSeriesDataFrame
        :param y: Target values.
        :type y: numpy.ndarray
        :return: Class object itself.
        """
        return self

    @function_debug_log_wrapped
    def transform(self, x):
        """
        Transform function for MissingDummiesTransformer.

        :param x: Input data.
        :type x: TimeSeriesDataFrame
        :return: Result of MissingDummiesTransformer.
        """
        result = x.copy()
        for col in self.numerical_columns:
            is_null = result[col].isnull()
            result[col + '_WASNULL'] = is_null.apply(lambda x: int(x))
        return result
