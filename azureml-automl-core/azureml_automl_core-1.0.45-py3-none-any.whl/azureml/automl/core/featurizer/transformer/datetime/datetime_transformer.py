# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Expands datetime features from input into sub features."""
from typing import Optional
import logging

import pandas as pd

from automl.client.core.common.logging_utilities import function_debug_log_wrapped
from ..automltransformer import AutoMLTransformer


class DateTimeFeaturesTransformer(AutoMLTransformer):
    """
    Expands datetime features from input into sub features.

    Like year, month, day, day of the week, day of the year, quarter, week of
    the month, hour, minute and second.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the logger.

        :param logger: Logger to be injected to usage in this class.
        """
        super().__init__()
        self._init_logger(logger)

    def _to_dict(self):
        """
        Create dict from transformer for  serialization usage.

        :return: a dictionary
        """
        dct = super(DateTimeFeaturesTransformer, self)._to_dict()
        dct['id'] = "datetime_transformer"
        dct['type'] = "datetime"

        return dct

    @function_debug_log_wrapped
    def fit(self, x, y=None):
        """
        Fit function for date time transform.

        :param x: Input array.
        :type x: numpy.ndarray or pandas.series
        :param y: Target values.
        :type y: numpy.ndarray
        :return: The instance object: self.
        """
        return self

    @function_debug_log_wrapped
    def transform(self, x):
        """
        Transform data x.

        :param x: The data to transform.
        :type x: numpy.ndarray or pandas.series
        :return: The transformed data.
        """
        return self._datetime_feats(x)

    def _datetime_feats(self, x):
        """
        Get the features for a datetime column.

        Expand the date time features from array of dates.

        :param x: Series that represents column.
        :type x: numpy.ndarray or pandas.series
        :return: Features for datetime column.
        """
        x = pd.to_datetime(pd.Series(x), infer_datetime_format=True,
                           box=False, errors="coerce").fillna(pd.Timestamp.min)
        return pd.concat([
            x.dt.year,                      # Year
            x.dt.month,                     # Month
            x.dt.day,                       # Day
            x.dt.dayofweek,                 # DayOfWeek
            x.dt.dayofyear,                 # DayOfYear
            x.dt.quarter,                   # QuarterOfYear
            (x.dt.day - 1) // 7 + 1,        # WeekOfMonth
            x.dt.hour,                      # Hour
            x.dt.minute,                    # Minute
            x.dt.second,                    # Second
        ], axis=1).values
