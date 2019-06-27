# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Augment input data with horizon rows and create a horizon feature."""
from typing import Any, Optional, List
from warnings import warn, filterwarnings
import logging

import pandas as pd
import numpy as np

from automl.client.core.common.exceptions import DataException
from automl.client.core.common.logging_utilities import function_debug_log_wrapped
from automl.client.core.common.time_series_data_frame import TimeSeriesDataFrame
from .forecasting_base_estimator import AzureMLForecastTransformerBase
from .forecasting_constants import ORIGIN_TIME_COLNAME_DEFAULT, HORIZON_COLNAME_DEFAULT
from .transform_utils import OriginTimeMixin


class MaxHorizonFeaturizer(AzureMLForecastTransformerBase, OriginTimeMixin):
    """
    A transformer that adds new rows to a TimeSeriesDataFrame up to a maximum forecast horizon
    and also adds an integer-typed horizon column.

    Example:
    >>> raw_data = {'store': ['wholefoods'] * 4,
    ...             'date' : pd.to_datetime(
    ...                   ['2017-01-01', '2017-02-01', '2017-03-01', '2017-04-01']),
    ...             'sales': range(4)}
    >>> tsdf = TimeSeriesDataFrame(
    ...    data=pd.DataFrame(raw_data),
    ...    grain_colnames=['store'], time_colname='date',
    ...    ts_value_colname='sales')
    >>> tsdf
                            sales
        date       store
        2017-01-01 wholefoods      0
        2017-02-01 wholefoods      1
        2017-03-01 wholefoods      2
        2017-04-01 wholefoods      3
    >>> MaxHorizonFeaturizer(2).fit_transform(tsdf)
                                          sales  horizon_origin
        date       store      origin
        2017-01-01 wholefoods 2016-12-01      0               1
                              2016-11-01      0               2
        2017-02-01 wholefoods 2017-01-01      1               1
                              2016-12-01      1               2
        2017-03-01 wholefoods 2017-02-01      2               1
                              2017-01-01      2               2
        2017-04-01 wholefoods 2017-03-01      3               1
                              2017-02-01      3               2
    """

    def __init__(self, max_horizon: int, origin_time_colname: str = ORIGIN_TIME_COLNAME_DEFAULT,
                 horizon_colname: str = HORIZON_COLNAME_DEFAULT, logger: Optional[logging.Logger] = None):
        """Create a horizon featurizer."""
        super().__init__()
        self.max_horizon = max_horizon
        self.origin_time_colname = origin_time_colname
        self.horizon_colname = horizon_colname

        self._init_logger(logger)

    def preview_column_names(self, tsdf: TimeSeriesDataFrame) -> List[str]:
        """
        Get the horizon features name that would be made if the transform were applied to X.

        :param tsdf: The TimeSeriesDataFrame to generate column names for.
        :type tsdf: TimeSeriesDataFrame
        :return: horizon feature name
        :rtype: list of str
        """
        return [self.horizon_colname]

    @function_debug_log_wrapped
    def fit(self, X: TimeSeriesDataFrame, y: Optional[Any] = None) -> 'MaxHorizonFeaturizer':
        """
        Fit the transform.

        :param X: Input data
        :type X: TimeSeriesDataFrame
        :param y: Ignored. Included for pipeline compatibility
        :return: Fitted transform
        :rtype: MaxHorizonFeaturizer
        """
        self._freq = X.infer_freq()

        return self

    @function_debug_log_wrapped
    def transform(self, X: TimeSeriesDataFrame) -> TimeSeriesDataFrame:
        """
        Create horizon rows and horizon feature.

        If the input already has origin times, an exception is raised.

        :param X: Input data
        :type X: TimeSeriesDataFrame
        :return: Data frame with horizon rows and columns
        :rtype: TimeSeriesDataFrame
        """
        if X.origin_time_colname is not None:
            raise DataException(
                'MaxHorizonFeaturizer cannot featurize data that contains origin times. ' +
                'Input data already has time-series features; ' +
                'please supply a dataset that has not been pre-processed.')

        X_new = self.create_origin_times(X, self.max_horizon, freq=self._freq,
                                         origin_time_colname=self.origin_time_colname,
                                         horizon_colname=self.horizon_colname)

        return X_new
