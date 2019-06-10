# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility classes and functions used by the transforms sub-package."""
from warnings import warn
import numpy as np
import pandas as pd

from .forecasting_constants import ORIGIN_TIME_COLNAME_DEFAULT
from automl.client.core.common.forecasting_exception import (TransformException,
                                                             TransformTypeException,
                                                             TransformValueException)
from automl.client.core.common.forecasting_utils import get_period_offsets_from_dates
from automl.client.core.common.time_series_data_frame import TimeSeriesDataFrame


class OriginTimeMixin(object):
    """Mixin class for origin time utility methods."""

    def verify_max_horizon_input(self, max_horizon):
        """
        Verify the validity of max_horizon input.

        It must be either a positive integer or a dictionary where all values
        are positive integers.

        :param max_horizon: Maximum horizon input
        :type max_horizon: int, dict

        :return: None
        :rtype: NoneType
        """
        if isinstance(max_horizon, dict):
            improper_types = [type(h) for h in max_horizon.values()
                              if not (isinstance(h, int) or
                                      issubclass(type(h), np.integer))]
            if len(improper_types) > 0:
                raise TransformTypeException(
                    ('All max_horizon values must be of integer type. ' +
                     'The following unsupported types were present in ' +
                     'the input: {0}').format(improper_types))

            not_positive = [h for h in max_horizon.values()
                            if h <= 0]
            if len(not_positive) > 0:
                raise TransformValueException(
                    ('All max_horizon values must be greater than zero. ' +
                     'The following unsupported values were present in ' +
                     'the input: {0}').format(not_positive))

        elif isinstance(max_horizon, int) \
                or issubclass(type(max_horizon), np.integer):
            if max_horizon <= 0:
                raise TransformValueException(
                    ('All max_horizon values must be greater than zero. ' +
                     'The following unsupported value was present in ' +
                     'the input: {0}').format(max_horizon))
        else:
            raise TransformException(
                'max_horizon must be an int or a dict.')

    def max_horizon_from_key_safe(self, key, max_horizon,
                                  default_horizon=1):
        """
        Safely return a maximum horizon in the case when it *might* be a value in a dictionary.

        The use case for this utility is when a max_horizon parameter
        to an origin-time-aware transform is a dictionary that maps
        time-series identifying keys to integer horizons.

        :param key: Dictionary key specifying the horizon to retrieve

        :param max_horizon: Object containing maximum horizons
        :type max_horizon: int, dict

        :param default_horizon:
            Default maximum horizon to return when the key
            isn't in the dictionary or max_horizon has an incompatible type
        :type default_horizon: int

        :return: A maximum horizon
        :rtype: int
        """
        try:
            h_max = (max_horizon[key] if isinstance(max_horizon, dict)
                     else max_horizon)
        except KeyError:
            warn(('OriginTimeMixin: No maximum horizon set for grain ' +
                  '{0}. Defaulting to a horizon of {1}.')
                 .format(key, default_horizon),
                 UserWarning)
            h_max = default_horizon

        if not isinstance(h_max, int):
            try:
                h_max = int(h_max)
            except BaseException:
                warn(('OriginTimeMixin: Maximum horizon for grain {0} ' +
                      'is not an integer. Defaulting to a horizon of {1}.')
                     .format(key, default_horizon))
                h_max = default_horizon

        return h_max

    def create_origin_times(self, X, max_horizon,
                            freq=None,
                            origin_time_colname=ORIGIN_TIME_COLNAME_DEFAULT):
        """
        Create origin time rows in an input data frame.

        If an origin_time_colname is already set, then this method is just
        a pass through.

        :param X: Input data frame to create origin times in.
        :type X: :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`

        :param max_horizon:
            Integer horizons defining the origin times to create.
            Parameter can be a single integer - which indicates a maximum
            horizon to create for all grains - or a dictionary where the keys
            are grain levels and each value is an integer maximum horizon.
        :type max_horizon: int, dict

        :param freq:
            Time series frequency as an offset alias or pandas.DateOffset.
            If freq=None, the method attempts to infer it from the input
            data frame
        :type freq: str, pd.DateOffset

        :param origin_time_colname:
            Name of origin time column to create in case origin times
            are not already contained in the input data frame.
            The `origin_time_colname` property of the transform output
            will be set to this parameter value in that case.
            This parameter is ignored if the input data frame contains
            origin times.
        :type origin_time_colname: str

        :return: TimeSeriesDataFrame with origin times added
        :rtype: :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`

        :raises: :class:`ftk.exception.AzureMLForecastException`
        """
        # Pass-through if origin times are set
        if X.origin_time_colname is not None:
            warn('OriginTimeMixin: Origin times already set. ' +
                 'Returning original data frame.', UserWarning)

            return X

        # Check freq input. Make sure it's a DateOffset.
        # Try to infer it if its not set
        if freq is None:
            freq = X.infer_freq()

        if not isinstance(freq, pd.DateOffset):
            freq = pd.tseries.frequencies.to_offset(freq)

        # Check max_horizon input
        self.verify_max_horizon_input(max_horizon)

        # Internal function for adding origins for a single horizon.
        # Returns a plain pandas.DataFrame with an origin column
        def add_origins_for_horizon(Xgr, h):

            origin_time_col = Xgr.time_index - h * freq

            return pd.DataFrame({origin_time_colname: origin_time_col},
                                index=Xgr.index)
        # ------------------------------------------------

        # Internal function for adding origins for a single grain
        # Returns a plain pandas data frame with an origin column
        def add_origins_single_grain(gr, Xgr):

            h_max = self.max_horizon_from_key_safe(gr, max_horizon)

            # Concat frames from all horizons
            return pd.concat([add_origins_for_horizon(Xgr, h)
                              for h in range(1, h_max + 1)])
        # ------------------------------------------------

        if X.grain_colnames is not None:
            origins_df = X.groupby_grain().apply(
                lambda Xgr: add_origins_single_grain(Xgr.name, Xgr))
        else:
            if not isinstance(max_horizon, int):
                raise TransformException(
                    'max_horizon must be an integer when no grain is set.')

            origins_df = add_origins_single_grain('', X)

        # Join with original frame (as plain data frame)
        X_df = pd.DataFrame(X, copy=False)
        X_df_origins = X_df.merge(origins_df, how='left',
                                  left_index=True, right_index=True)

        # Create a time-series data frame with metadata
        #  set appropriately
        ctr_args = {k: getattr(X, k) for k in X._metadata}
        ctr_args['origin_time_colname'] = origin_time_colname

        return TimeSeriesDataFrame(X_df_origins, copy=False, **ctr_args)

    def detect_max_horizons_by_grain(self, X, freq=None):
        """
        Detect a dictionary of maximum horizons for each grain in with a time index and origin times.

        :param X: Input data
        :type X: :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`

        :return:
            A dictionary of maximum horizons. The keys are grain identifiers;
            the values are integer horizons.
            If the origin time is not set, this function returns
            None.
        :rtype: dict, int, NoneType
        """
        if X.origin_time_colname is None:
            return None

        # Check freq input.
        # Try to infer it if its not set
        if freq is None:
            freq = X.infer_freq()

        horizons = get_period_offsets_from_dates(X.origin_time_index,
                                                 X.time_index,
                                                 freq)
        if X.grain_colnames is None:
            return horizons.max()

        horizon_series = pd.Series(horizons, index=X.index)
        max_horizon_series = (horizon_series
                              .groupby(level=X.grain_colnames,
                                       group_keys=False)
                              .max())

        return max_horizon_series.to_dict()
