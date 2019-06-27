# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Derive and select features from the time index, for instance 'day of week'."""
from typing import cast, List
from warnings import warn

import numpy as np
import pandas as pd
import datetime as dt

from automl.client.core.common.constants import TimeSeriesInternal
from automl.client.core.common.forecasting_exception import NotTimeSeriesDataFrameException
from automl.client.core.common.forecasting_ts_utils import construct_day_of_quarter, datetime_is_date
from automl.client.core.common.forecasting_utils import subtract_list_from_list
from automl.client.core.common.forecasting_verify import Messages, type_is_numeric
from automl.client.core.common.logging_utilities import function_debug_log_wrapped
from automl.client.core.common.time_series_data_frame import TimeSeriesDataFrame
from .forecasting_base_estimator import AzureMLForecastTransformerBase


class TimeIndexFeaturizer(AzureMLForecastTransformerBase):
    """
    A transformation class for computing (mostly categorical) features.

    .. py:class:: TimeIndexFeaturizer

    .. _Wikipedia.ISO: https://en.wikipedia.org/wiki/ISO_week_date

    This is intended to be used as a featurization step inside the
    forecast pipeline.

    This transform returns a new TimeSeriesDataFrame with all the
    original columns, plus extra 18 columns with datetime-based features.
    The following features are created:
    * year - calendar year
    * year_iso - ISO year, see details later
    * half - half-year, 1 if date is prior to July 1, 2 otherwise
    * quarter - calendar quarter, 1 through 4
    * month - calendar month, 1 through 12
    * month_lbl - calendar month as string, 'January' through 'December'
    * day - calendar day of month, 1 through 31
    * hour - hour of day, 0 through 23
    * minute - minute of day, 0 through 59
    * second - second of day, 0 through 59
    * am_pm - 0 if hour is before noon (12 pm), 1 otherwise
    * am_pm_lbl - 'am' if hour is before noon (12 pm), 'pm' otherwise
    * hour12 - hour of day on a 12 basis, without the AM/PM piece
    * wday - day of week, 0 (Monday) through 6 (Sunday)
    * wday_lbl - day of week as string
    * qday - day of quarter, 1 through 92
    * yday - day of year, 1 through 366
    * week - ISO week, see below for details

    ISO year and week are defined in ISO 8601, see Wikipedia.ISO for details.
    In short, ISO weeks always start on Monday and last 7 days.
    ISO years start on the first week of year that has a Thursday.
    This means if January 1 falls on a Friday, ISO year will begin only on
    January 4. As such, ISO years may differ from calendar years.

    :param overwrite_columns:
        Flag that permits the transform to overwrite existing columns in the
        input TimeSeriesDataFrame for features that are already present in it.
        If True, prints a warning and overwrites columns.
        If False, throws a RuntimeError.
        Defaults to False to protect user data.
        Full list of columns that will be created is stored in the
        FEATURE_COLUMN_NAMES attribute.
    :type overwrite_columns: boolean
    :param prune_features:
        Flag that calls the method to prune obviously useless features.
        The following pruning strategies are employed:
            1. Discards all 'string' features, such as ``month_lbl``.
            2. If input TimeSeriesDataFrame's time index has only dates, and
             no time component, all hour/minute/etc features are removed.
            3. Any features with zero variance in them are removed.
            4. Finally, correlation matrix is constructed for all remaining
             features. From each pair such that the absolute value of
             cross-correlation across features exceeds ``correlation_cutoff``
             one of the features is discarded. Example is quarter of year and
             month of year for quarterly time series data - these two features
             are perfectly correlated.
    :type prune_features: boolean
    :param correlation_cutoff:
        If ``prune_features`` is ``True``, features that have
        ``abs(correlation)`` of ``correlation_cutoff`` or higher will be
        discarded. For example, for quarterly time series both quarter of
        year and month of year can be constructed, but they will be perfectly
        correlated. Only one of these features will be preserved.
        Note that ``correlation_cutoff`` must be between 0 and 1, signs of
        correlations are discarded. Correlation with target is not computed
        to avoid overfitting and target leaks. Default value is 0.99, which
        preserves most features, lower values will prune features more
        aggressively.
    :type correlation_cutoff: float
    :param force_feature_list:
        A list of time index features to create. Must be a subset of the full feature list.
        If `force_feature_list` is specified, `prune_features` and `correlation_cutoff`
        settings are ignored.
    :type force_feature_list: list
    """

    _FEATURE_COLUMN_NAMES = ['year', 'year_iso', 'half', 'quarter', 'month',
                             'month_lbl', 'day', 'hour', 'minute', 'second',
                             'am_pm', 'am_pm_lbl', 'hour12', 'wday',
                             'wday_lbl', 'qday', 'yday', 'week']
    _datetime_sub_feature_names = ['Year', 'Month', 'Day', 'DayOfWeek',
                                   'DayOfYear', 'QuarterOfYear', 'WeekOfMonth',
                                   'Hour', 'Minute', 'Second']

    # constructor
    def __init__(self, overwrite_columns=False, prune_features=True,
                 correlation_cutoff=0.99, country_or_region=None,
                 force_feature_list=None, freq=None,
                 datetime_columns=None, logger=None):
        """Create a time_index_featurizer."""
        self.overwrite_columns = overwrite_columns
        self.prune_features = prune_features
        self.correlation_cutoff = correlation_cutoff
        self.country_or_region = country_or_region
        self.force_feature_list = force_feature_list
        self.freq = freq
        self.holidays = None
        self.enable_holiday = False
        self.datetime_columns = datetime_columns

        self._init_logger(logger)

    # making a read-only property of class instance, hence no setter method
    @property
    def FEATURE_COLUMN_NAMES(self):
        """Full set of new feature columns that can be created by this transform."""
        return self._FEATURE_COLUMN_NAMES.copy()

    @property
    def force_feature_list(self):
        """Explicit list of feature columns to make, regardless of pruning settings."""
        return self._force_feature_list

    @force_feature_list.setter
    def force_feature_list(self, val):
        if val is not None and not isinstance(val, list):
            raise TypeError('`force_feature_list` must be a list.')

        if val is not None:
            invalid_features = [ft for ft in val if ft not in self._FEATURE_COLUMN_NAMES]
            if len(invalid_features) > 0:
                raise ValueError(
                    '`force_feature_list` has invalid features: {}'.format(invalid_features))

        self._force_feature_list = val

    def _check_inputs(self, X):
        """
        Check if input X is a TimeSeriesDataFrame.

        Then check if features created will overwrite any of the columns in X.
        Raise an exception if this happens and users did not opt into this behavior.
        """
        # making sure X is a tsdf
        if not isinstance(X, TimeSeriesDataFrame):
            raise NotTimeSeriesDataFrameException(
                Messages.XFORM_INPUT_IS_NOT_TIMESERIESDATAFRAME)
        # unless instructed to overwrite, will raise exception
        existing_columns = set(X.columns)
        overlap = set(self.FEATURE_COLUMN_NAMES).intersection(existing_columns)
        # if overwrites were to happen:
        if len(overlap) > 0:
            message = 'Some of the existing columns in X will be ' + \
                'overwritten by the transform: {0}. '.format(overlap)
            # if told to overwrite - warn
            if self.overwrite_columns:
                warn(message, UserWarning)
            else:
                # if not told to overwrite - raise exception
                error_message = message + "Set 'overwrite_columns' to True " + \
                    'to overwrite columns in X, currently it is {}'.format(
                        self.overwrite_columns)
                raise RuntimeError(error_message)

    def _construct_features_from_time_index(self, X):
        """Extract features from time_index attributes from a TimeSeriesDataFrame object."""
        # sanity check
        self._check_inputs(X)
        # precompute objects we will need later
        _isocalendar = [x.isocalendar() for x in X.time_index]
        _months = X.time_index.month.values
        _hour = X.time_index.hour.values
        _am_pm_lbl = ['am' if x < 12 else 'pm' for x in _hour]
        _qday_df = construct_day_of_quarter(X)
        # start working
        result = X.copy()
        result['year'] = X.time_index.year.values
        result['year_iso'] = [x[0] for x in _isocalendar]
        result['half'] = [1 if month < 7 else 2 for month in _months]
        result['quarter'] = X.time_index.quarter.values
        result['month'] = _months
        result['month_lbl'] = [x.strftime('%B') for x in X.time_index]
        result['day'] = X.time_index.day.values
        result['hour'] = X.time_index.hour.values
        result['minute'] = X.time_index.minute.values
        result['second'] = X.time_index.second.values
        result['am_pm'] = [1 if x == 'pm' else 0 for x in _am_pm_lbl]
        result['am_pm_lbl'] = _am_pm_lbl
        result['hour12'] = [x if x <= 12 else x - 12 for x in _hour]
        result['wday'] = X.time_index.weekday.values
        result['wday_lbl'] = X.time_index.weekday_name.values
        result['qday'] = _qday_df['day_of_quarter'].values
        result['yday'] = X.time_index.dayofyear.values
        result['week'] = X.time_index.weekofyear.values

        if self.country_or_region is not None and (self.freq == 'D' or X.time_index.inferred_freq == 'D'):
            self.enable_holiday = True
            result = self._get_holidays(result)

        return result

    def _get_holidays(self, X):
        """
        Get the enriched holiday names appended to X.

        :param X: Input data
        :type X: TimeSeriesDataFrame

        :return: Data with holiday features appended
        :rtype: TimeSeriesDataFrame
        """
        try:
            from .publicholidays.holidays import Holidays
        except ImportError:
            warn("Failed to find holiday dependency, no holiday feature will be generated", ImportWarning)
            self.enable_holiday = False
            return X

        if self.holidays is None:
            self.holidays = Holidays()
        holidays_api = cast(Holidays, self.holidays)
        _date_column_name = X.index.names[0]
        _holidays = holidays_api.get_holidays_in_range(start_date=pd.to_datetime(X.time_index.min().date()),
                                                       end_date=pd.to_datetime(X.time_index.max().date()),
                                                       country_code=self.country_or_region)
        _holidays = _holidays.rename(columns={'Date': _date_column_name,
                                              'Name': TimeSeriesInternal.HOLIDAY_COLUMN_NAME})

        rs = X.join(_holidays.set_index(_date_column_name), how='left')

        # set the isPaidTimeOff explicitly
        rs[TimeSeriesInternal.PAID_TIMEOFF_COLUMN_NAME] = [1 if not np.isnan(x) and x else 0
                                                           for x in rs['IsPaidTimeOff']]
        rs.drop(columns=['IsPaidTimeOff'], inplace=True)

        return rs

    def _get_noisy_features(self, X):
        """
        Several heuristics to get the noisy features returned by the transform.

        The following strategies are used:
            1. Discards all 'string' features, such as ``month_lbl``.
            2. If input TimeSeriesDataFrame's time index has only dates, and
              no time component, all hour/minute/etc features are removed.
            3. Any features with zero variance in them are removed.
            4. Finally, correlation matrix is constructed for all remaining
              features. From each pair such that the absolute value of
              cross-correlation across features exceeds
              ``self.correlation_cutoff`` one of the features is discarded.
              Example is quarter of year and month of year for quarterly
              time series data - these two features are perfectly correlated.

        :return: a list of columns to be dropped in feature pruning
        """
        features_to_drop_all = []   # type: List[str]

        # making sure X is a tsdf
        if not isinstance(X, TimeSeriesDataFrame):
            raise NotTimeSeriesDataFrameException(
                Messages.XFORM_INPUT_IS_NOT_TIMESERIESDATAFRAME)
        # check that features that will be trimmed as present
        existing_columns = set(X.columns)
        overlap = set(self.FEATURE_COLUMN_NAMES).intersection(existing_columns)
        if len(overlap) == 0:
            warning_message = "Input TimeSeriesDataFrame X has no " + \
                "features from X.time_index that can be pruned! Found " + \
                "none of these features: {0}".format(self.FEATURE_COLUMN_NAMES)
            warn(warning_message, UserWarning)
            return features_to_drop_all
        remaining_colnames = self._FEATURE_COLUMN_NAMES.copy()

        # Step 1: get rid of 'textual' features
        features_to_drop = ['month_lbl', 'wday_lbl', 'am_pm_lbl']
        features_to_drop_all += features_to_drop
        remaining_colnames = subtract_list_from_list(remaining_colnames,
                                                     features_to_drop)

        # Step 2: prune all within-day features if no timestamps in index
        if datetime_is_date(X.time_index):
            features_to_drop = ['hour', 'minute', 'second', 'am_pm', 'hour12']
            features_to_drop_all += features_to_drop
            remaining_colnames = subtract_list_from_list(remaining_colnames,
                                                         features_to_drop)

        # Step 3: find and remove zero-variance features
        _stdevs = np.std(X[remaining_colnames].values, axis=0)
        features_to_drop = [x[0] for x in zip(remaining_colnames, _stdevs)
                            if x[1] == 0]
        features_to_drop_all += features_to_drop
        remaining_colnames = subtract_list_from_list(remaining_colnames,
                                                     features_to_drop)

        # Step 4: prune features that have strong correlation with each other
        # We will remove all features with correlation that exceeds cutoff
        if remaining_colnames:
            corr_mat = abs(X[remaining_colnames].corr())
            # take column max of an upper-triangular component
            # k=1 excludes main diagonal, which has 1 everywhere
            max_corr = np.max(np.triu(corr_mat, k=1), axis=0)
            features_to_drop = [x[1] for x in zip(
                max_corr >= self.correlation_cutoff, remaining_colnames) if x[0]]
            features_to_drop_all += features_to_drop

        return features_to_drop_all

    def _get_feature_names_to_drop(self, X):
        """Create a list of feature columns that should be dropped from X due to user input or auto-pruning."""
        if self.force_feature_list is not None:
            drop_features = list(set(self._FEATURE_COLUMN_NAMES) -
                                 set(self.force_feature_list))
        elif self.prune_features:
            result = self._construct_features_from_time_index(X)
            result = self._construct_features_from_time_columns(result)
            drop_features = self._get_noisy_features(result)
        else:
            drop_features = []

        return drop_features

    @property
    def overwrite_columns(self):
        """See `overwrite_columns` parameter."""
        return self._overwrite_columns

    @overwrite_columns.setter
    def overwrite_columns(self, value):
        if not isinstance(value, bool):
            error_message = ("Input 'overwrite_column' must be True or " +
                             "False, instead received {}".format(value))
            raise TypeError(error_message)
        self._overwrite_columns = value

    # prune features flag
    @property
    def prune_features(self):
        """See `prune_features` parameter."""
        return self._prune_features

    @prune_features.setter
    def prune_features(self, value):
        if not isinstance(value, bool):
            error_message = ("Input 'prune_features' must be True or " +
                             "False, instead received {}".format(value))
            raise TypeError(error_message)
        self._prune_features = value

    # define correlation cutoff get/set with checks
    @property
    def correlation_cutoff(self):
        """See `correlation_cutoff` parameter."""
        return self._correlation_cutoff

    @correlation_cutoff.setter
    def correlation_cutoff(self, value):
        type_is_numeric(type(value),
                        "correlation_cutoff must be a real number!")
        if (value < 0) or (value > 1):
            raise ValueError("correlation_cutoff must be between 0 and 1!")
        self._correlation_cutoff = value

    @function_debug_log_wrapped
    def fit(self, X, y=None):
        """
        Fit the transform.

        Determine which features, if any, should be pruned.

        :param X: Input data
        :type X: :class:`ftk.dateframets.TimeSeriesDataFrame`

        :param y: Passed on to sklearn transformer fit

        :return: Fitted transform
        :rtype: TimeIndexFeaturizer
        """
        self._features_to_prune = self._get_feature_names_to_drop(X)

        return self

    @function_debug_log_wrapped
    def transform(self, X):
        """
        Create time index features for an input data frame.

        :param X: Input data
        :type X: :class:`ftk.dateframets.TimeSeriesDataFrame`

        :return: Data frame with time index features
        :rtype: :class:`ftk.dateframets.TimeSeriesDataFrame`
        """
        result = self._construct_features_from_time_index(X)
        result = self._construct_features_from_time_columns(result)
        if len(self._features_to_prune) > 0:
            result = result.drop(self._features_to_prune, axis=1)
        return result

    @function_debug_log_wrapped
    def fit_transform(self, X, y=None):
        """
        Apply `fit` and `transform` methods in sequence.

        Determine which features, if any, should be pruned.

        :param X: Input data
        :type X: :class:`ftk.dateframets.TimeSeriesDataFrame`

        :param y: Passed on to sklearn transformer fit

        :return: Data frame with time index features
        :rtype: :class:`ftk.dateframets.TimeSeriesDataFrame`
        """
        return self.fit(X, y).transform(X)

    def preview_non_holiday_feature_names(self, X):
        """
        Get the non-Holiday time features names that would be made if the transform were applied to X.

        :param X: Input data
        :type X: TimeSeriesDataFrame

        :return: time feature names
        :rtype: list of strings
        """
        features_to_drop = self._get_feature_names_to_drop(X)
        return subtract_list_from_list(self._FEATURE_COLUMN_NAMES, features_to_drop)

    def preview_time_feature_names(self, X):
        """
        Get the time features names that would be made if the transform were applied to X.

        :param X: Input data
        :type X: TimeSeriesDataFrame

        :return: time feature names
        :rtype: list of strings
        """
        features_to_drop = self._get_feature_names_to_drop(X)
        feature_names = self.FEATURE_COLUMN_NAMES.copy()
        if self.enable_holiday:
            feature_names.append(TimeSeriesInternal.HOLIDAY_COLUMN_NAME)
            feature_names.append(TimeSeriesInternal.PAID_TIMEOFF_COLUMN_NAME)
        return subtract_list_from_list(feature_names, features_to_drop)

    # TODO: Merge this logic with time index feature generation
    def preview_datetime_column_featured_names(self):
        """
        Get the time features names that generated on other datetime columns(not time index).

        :return: time feature names
        :rtype: list of strings
        """
        all_features = []
        for raw_name in self.datetime_columns:
            for feature in self._datetime_sub_feature_names:
                all_features.append(raw_name + "_" + feature)
        return all_features

    def _construct_datatime_feature(self, x: pd.Series) -> pd.DataFrame:
        x_columns = [x.name + "_" + s for s in self._datetime_sub_feature_names]

        return pd.DataFrame(data=pd.concat([
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
        ], axis=1).values, columns=x_columns)

    def _construct_features_from_time_columns(self, X: TimeSeriesDataFrame) -> TimeSeriesDataFrame:
        if self.datetime_columns is None or len(self.datetime_columns) == 0:
            return X
        for col in self.datetime_columns:
            time_features = self._construct_datatime_feature(X[col])
            for c in time_features.columns.values:
                X[c] = time_features[c].values
        X = X.drop(self.datetime_columns, axis=1)
        return X
