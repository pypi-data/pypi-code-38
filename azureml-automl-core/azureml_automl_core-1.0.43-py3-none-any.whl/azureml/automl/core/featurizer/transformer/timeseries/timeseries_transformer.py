# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Class for timeseries preprocessing."""
from typing import Any, cast, DefaultDict, Dict, List, Optional, Type, Union
import copy
import inspect
import json
import logging
import warnings

from collections import defaultdict
from sklearn.base import TransformerMixin
import numpy as np
import pandas as pd

from automl.client.core.common import memory_utilities
from automl.client.core.common.constants import TimeSeriesInternal, TimeSeries
from automl.client.core.common.time_series_data_frame import TimeSeriesDataFrame
from automl.client.core.common.forecasting_ts_utils import detect_seasonality_tsdf
from automl.client.core.common.types import DataInputType, DataSingleColumnInputType, FeaturizationSummaryType
from automl.client.core.common.exceptions import ConfigException
from .category_binarizer import CategoryBinarizer
from .rolling_window import RollingWindow
from .lag_lead_operator import LagLeadOperator
from .missingdummies_transformer import MissingDummiesTransformer
from .abstract_timeseries_transformer import AbstractTimeSeriesTransformer
from .forecasting_base_estimator import AzureMLForecastTransformerBase
from .forecasting_pipeline import AzureMLForecastPipeline
from .stl_featurizer import STLFeaturizer
from ..automltransformer import AutoMLTransformer
from ...._engineered_feature_names import \
    _FeatureTransformersAsJSONObject, _TransformationFunctionNames, _OperatorNames, \
    FeatureTypeRecognizer, _Transformer, _FeatureTransformers, _RawFeatureFeaturizationInfo


# Prevent warnings when using Jupyter
warnings.simplefilter("ignore")
pd.options.mode.chained_assignment = None


class TimeSeriesTransformer(AbstractTimeSeriesTransformer):
    """Class for timeseries preprocess."""

    REMOVE_LAG_LEAD_WARN = "The lag-lead operator was removed due to memory limitation."
    REMOVE_ROLLING_WINDOW_WARN = "The rolling window operator was removed due to memory limitation."

    def __init__(self, logger: Optional[logging.Logger] = None, **kwargs: Any) -> None:
        """
        Construct for the class.

        :param logger: The logger to be used in the pipeline.
        :param kwargs: dictionary contains metadata for TimeSeries.
                       time_column_name: The column containing dates.
                       grain_column_names: The set of columns defining the
                       multiple time series.
                       origin_column_name: latest date from which actual values
                       of all features are assumed to be known with certainty.
                       drop_column_names: The columns which will needs
                       to be removed from the data set.
                       group: the group column name.
        :type kwargs: dict
        """
        self._transforms = {}   # type: Dict[str, TransformerMixin]
        if TimeSeriesInternal.LAGS_TO_CONSTRUCT in kwargs.keys():
            # We need to backfill the cache to avoid problems with shape.
            kwargs['backfill_cache'] = True
            self._get_transformer_params(LagLeadOperator,
                                         TimeSeriesInternal.LAG_LEAD_OPERATOR,
                                         **kwargs)
        if TimeSeriesInternal.WINDOW_SIZE in kwargs.keys() and TimeSeriesInternal.TRANSFORM_DICT in kwargs.keys():
            # We need to disable the horizon detection, because it is very slow on large data sets.
            kwargs['check_max_horizon'] = False
            # We need to backfill the cache to avoid problems with shape.
            kwargs['backfill_cache'] = True
            self._get_transformer_params(RollingWindow,
                                         TimeSeriesInternal.ROLLING_WINDOW_OPERATOR,
                                         **kwargs)
        self._max_horizon = cast(int, kwargs.get(TimeSeries.MAX_HORIZON, TimeSeriesInternal.MAX_HORIZON_DEFAULT))
        self.use_stl = kwargs.get(TimeSeries.USE_STL,
                                  TimeSeriesInternal.USE_STL_DEFAULT)
        if self.use_stl is not None and self.use_stl not in TimeSeriesInternal.STL_VALID_OPTIONS:
            raise ConfigException('{} setting must be None or one of the following: {}'.format(
                TimeSeries.USE_STL, TimeSeriesInternal.STL_VALID_OPTIONS))
        self.seasonality = kwargs.get(TimeSeries.SEASONALITY,
                                      TimeSeriesInternal.SEASONALITY_VALUE_DEFAULT)
        self.force_time_index_features = kwargs.get(TimeSeriesInternal.FORCE_TIME_INDEX_FEATURES_NAME,
                                                    TimeSeriesInternal.FORCE_TIME_INDEX_FEATURES_DEFAULT)
        self.time_index_non_holiday_features = []  # type: List[str]
        super(TimeSeriesTransformer, self).__init__(logger, **kwargs)

    def _get_transformer_params(self,
                                cls: 'Type[AzureMLForecastTransformerBase]',
                                name: str,
                                **kwargs: Any) -> None:
        """
        Create the transformer if type cls and put it to the self._transforms with label name.

        :param cls: the class of transformer to be constructed.
        :type cls: type
        :param name: Transformer label.
        :type name: str
        :param kwargs: the dictionary of parameters to be parsed.
        :type kwargs: dict

        """
        rw = {}
        valid_args = inspect.getfullargspec(cls.__init__).args
        for k, v in kwargs.items():
            if k in valid_args:
                rw[k] = v

        self._transforms[name] = cls(**rw)

    def _construct_pre_processing_pipeline(self,
                                           tsdf: TimeSeriesDataFrame,
                                           drop_column_names: List[str]) -> AzureMLForecastPipeline:
        """Return the featurization pipeline."""
        from .forecasting_pipeline import AzureMLForecastPipeline
        from .grain_index_featurizer import GrainIndexFeaturizer
        from .time_series_imputer import TimeSeriesImputer
        from .time_index_featurizer import TimeIndexFeaturizer

        numerical_columns = [x for x in tsdf.select_dtypes(include=[np.number]).columns
                             if x not in drop_column_names]
        if self.target_column_name in numerical_columns:
            numerical_columns.remove(self.target_column_name)
        if self.original_order_column in numerical_columns:
            numerical_columns.remove(self.original_order_column)

        imputation_dict = {col: tsdf[col].median() for col in numerical_columns}
        impute_missing_numerical_values = TimeSeriesImputer(
            input_column=numerical_columns, value=imputation_dict, freq=self.freq, logger=self.logger)

        datetime_columns = [x for x in tsdf.select_dtypes(include=[np.datetime64]).columns
                            if x not in drop_column_names]
        fillna_imputer_ffill = TimeSeriesImputer(option='fillna', method='ffill',
                                                 input_column=datetime_columns,
                                                 freq=self.freq, logger=self.logger)
        fillna_imputer_bfill = TimeSeriesImputer(option='fillna', method='bfill',
                                                 input_column=datetime_columns,
                                                 freq=self.freq, logger=self.logger)
        # In forecasting destination date function, neither forward or backward will work
        # have to save the last non null value to impute
        # TODO: make both numeric and this imputation grain aware
        datetime_imputation_dict = {col: tsdf.loc[tsdf[col].last_valid_index()][col]
                                    for col in datetime_columns}
        datetime_imputer_final = TimeSeriesImputer(option='fillna',
                                                   input_column=datetime_columns,
                                                   value=datetime_imputation_dict,
                                                   freq=self.freq)

        # pipeline:
        # TODO: unify the imputers to support all data types
        default_pipeline = AzureMLForecastPipeline([
            (TimeSeriesInternal.MAKE_NUMERIC_NA_DUMMIES, MissingDummiesTransformer(numerical_columns)),
            (TimeSeriesInternal.IMPUTE_NA_NUMERIC_COLUMNS, impute_missing_numerical_values),
            (TimeSeriesInternal.IMPUTE_NA_FORWARD, fillna_imputer_ffill),
            (TimeSeriesInternal.IMPUTE_NA_BACKWARD, fillna_imputer_bfill),
            (TimeSeriesInternal.IMPUTE_NA_FINAL, datetime_imputer_final),
        ])
        # We introduce the STL transform, only if we need it after the imputation,
        # but before the lag lead operator and rolling window because STL does not support
        # origin time index.
        if self.use_stl is not None:
            only_season_feature = self.use_stl == TimeSeries.STL_OPTION_SEASON
            default_pipeline.add_pipeline_step(
                TimeSeriesInternal.MAKE_SEASONALITY_AND_TREND,
                STLFeaturizer(seasonal_feature_only=only_season_feature, seasonality=self.seasonality))

        # Lag and rolling window transformer
        # To get the determined behavior sort the self._transforms.
        transforms_ordered = sorted(self._transforms.keys())
        for transform in transforms_ordered:
            # Add the transformer to the default pipeline
            default_pipeline.add_pipeline_step(transform, self._transforms[transform])

        # Don't apply grain featurizer when there is single time series
        if self.dummy_grain_column not in self.grain_column_names:
            grain_index_featurizer = GrainIndexFeaturizer(overwrite_columns=True, logger=self.logger)
            default_pipeline.add_pipeline_step(TimeSeriesInternal.MAKE_GRAIN_FEATURES, grain_index_featurizer)

        # Add step to preprocess datetime
        time_index_featurizer = TimeIndexFeaturizer(overwrite_columns=True, country_or_region=self.country_or_region,
                                                    freq=self.freq, datetime_columns=datetime_columns,
                                                    logger=self.logger,
                                                    force_feature_list=self.force_time_index_features)
        self.time_index_non_holiday_features = time_index_featurizer.preview_non_holiday_feature_names(tsdf)
        default_pipeline.add_pipeline_step(TimeSeriesInternal.MAKE_TIME_INDEX_FEATURES, time_index_featurizer)

        # Add step to preprocess categorical data
        default_pipeline.add_pipeline_step(TimeSeriesInternal.MAKE_CATEGORICALS_ONEHOT,
                                           CategoryBinarizer(logger=self.logger))

        return default_pipeline

    def _create_feature_transformer_graph(self,
                                          graph: Dict[str, List[List[Union[str, TransformerMixin]]]],
                                          feature_from: str,
                                          feature_to: str,
                                          transformer: AutoMLTransformer) -> None:
        """
        Add the each feature's transform procedure into the graph.

        :param graph: a dictionary contains feature's transformer path
        :type graph: dict
        :param feature_from: feature name before transform
        :type feature_from: str
        :param feature_to: feature name after transform
        :type feature_to: str
        :param transformer: the name of transformer processed the feature
        :type transformer: str
        """
        if feature_to in graph:
            graph[feature_to].append([feature_from, transformer])
        else:
            if feature_from in graph:
                # Deep copy the feature's pre transformers
                graph[feature_to] = copy.deepcopy(graph[feature_from])
                graph[feature_to].append([feature_from, transformer])
            else:
                graph[feature_to] = [[feature_from, transformer]]

    def _generate_json_for_engineered_features(self, tsdf: TimeSeriesDataFrame) -> None:
        """
        Create the transformer json format for each engineered feature.

        :param tsdf: time series data frame
        """
        # Create the feature transformer graph from pipeline's steps
        # The dict contains key-> list, list includes a series of transformers
        graph = defaultdict(list)   # type: DefaultDict[str, List[List[Union[str, TransformerMixin]]]]
        for name, transformer in self.pipeline._steps:
            if name == TimeSeriesInternal.MAKE_NUMERIC_NA_DUMMIES:
                for col in transformer.numerical_columns:
                    self._create_feature_transformer_graph(graph, col, col + '_WASNULL', name)
            elif name == TimeSeriesInternal.IMPUTE_NA_NUMERIC_COLUMNS:
                for col in transformer.input_column:
                    self._create_feature_transformer_graph(graph, col, col, name)
            elif name == TimeSeriesInternal.MAKE_TIME_INDEX_FEATURES:
                for col in transformer.preview_time_feature_names(tsdf):
                    self._create_feature_transformer_graph(graph, tsdf.time_colname, col, name)
                for date_col in transformer.datetime_columns:
                    for dst in transformer._datetime_sub_feature_names:
                        self._create_feature_transformer_graph(graph, date_col, date_col + "_" + dst, name)
            elif name == TimeSeriesInternal.MAKE_GRAIN_FEATURES:
                for col in tsdf.grain_colnames:
                    self._create_feature_transformer_graph(graph, col, 'grain_' + col, name)
            elif name == TimeSeriesInternal.MAKE_CATEGORICALS_NUMERIC:
                for col in transformer._categories_by_col.keys():
                    self._create_feature_transformer_graph(graph, col, col, name)
            elif name == TimeSeriesInternal.MAKE_CATEGORICALS_ONEHOT:
                for col in transformer._categories_by_col.keys():
                    for dst in transformer._categories_by_col[col]:
                        self._create_feature_transformer_graph(graph, col, str(col) + '_' + str(dst), name)
            elif name in [TimeSeriesInternal.LAG_LEAD_OPERATOR,
                          TimeSeriesInternal.ROLLING_WINDOW_OPERATOR]:
                for col in transformer.preview_column_names(tsdf):
                    if name == TimeSeriesInternal.LAG_LEAD_OPERATOR:
                        features = transformer.lags_to_construct.keys()
                    else:
                        features = transformer.transform_dict.values()
                    raw_feature = tsdf.ts_value_colname
                    for feature in features:
                        if col.startswith(feature):
                            raw_feature = feature
                    self._create_feature_transformer_graph(graph, raw_feature, col, name)
            elif name == TimeSeriesInternal.MAKE_SEASONALITY_AND_TREND:
                raw_feature = tsdf.ts_value_colname
                for col in transformer.preview_column_names(tsdf):
                    self._create_feature_transformer_graph(graph, raw_feature, col, name)

        if self.engineered_feature_names is None:
            # This can happen only if user invoked _generate_json_for_engineered_features
            # outside the transform function without setting engineered_feature_names.
            raise Exception("No feature were generated to build json.")

        for engineered_feature_name in self.engineered_feature_names or []:
            col_transformers = graph.get(engineered_feature_name, [])
            transformers = []   # type: List[_Transformer]
            val = ''
            for col, transformer in col_transformers:
                input_feature = col
                # for each engineered feature's transform path, only store the first transformer's
                # input which is raw feature name, other transformers' input are previous transformer
                if len(transformers) > 0:
                    input_feature = len(transformers)
                if transformer == TimeSeriesInternal.MAKE_NUMERIC_NA_DUMMIES:
                    transformers.append(
                        _Transformer(
                            parent_feature_list=[input_feature],
                            transformation_fnc=_TransformationFunctionNames.ImputationMarker,
                            operator=None,
                            feature_type=FeatureTypeRecognizer.Numeric,
                            should_output=True)
                    )
                elif transformer == TimeSeriesInternal.IMPUTE_NA_NUMERIC_COLUMNS:
                    transformers.append(
                        _Transformer(
                            parent_feature_list=[input_feature],
                            transformation_fnc=_TransformationFunctionNames.Imputer,
                            operator=_OperatorNames.Mean,
                            feature_type=FeatureTypeRecognizer.Numeric,
                            should_output=True)
                    )
                elif transformer == TimeSeriesInternal.MAKE_TIME_INDEX_FEATURES:
                    transformers.append(
                        _Transformer(
                            parent_feature_list=[input_feature],
                            transformation_fnc=_TransformationFunctionNames.DateTime,
                            operator=None,
                            feature_type=FeatureTypeRecognizer.DateTime,
                            should_output=True)
                    )
                    val = engineered_feature_name
                elif transformer == TimeSeriesInternal.MAKE_GRAIN_FEATURES:
                    transformers.append(
                        _Transformer(
                            parent_feature_list=[input_feature],
                            transformation_fnc=_TransformationFunctionNames.GrainMarker,
                            operator=None,
                            feature_type=FeatureTypeRecognizer.Ignore,
                            should_output=True)
                    )
                elif transformer == TimeSeriesInternal.MAKE_CATEGORICALS_NUMERIC:
                    transformers.append(
                        _Transformer(
                            parent_feature_list=[input_feature],
                            transformation_fnc=_TransformationFunctionNames.LabelEncoder,
                            operator=None,
                            feature_type=FeatureTypeRecognizer.Categorical,
                            should_output=True)
                    )
                elif transformer == TimeSeriesInternal.MAKE_CATEGORICALS_ONEHOT:
                    val = engineered_feature_name
                    transformers.append(
                        _Transformer(
                            parent_feature_list=[input_feature],
                            transformation_fnc=_TransformationFunctionNames.OneHotEncoder,
                            operator=None,
                            feature_type=FeatureTypeRecognizer.Categorical,
                            should_output=True)
                    )
                elif transformer == TimeSeriesInternal.LAG_LEAD_OPERATOR:
                    # engineered_feature_name of lag operation is %target_col_name%_lags%size%%period"
                    # put the %size%%period% to val
                    val = engineered_feature_name[(len(col) + 4):]
                    transformers.append(
                        _Transformer(
                            parent_feature_list=[input_feature],
                            transformation_fnc=_TransformationFunctionNames.Lag,
                            operator=None,
                            feature_type=FeatureTypeRecognizer.Numeric,
                            should_output=True)
                    )
                elif transformer == TimeSeriesInternal.ROLLING_WINDOW_OPERATOR:
                    # engineered_feature_name of rollingwindow operation is %target_col_name%_func%size%%period"
                    # put the %size%%period% to val
                    func_value = engineered_feature_name[len(col) + 1:].split("_", 2)
                    func = func_value[0]
                    val = func_value[1]
                    transformers.append(
                        _Transformer(
                            parent_feature_list=[input_feature],
                            transformation_fnc=_TransformationFunctionNames.RollingWindow,
                            operator=func,
                            feature_type=FeatureTypeRecognizer.Numeric,
                            should_output=True)
                    )
                elif transformer == TimeSeriesInternal.MAKE_SEASONALITY_AND_TREND:
                    # engineered_feature_name of STL operation is %target_col_name%_seasonal"
                    transformers.append(
                        _Transformer(
                            parent_feature_list=[input_feature],
                            transformation_fnc=_TransformationFunctionNames.STLFeaturizer,
                            operator=None,
                            feature_type=FeatureTypeRecognizer.Numeric,
                            should_output=True)
                    )

            feature_transformers = _FeatureTransformers(transformers)
            # Create the JSON object
            transformation_json = feature_transformers.encode_transformations_from_list()
            transformation_json._set_value_tag(val)
            self._engineered_feature_name_objects[engineered_feature_name] = transformation_json

    def _get_json_str_for_engineered_feature_name(self,
                                                  engineered_feature_name: str) -> str:
        """
        Return JSON string for engineered feature name.

        :param engineered_feature_name: Engineered feature name for
            whom JSON string is required
        :return: JSON string for engineered feature name
        """
        # If the JSON object is not valid, then return None
        if engineered_feature_name not in self._engineered_feature_name_objects:
            return json.dumps([])
        else:
            engineered_feature_name_json_obj = \
                cast(_FeatureTransformersAsJSONObject,
                     self._engineered_feature_name_objects[engineered_feature_name])._entire_transformation_json_data
            # Convert JSON into string and return
            return json.dumps(engineered_feature_name_json_obj)

    def get_json_strs_for_engineered_feature_names(self,
                                                   engi_feature_name_list: Optional[List[str]] = None) -> List[str]:
        """
        Return JSON string list for engineered feature names.

        :param engi_feature_name_list: Engineered feature names for
            whom JSON strings are required
        :return: JSON string list for engineered feature names
        """
        engineered_feature_names_json_str_list = []

        if engi_feature_name_list is None:
            engi_feature_name_list = self.get_engineered_feature_names()

        # Walk engineering feature name list and get the corresponding
        # JSON string
        for engineered_feature_name in cast(List[str], engi_feature_name_list):

            json_str = \
                self._get_json_str_for_engineered_feature_name(
                    engineered_feature_name)

            engineered_feature_names_json_str_list.append(json_str)

        # Return the list of JSON strings for engineered feature names
        return engineered_feature_names_json_str_list

    def get_featurization_summary(self) -> FeaturizationSummaryType:
        """
        Return the featurization summary for all the input features seen by TimeSeriesTransformer.

        :return: List of featurization summary for each input feature.
        """
        return _RawFeatureFeaturizationInfo.get_coalesced_raw_feature_featurization_mapping(
            self._engineered_feature_name_objects)

    def fit(self, X: pd.DataFrame, y: Optional[np.ndarray] = None) -> 'TimeSeriesTransformer':
        """
        Perform the raw data validation and identify the transformations to apply.

        :param X: Dataframe representing text, numerical or categorical input.
        :type X: pandas.DataFrame
        :param y: To match fit signature.
        :type y: numpy.ndarray

        :return: DataTransform object.
        :raises: Value Error for non-dataframe and empty dataframes.
        """
        # Override the parent class fit method to define if there is enough memory
        # for using LagLeadOperator and RollingWindow.
        self._remove_lag_lead_and_rw_maybe(X, y)
        super(TimeSeriesTransformer, self).fit(X, y)
        return self

    def transform(self,
                  df: DataInputType,
                  y: Optional[DataSingleColumnInputType] = None) -> pd.DataFrame:
        """
        Transform the input raw data with the transformations identified in fit stage.

        :param df: Dataframe representing text, numerical or categorical input.
        :type df: pandas.DataFrame
        :param y: To match fit signature.
        :type y: numpy.ndarray

        :return: pandas.DataFrame

        """
        df = super(TimeSeriesTransformer, self).transform(df, y)
        # if we have applied STL transform, we need to make sure that leading np.NaNs are removed
        # from the trend.
        stl = self.pipeline.get_pipeline_step(TimeSeriesInternal.MAKE_SEASONALITY_AND_TREND)
        if stl:
            cols = stl.preview_column_names(target=self.target_column_name)
            for col in cols:
                if col.endswith(TimeSeriesInternal.STL_TREND_SUFFIX):
                    df = df[df[col].notnull()]

        # remove the possible nans that brought by lags
        check_columns = [col for col in df.columns.values if col != self.target_column_name]
        df.dropna(axis=0, inplace=True, subset=check_columns)
        return df

    def _remove_lag_lead_and_rw_maybe(self, df: pd.DataFrame, y: np.ndarray) -> None:
        """
        Remove the LagLead and or RollingWindow operator from the pipeline if there is not enough memory.

        :param df: DataFrame representing text, numerical or categorical input.
        :type df: pandas.DataFrame
        :param y: To match fit signature.
        :type y: numpy.ndarray

        """
        memory_per_df = memory_utilities.get_data_memory_size(df)
        if y is not None:
            memory_per_df += memory_utilities.get_data_memory_size(y)
        remove_ll_rw = True
        try:
            total_memory = memory_utilities.get_all_ram(self.logger)
            remove_ll_rw = TimeSeriesInternal.MEMORY_FRACTION_FOR_DF < self._max_horizon * memory_per_df / total_memory
        except Exception as e:
            if self.logger is not None:
                self.logger.warning(repr(e))
        if remove_ll_rw:
            self._remove_step_maybe(TimeSeriesInternal.LAG_LEAD_OPERATOR,
                                    TimeSeriesTransformer.REMOVE_LAG_LEAD_WARN)
            self._remove_step_maybe(TimeSeriesInternal.ROLLING_WINDOW_OPERATOR,
                                    TimeSeriesTransformer.REMOVE_ROLLING_WINDOW_WARN)

    def _remove_step_maybe(self, step_name: str, warning_text: str) -> None:
        """
        Safely remove the pipeline step.

        :param step_name: The name of a pipeline step.
        :type step_name: str
        :param warning_text: The warning text to be shown to user.
                             If None, no warning will be shown.
        :type warning_text: str

        """
        if step_name in self._transforms.keys():
            del self._transforms[step_name]
            if warning_text is not None:
                print(warning_text)

    @property
    def max_horizon(self) -> int:
        """Return the max horizon."""
        return self._max_horizon
