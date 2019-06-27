# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Decompose the target value to the Trend and Seasonality."""
from typing import Optional, Any, Tuple, List, Callable, Union, Dict, Iterator, cast
import numpy as np
import pandas as pd
import warnings

from itertools import product
from pandas.tseries.frequencies import to_offset
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.holtwinters import HoltWintersResultsWrapper

from .time_series_imputer import TimeSeriesImputer
from .forecasting_base_estimator import AzureMLForecastTransformerBase
from automl.client.core.common.time_series_data_frame import TimeSeriesDataFrame
from automl.client.core.common.forecasting_utils import get_period_offsets_from_dates, grain_level_to_dict
from automl.client.core.common.forecasting_ts_utils import detect_seasonality_tsdf, get_stl_decomposition
from automl.client.core.common.forecasting_exception import NotSupportedException
from automl.client.core.common.exceptions import DataException, ConfigException, ClientException
from automl.client.core.common.constants import TimeSeriesInternal


def _complete_short_series(series_values: pd.Series,
                           season_len: int) -> Union[np.ndarray, pd.Series]:
    """
    Complete the two seasons required by statsmodels.

    statsmodels requires at least two full seasons of data
    in order to train. "Complete" the data if this requirement
    is not met.
    If there is less than one full season, carry the last observation
    forward to complete a full season.
    Use a seasonal naive imputation to fill in series values
    so the completed series has length at least 2*season_len
    :param series_values: The series with data.
    :type series_values: pd.Series
    :param season_len: The number of periods in the season.
    :type season_len: int
    :returns: the array with extended data or pd.Series.
    :rtype: np.ndarray pr pd.Series

    """
    series_len = len(series_values)

    # Nothing to do if we already have at least two seasons of data
    if series_len >= 2 * season_len:
        return series_values

    if series_len < season_len:
        last_obs = series_values[-1]
        one_season_ext = np.repeat(last_obs, season_len - series_len)
    else:
        one_season_ext = np.array([])

    # Complete a full season
    series_values_ext = np.append(series_values, one_season_ext)

    # Complete the second season via seasonal naive imputation
    num_past_season = len(series_values_ext) - season_len
    series_first_season = series_values_ext[:season_len]
    series_snaive_second_season = series_first_season[num_past_season:]

    # Get the final bit of the series by seasonal naive imputation
    series_snaive_end = series_values_ext[season_len:]

    # Concatenate all the imputations and return
    return np.concatenate((series_values_ext,
                           series_snaive_second_season,
                           series_snaive_end))


def _sm_is_ver9() -> bool:
    """
    Try to determine if the statsmodels version is 0.9.x.

    :returns: True if the statsmodels is of 0.9.x version.
    :rtype: bool

    """
    try:
        import pkg_resources
        sm_ver = pkg_resources.get_distribution('statsmodels').version
        major, minor = sm_ver.split('.')[:2]
        if major == '0' and minor == '9':
            return True
    except BaseException:
        return True

    return False


def _extend_series_for_sm9_bug(series_values: np.ndarray,
                               season_len: int,
                               model_type: Tuple[str, str, bool]) -> np.ndarray:
    """
    Fix the statsmodel 0.9.0 bug.

    statsmodel 0.9.0 has a bug that causes division by zero during
    model fitting under the following condition:
    series_length = num_model_params + 3.
    Try to detect this condition and if it is found, carry the last
    observation forward once in order to increase the series length.
    This bug is fixed in the (dev) version 0.10.x.
    :param series_values: the series with data.
    :type series_values: np.ndarray
    :param season_len: The number of periods in the season.
    :type season_len: int
    :param model_type: The type of a model used.
    :type model_type: tuple

    """
    trend_type, seas_type, damped = model_type
    num_params = 2 + 2 * (trend_type != 'N') + 1 * (damped) + \
        season_len * (seas_type != 'N')

    if len(series_values) == num_params + 3:
        series_ext = np.append(series_values, series_values[-1])
    else:
        series_ext = series_values

    return series_ext


class STLFeaturizer(AzureMLForecastTransformerBase):
    """
    The class for decomposition of input data to the seasonal and trend component.

    If seasonality is not presented by int or np.int64 ConfigException is raised.
    :param seasonality: Time series seasonality. If seasonality is set to -1, it will be inferred.
    :type seasonality: int
    :param seasonal_feature_only: If true, the transform creates a seasonal feature, but not a trend feature.
    :type seasonal_feature_only: bool
    :raises: ConfigException

    """
    SEASONAL_COMPONENT_NAME = 'seasonal'
    TREND_COMPONENT_NAME = 'trend'

    def __init__(self,
                 seasonal_feature_only: bool = False,
                 seasonality: int = TimeSeriesInternal.SEASONALITY_VALUE_DETECT) -> None:
        """Constructor."""
        if not isinstance(seasonality, int):
            raise ConfigException(("The seasonality for the STL featurizer should be an integer, but got type {}. \
                Please set the seasonality to an integer value.").format(type(seasonality)))
        self.seasonal_feature_only = seasonal_feature_only
        self._seasonality = seasonality
        self._stls = {}  # type: Dict[Tuple[str], Dict[str, np.ndarray]]
        self._es_models = {}  # type: Dict[Tuple[str], HoltWintersResultsWrapper]

        # We will use an additive Holt-Winters model with no seasonal component to extrapolate trend
        self.es_type = 'AN'
        self.use_boxcox = False
        self.use_basinhopping = False
        self.damped = False
        self.selection_metric = 'aic'
        self._char_to_statsmodels_opt = \
            {'A': 'add', 'M': 'mul', 'N': None}
        self._freq = 0
        self._first_observation_dates = {}  # type: Dict[Tuple[str], pd.Timestamp]
        self._last_observation_dates = {}  # type: Dict[Tuple[str], pd.Timestamp]
        self._sm9_bug_workaround = _sm_is_ver9()
        self._ts_value = None  # Optional[str]

    def data_check(self, X: TimeSeriesDataFrame) -> None:
        """
        Perform data check before transform will be called.

        If the data are not valid the DataException is being raised.
        :param X: The TimeSeriesDataFrame with data to be transformed.
        :type X: TimeSeriesDataFrame
        :raises: DataException
        """
        for grain, df_one in X.groupby_grain():
            if grain not in self._last_observation_dates.keys() or \
               grain not in self._first_observation_dates.keys():
                raise DataException('The grain {} is not in the training set.'.format(grain))
            if df_one.time_index.min() < self._first_observation_dates[grain]:
                raise DataException('The forecast date cannot be less then training date.')

    def _get_imputed_df(self, X: TimeSeriesDataFrame) -> TimeSeriesDataFrame:
        """
        Impute the missing y values.

        :param X: Input data
        :type X: :class:`TimeSeriesDataFrame`
        :rtype: TimeIndexFeaturizer

        """
        # Imopute values by forward fill the values.
        imputer = TimeSeriesImputer(input_column=X.ts_value_colname,
                                    option='fillna',
                                    method='ffill',
                                    freq=self._freq)
        # We forward filled values at the middle and at the end
        # of a data frame. We will fill the begin with zeroes.
        zero_imputer = TimeSeriesImputer(input_column=X.ts_value_colname,
                                         value=0,
                                         freq=self._freq)
        imputed_X = imputer.transform(X)
        return cast(TimeSeriesDataFrame, zero_imputer.transform(imputed_X))

    def fit(self,
            X: TimeSeriesDataFrame,
            y: Optional[np.ndarray] = None) -> 'STLFeaturizer':
        """
        Determine trend and seasonality.

        A DataException is raised if any time-series grains are shorter than the seasonality for the dataframe.
        :param X: Input data
        :type X: :class:`TimeSeriesDataFrame`
        :param y: Not used, added for back compatibility with scikit**-**learn.
        :type y: np.ndarray
        :return: Fitted transform
        :rtype: TimeIndexFeaturizer
        :raises: DataException

        """
        if X.origin_time_colname is not None:
            raise ClientException('Input dataframe is malformed for this transform (origin times are present). \
                This is an internal error; please report the message contents to the product support team.')
        self._ts_value = X.ts_value_colname
        self._freq = X.infer_freq()

        # We have to impute missing values for correct
        # of seasonality detection.
        imputed_X = self._get_imputed_df(X)

        if self.seasonality == TimeSeriesInternal.SEASONALITY_VALUE_DETECT:
            self._seasonality = detect_seasonality_tsdf(imputed_X)

        for grain, df_one in imputed_X.groupby_grain():
            self._fit_one_grain(grain, df_one)

        return self

    def transform(self,
                  X: TimeSeriesDataFrame) -> TimeSeriesDataFrame:
        """
        Create time index features for an input data frame.

        **Note** in this method we assume that we do not know the target value.
        :param X: Input data
        :type X: :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`
        :return: Data frame with trand and seasonality column.
        :rtype: :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`
        :raises: Exception
        """
        if not self._stls.keys() or self.seasonality == -1:
            raise ClientException("STL featurizer transform method called before fit.")
        self.data_check(X)
        return self._apply_func_to_grains(self._transform_one_grain, X)

    def fit_transform(self,
                      X: TimeSeriesDataFrame,
                      y: Optional[np.ndarray] = None) -> TimeSeriesDataFrame:
        """
        Apply `fit` and `transform` methods in sequence.

        **Note** that because in this case we know the target value
        and hence we can use the statsmodel of trend inference.
        :param X: Input data.
        :type X: :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`
        :param y: Not used, added for back compatibility with scikit**-**learn.
        :type y: np.ndarray
        :return: Data frame with trand and seasonality column.
        :rtype: :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`

        """
        self.fit(X)
        return self._apply_func_to_grains(self._fit_transform_one_grain, X)

    def preview_column_names(self,
                             tsdf: Optional[TimeSeriesDataFrame] = None,
                             target: Optional[str] = None) -> List[str]:
        """
        Return the list of columns to be generated based on data in the data frame X.

        TimeSeriesDataFrame or target column, but not both should be provided.
        If neither or both are provided the DataException is raised.
        :param tsdf: The TimeSeriesDataFrame to generate column names for.
        :type tsdf: TimeSeriesDataFrame
        :param target: The name of a target column.
        :type target: str
        :returns: the list of generated columns.
        :rtype: list
        :raises: DataException

        """
        if (tsdf is None and target is None) or\
           (tsdf is not None and target is not None):
            raise DataException('tsdf or or target, but not both should be provided.')

        target_name = tsdf.ts_value_colname if tsdf is not None else cast(str, target)
        season_name, trend_name = self._get_column_names(target_name)

        return [season_name] if self.seasonal_feature_only else [season_name, trend_name]

    def _fit_one_grain(self,
                       grain: Tuple[str],
                       df_one: TimeSeriesDataFrame) -> None:
        """
        Do the STL decomposition of a single grain and save the result object.

        If one of grains contains fewer then one dimensions the DataException is raised.
        :param grain: the tuple of grains.
        :type grain: tuple
        :param df_one: The TimeSeriesDataFrame with one grain.
        :type df_one: TimeSeriesDataFrame
        :raises: DataException

        """
        self._first_observation_dates[grain] = df_one.time_index.min()
        self._last_observation_dates[grain] = df_one.time_index.max()
        if df_one.shape[0] < 2:
            raise DataException(
                ('STL featurizer requires at least two data points in each grain. \
                    Grain {} contains only one point. Please remove this grain from the dataset.').format(grain))
        if self.seasonality >= len(df_one):
            raise DataException(("Must have at least a full season of data for each grain. \
                                  Grain {} has {} observations with seasonality={}")
                                .format(grain, len(df_one), self.seasonality))
        series_vals = df_one[df_one.ts_value_colname].values
        seasonal, trend, resid = get_stl_decomposition(series_vals, seasonality=self.seasonality)

        self._stls[grain] = {STLFeaturizer.SEASONAL_COMPONENT_NAME: seasonal,
                             STLFeaturizer.TREND_COMPONENT_NAME: trend}
        self._es_models[grain] = self._get_trend_model(trend) \
            if not self.seasonal_feature_only else None

    def _fit_transform_one_grain(self,
                                 grain: Tuple[str],
                                 df_one: TimeSeriesDataFrame) -> TimeSeriesDataFrame:
        """
        Infer the seasonality and trend for single grain.

        In this case we assume that fit data are the same as train data.
        This method is used in the fit_transform.
        :param grain: the tuple of grains.
        :type grain: tuple
        :param df_one: The TimeSeriesDataFrame with one grain.
        :type df_one: TimeSeriesDataFrame
        :returns: The data frame with season and trend columns.
        :rtype: TimeSeriesDataFrame
        """
        stl_result = self._stls[grain]
        return self._assign_trend_season(
            df_one, stl_result[STLFeaturizer.SEASONAL_COMPONENT_NAME],
            stl_result[STLFeaturizer.TREND_COMPONENT_NAME])

    def _transform_one_grain(self,
                             grain: Tuple[str],
                             df_one: TimeSeriesDataFrame) -> TimeSeriesDataFrame:
        """
        Compute seasonality and trend features for a single grain.

        :param grain: the tuple of grains.
        :type grain: tuple
        :param df_one: The TimeSeriesDataFrame with one grain.
        :type df_one: TimeSeriesDataFrame
        :returns: The data frame with season and trend columns.
        :rtype: TimeSeriesDataFrame
        """

        # Define which part of data is in training and which in testing set.
        # The data already present in training set. We know the trend for them.
        df_one_train = None  # type: Optional[TimeSeriesDataFrame]
        # The new data, we need to forecast trend.
        df_one_pred = None  # type: Optional[TimeSeriesDataFrame]
        # Split the data on training and prediction part.
        if df_one.time_index.min() < self._last_observation_dates[grain]:
            df_one_train = df_one[:self._last_observation_dates[grain]]
        if df_one.time_index.max() > self._last_observation_dates[grain]:
            df_one_pred = df_one[self._last_observation_dates[grain] + to_offset(self._freq):]

        stl_result = self._stls[grain]
        if df_one_train is not None:
            offset = len(
                pd.date_range(
                    self._first_observation_dates[grain],
                    df_one.time_index.min(),
                    freq=self._freq)) - 1
            end = df_one_train.shape[0] + offset
            df_one_train = self._assign_trend_season(df_one_train,
                                                     stl_result[STLFeaturizer.SEASONAL_COMPONENT_NAME][offset:end],
                                                     stl_result[STLFeaturizer.TREND_COMPONENT_NAME][offset:end])

        if df_one_pred is not None:
            model = self._es_models[grain]
            ts_value = cast(str, self._ts_value)
            season_name, trend_name = self._get_column_names(ts_value)
            try:
                horizon = get_period_offsets_from_dates(
                    self._last_observation_dates[grain],
                    df_one_pred.time_index,
                    self._freq).max()
            except KeyError:
                raise DataException('Unable to determine horizon for grain {}'.format(grain))

            fcast_start = self._last_observation_dates[grain] + self._freq
            fcast_dates = pd.date_range(start=fcast_start,
                                        periods=horizon,
                                        freq=self._freq)
            # Generate seasons for all the time periods beginning from the one next to last
            # date in the training set.
            start_season = len(pd.date_range(start=self._first_observation_dates[grain],
                                             end=self._last_observation_dates[grain],
                                             freq=self._freq)) % self.seasonality
            seasonal = [stl_result[STLFeaturizer.SEASONAL_COMPONENT_NAME][start_season + season % self.seasonality]
                        for season in range(len(fcast_dates))]

            if model is not None:
                point_fcast = model.forecast(steps=horizon)
            else:
                point_fcast = np.repeat(np.NaN, horizon)
            # Construct the time axis that aligns with the forecasts
            forecast_dict = {
                df_one_pred.time_colname: fcast_dates,
                season_name: seasonal}
            if not self.seasonal_feature_only:
                forecast_dict.update({trend_name: point_fcast})
            if df_one_pred.grain_colnames:
                forecast_dict.update(grain_level_to_dict(df_one_pred.grain_colnames,
                                                         grain))
            # Merge the data sets and consequently, trim the unused periods.
            tsdf_temp = TimeSeriesDataFrame(forecast_dict,
                                            time_colname=df_one_pred.time_colname,
                                            grain_colnames=df_one_pred.grain_colnames)
            df_one_pred = df_one_pred.merge(tsdf_temp, left_index=True, right_index=True)
        if df_one_pred is None:
            # In this case df_one_train have to be not None.
            # This means fit_transform was called.
            return cast(TimeSeriesDataFrame, df_one_train)
        if df_one_train is None:
            # In this case df_one_pred have to be not None.
            return df_one_pred
        return cast(TimeSeriesDataFrame, pd.concat([df_one_train, df_one_pred]))

    def _assign_trend_season(self,
                             tsdf: TimeSeriesDataFrame,
                             ar_season: np.ndarray,
                             ar_trend: np.ndarray) -> TimeSeriesDataFrame:
        """
        Create the season and trend columns in the data frame.

        :param tsdf: Target data frame.
        :type tsdf: :class:`TimeSeriesDataFrame`
        :param ar_season: seasonality component.
        :type ar_season: np.ndarray
        :param ar_trend: trend component.
        :type ar_trend: np.ndarray
        :returns: The time series data frame with trend and seasonality components.
        :rtype: TimeSeriesDataFrame
        :raises: DataException

        """
        if self._ts_value is None:
            # This exception should not be raised here,
            # but enforcement of type checking requires Optopnal[str] to be
            # checked for None.
            raise DataException("Fit not called")
        season_name, trend_name = self._get_column_names(self._ts_value)

        assign_dict = {season_name: ar_season}
        if not self.seasonal_feature_only:
            assign_dict[trend_name] = ar_trend
        return cast(TimeSeriesDataFrame, tsdf.assign(**assign_dict))

    def _get_column_names(self, target: str) -> Tuple[str, str]:
        """
        Return the names of columns to be generated.

        :param tsdf: The time series data frame to generate seasonality and trend for.
        :type tsdf: TimeSeriesDataFrame
        :returns: The tuple of seasonality and trend columns.
        :rtype: tuple

        """
        return (target + TimeSeriesInternal.STL_SEASON_SUFFIX,
                target + TimeSeriesInternal.STL_TREND_SUFFIX)

    @property
    def seasonality(self) -> int:
        """
        Return the number of periods after which the series values tend to repeat.

        :returns: seasonality.
        :rtype: int

        """
        return self._seasonality

    def _get_trend_model(self,
                         series_values: np.ndarray) -> 'HoltWintersResultsWrapper':
        """
        Train the Exponential Smoothing model on single series.

        This model will be used for the trend forecasting.
        :param series_values: The series with target values.
        :type series_values: np.ndarray
        :returns: The Exponential smoothing model .
        :rtype: HoltWintersResultsWrapper

        """
        # Model type consistency checks
        self._assert_damping_valid()
        self._assert_mult_model_valid(series_values)

        # Make sure the series is long enough for fitting
        # If not, impute values to "complete" the series
        series_values = _complete_short_series(series_values, 1)

        # Internal function for fitting a statsmodel ETS model
        #  and determining if a model type should be considered in selection
        # ------------------------------------------------------------------
        def fit_sm(model_type):
            trend_type, seas_type, damped = model_type

            if self._sm9_bug_workaround:
                series_values_safe = \
                    _extend_series_for_sm9_bug(series_values, 1,
                                               model_type)
            else:
                series_values_safe = series_values

            ets_model = \
                ExponentialSmoothing(series_values_safe,
                                     trend=self._char_to_statsmodels_opt[trend_type],
                                     seasonal=self._char_to_statsmodels_opt[seas_type],
                                     damped=damped,
                                     seasonal_periods=None)

            return ets_model.fit(use_boxcox=self.use_boxcox,
                                 use_basinhopping=self.use_basinhopping)

        def model_is_valid(model_type, has_zero_or_neg):
            trend_type, seas_type, damped = model_type

            if trend_type == 'N' and damped:
                return False

            if (trend_type == 'M' or seas_type == 'M') \
                    and has_zero_or_neg:
                return False

            return True
        # ------------------------------------------------------------------

        # Make a grid of model types and select the one with minimum loss
        has_zero_or_neg = (series_values <= 0.0).any()
        type_grid = self._make_param_grid(False)
        fit_models = {mtype: fit_sm(mtype) for mtype in type_grid
                      if model_is_valid(mtype, has_zero_or_neg)}
        best_type, best_result = \
            min(fit_models.items(),
                key=lambda it: getattr(it[1], self.selection_metric))

        return best_result

    def _assert_damping_valid(self) -> None:
        """
        Make sure the damped setting is consistent with the model type setting.

        :raises: ConfigException

        """
        if self.es_type[0] == 'N' and self.damped:
            raise ConfigException(
                ('Inconsistent settings: `model_type`={0} and `damped`={1}. ' +
                 'Damping can only be applied when there is a trend term.')
                .format(self.es_type, self.damped))

    def _assert_mult_model_valid(self, series_values: pd.Series) -> None:
        """
        Make sure that multiplicative model settings are consistent.

        Currently, the underlying fit cannot handle zero or negative valued
        series with multiplicative models.

        :param series_values: The series with the values.
        :type series_values: pd.Series
        :raises: ConfigException

        """
        if 'M' in self.es_type and (series_values <= 0.0).any():
            raise ConfigException(
                ('Cannot use multiplicative model type {0} because trend ' +
                 'contains negative or zero values.')
                .format(self.es_type))

    def _make_param_grid(self, is_seasonal: bool) -> Iterator[Tuple[str, str, bool]]:
        """
        Make an iterable of model type triples (trend, seasonal, damping).

        :param is_seasonal: Does model include seasonality?
        :type is_seasonal: bool
        :returns: The model grid to be fitted for the best model selection.
        :rtype: list

        """
        mtype = self.es_type
        trend_in, seas_in = mtype
        trend_grid = [trend_in] if trend_in != 'Z' else ['A', 'M', 'N']

        if is_seasonal:
            seasonal_grid = [seas_in] if seas_in != 'Z' else ['A', 'M', 'N']
        else:
            seasonal_grid = ['N']

        damped_grid = [self.damped] \
            if self.damped is not None else [True, False]

        return product(trend_grid, seasonal_grid, damped_grid)

    def _apply_func_to_grains(self,
                              func: 'Callable[[Tuple[str], TimeSeriesDataFrame], TimeSeriesDataFrame]',
                              data_frame: TimeSeriesDataFrame) -> TimeSeriesDataFrame:
        """
        Apply function func to all grains of the data_frame and concatenate their output to another TSDF.

        :param data_frame: The initial data frame.
        :type data_frame: TimeSeriesDataFrame
        :param func: the function, returning TimeSeriesDataFrame and taking grain tuple and
                     TimeSeriesDataFrame as a parameters.
        :type func: function
        :param data_frame: target time series data frame.
        :type data_frame: TimeSeriesDataFrame
        :returns: The modified data frame.
        :rtype: TimeSeriesDataFrame

        """
        result = []
        for grain, X in data_frame.groupby_grain():
            result.append(func(grain, X))
        result_df = pd.concat(result)
        result_df.sort_index(inplace=True)
        return cast(TimeSeriesDataFrame, result_df)
