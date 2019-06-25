# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Encode categorical columns with integer codes."""
import warnings
import numpy as np
import pandas as pd

from automl.client.core.common.logging_utilities import function_debug_log_wrapped
from ..automltransformer import AutoMLTransformer

# Prevent warnings when using Jupyter
warnings.simplefilter("ignore")
pd.options.mode.chained_assignment = None


class NumericalizeTransformer(AutoMLTransformer):
    """Encode categorical columns with integer codes."""

    NA_CODE = pd.Categorical(np.nan).codes[0]

    def __init__(self, logger=None):
        """
        Construct for NumericalizeTransformer.

        :param categorical_columns: The columns that will be marked.
        :type categorical_columns: list
        :return:
        """
        super().__init__()
        self._init_logger(logger)

    def fit(self, x, y=None):
        """
        Fit function for NumericalizeTransformer.

        :param x: Input data.
        :type x: TimeSeriesDataFrame
        :param y: Target values.
        :type y: numpy.ndarray
        :return: Class object itself.
        """
        # Detect all categorical type columns
        fit_cols = (x.select_dtypes(['object', 'category', 'bool'])
                    .columns)

        # Save the category levels to ensure consistent encoding
        #   between fit and transform
        self._categories_by_col = {col: pd.Categorical(x[col]).categories
                                   for col in fit_cols}

        return self

    @function_debug_log_wrapped
    def transform(self, x):
        """
        Transform function for NumericalizeTransformer transforms categorical data to numeric.

        :param x: Input data.
        :type x: TimeSeriesDataFrame
        :return: Result of NumericalizeTransformer.
        """
        # Check if X categoricals have categories not present at fit
        # If so, warn that they will be coded as NAs
        for col, fit_cats in self._categories_by_col.items():
            now_cats = pd.Categorical(x[col]).categories
            new_cats = set(now_cats) - set(fit_cats)
            if len(new_cats) > 0:
                warnings.warn((type(self).__name__ + ': Column {0} contains '
                               'categories not present at fit: {1}. '
                               'These categories will be set to NA prior to encoding.')
                              .format(col, new_cats))

        # Get integer codes according to the categories found during fit
        assign_dict = {col:
                       pd.Categorical(x[col],
                                      categories=fit_cats)
                       .codes
                       for col, fit_cats in self._categories_by_col.items()}

        return x.assign(**assign_dict)
