# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Classes and functions to validate the model using Rolling Origin Cross-Validation evaluation strategy."""
import numpy as np
import pandas as pd
from sklearn.model_selection import BaseCrossValidator
from sklearn.utils import indexable
from sklearn.utils.validation import _num_samples

from automl.client.core.common.exceptions import ConfigException, DataException, ClientException
from automl.client.core.common.time_series_data_frame import \
    TimeSeriesDataFrame


class RollingOriginValidator(BaseCrossValidator):
    """
    A subclass of sklearn.BaseCrossValidator_ which creates temporal splits in rows of data.

    Provides train/test indices to split data in train/test sets for
    rolling forecast origin cross-validation

    Defines rolling forecast origin cross-validation folds for the data
    for use as inputs in machine learning parameter tuning.

    .. _sklearn.BaseCrossValidator: http://scikit-learn.org/stable/modules/cross_validation.html

    :param n_splits: Number of splits. Must be at least 1.
    :type n_splits: int, default=3
    :param n_step:
        Number of periods between the origin_time of one CV fold and the next fold. For
        example, if `n_step` = 3 for daily data, the origin time for each fold will be
        three days apart.
    :type n_step: int, default=1
    :param max_horizon: The maximum number of periods into the future to include in the testing data.
    :type max_horizon: int

    Examples:
    >>> rollcv = RollingOriginValidator(n_splits=3)
    >>> df = TimeSeriesDataFrame(
    ...    {'category': ['a']*6 + ['b']*6,
    ...    'date': pd.to_datetime(['2017-01-02', '2017-01-03', '2017-01-04',
    ...                            '2017-01-05', '2017-01-06', '2017-01-07']*2),
    ...    'values' : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    ...    'origin': pd.to_datetime(['2017-01-01', '2017-01-02', '2017-01-03',
    ...                              '2017-01-04', '2017-01-05', '2017-01-06']*2)
    ...    }, time_colname='date', grain_colnames= 'category', origin_time_colname='origin')
    >>> splits = rollcv.split(df)

    """

    def __init__(self, n_splits=3, n_step=1, max_horizon=None):
        """Create a RollingOriginValidator."""
        # TODO: add ```max_train_size``` argument later so that previous training
        # data will be dropped when the training data size grows exceeding the
        # max_train_size. This could be helpful for controlling the model
        # training time for data with long history.
        super().__init__()
        self.n_splits = n_splits
        self.max_horizon = max_horizon
        self.n_step = n_step

    @property
    def n_step(self):
        """
        Get the number of periods between the origin of one CV fold and the next.

        For example, if `n_step` = 3 for daily data, the origin time for each fold
        will be three days apart.
        """
        return self.__n_step

    @n_step.setter
    def n_step(self, val):
        if isinstance(val, int):
            if val < 1:
                raise ConfigException('n_step must be a positive int.')
            self.__n_step = val
        elif val is None:
            self.__n_step = val
        else:
            raise ConfigException(
                'n_step values must be a positive int.')

    @property
    def max_horizon(self):
        """
        Max value of horizons for the cross-validation folds.

        If None all data will the same `origin_time` are put into the
        same CV-fold.
        """
        return self.__max_horizon

    @max_horizon.setter
    def max_horizon(self, val):
        if val is None:
            self.__max_horizon = None
        elif isinstance(val, int):
            if val < 1:
                raise ConfigException('max_horizon must be positive.')
            self.__max_horizon = val
        else:
            raise ConfigException(
                'max_horizon values must be a positive int.')

    def get_n_splits(self, X=None, y=None, groups=None):
        """
        Return the number of splitting iterations in the cross-validator.

        :param X: Always ignored, exists for compatibility.
        :type X: object

        :param y: Always ignored, exists for compatibility.
        :type y: object

        :param groups: Always ignored, exists for compatibility.
        :type groups: object

        :return:
            The number of splitting iterations in the cross-validator.
        :rtype: int
        """
        return self.n_splits

    def split(self, X, y=None, groups=None):
        """
        Generate indices to split data into training and test set.

        :param X:
            Training data, where n_samples is the number of samples
            and n_features is the number of features.
        :type X: TimeSeriesDataFrame, shape (n_samples, n_features)

        :param y:
            Always ignored, exists for compatibility.
        :type y: array-like, shape (n_samples,), optional

        :param groups:
            Always ignored, exists for compatibility.
        :type groups: array-like, with shape (n_samples,), optional

        :return:
           Tuple of the training set and testing set indices for that
           split.
        :rtype: Generator of tuples of two ndarrays
        """
        if not isinstance(X, TimeSeriesDataFrame):
            raise ClientException(
                "X not a TimeSeriesDataFrame.")
        time_value = X.time_index
        fcast_index = X.origin_time_index
        freq = X.infer_freq()
        has_origin = True
        if X.infer_single_freq() is None:
            raise DataException(
                "Could not infer a single frequency for all time-series.")
        if fcast_index is None:
            if self.max_horizon is None:
                fcast_index = time_value - freq
            else:
                has_origin = False
        # make the arrays indexable for cross-validation
        if has_origin:
            X, y, groups, time_value, fcast_index = indexable(  # pylint: disable=unbalanced-tuple-unpacking
                X, y, groups, time_value, fcast_index)
        else:
            X, y, groups, time_value = indexable(  # pylint: disable=unbalanced-tuple-unpacking
                X, y, groups, time_value)
        n_samples = _num_samples(X)
        n_splits = self.n_splits
        if self.max_horizon is not None:
            num_horizon = self.max_horizon
            time_horizon = self.max_horizon * freq
        else:
            num_horizon = len((fcast_index - time_value).unique())
        n_step_temp = self.n_step if self.n_step is not None else 1
        if (n_splits - 1) * n_step_temp + 1 + num_horizon > n_samples:
            raise DataException(
                ("Series is too short for the requested number of CV folds or requested horizon." +
                 "Cannot have (n_splits - 1)*n_step + 1 + num_horizon = {0} greater " +
                 "than the number of samples: {1}.").format(
                     (n_splits - 1) * n_step_temp + 1 + num_horizon, n_samples))
        if has_origin:
            fcast_index_sort = fcast_index.unique().sort_values()
        else:
            fcast_index_sort = time_value.unique().sort_values()[:-1]

        if self.n_step is not None:
            index_delta = freq * self.n_step
            fold_origins = pd.date_range(end=fcast_index_sort[-1], periods=n_splits,
                                         freq=index_delta)
        else:
            fold_origins = fcast_index_sort[-n_splits:]

        for fcast_time in fold_origins:
            origin_valid = fcast_index == fcast_time if has_origin else \
                time_value > fcast_time
            if self.max_horizon is not None:
                horizon_valid = time_value <= fcast_time + time_horizon
            else:
                horizon_valid = np.array([True] * len(time_value))
            yield(np.array(np.where(time_value <= fcast_time)).flatten(),
                  np.array(np.where(np.logical_and(origin_valid, horizon_valid))).flatten())
