# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""abstract_timeseries_transformer.py, a file for storing abstract class for transformers operating on time series."""
from typing import Any, cast, Dict, List, Optional, Union
import abc
import logging
import warnings

import numpy as np
import pandas as pd

from automl.client.core.common import constants
from automl.client.core.common import forecasting_utils
from automl.client.core.common.exceptions import DataException
from automl.client.core.common.logging_utilities import function_debug_log_wrapped
from automl.client.core.common.time_series_data_frame import TimeSeriesDataFrame
from automl.client.core.common.types import DataInputType, DataSingleColumnInputType
from ..automltransformer import AutoMLTransformer
from .time_series_imputer import TimeSeriesImputer
from .forecasting_pipeline import AzureMLForecastPipeline

warnings.simplefilter("ignore")


class AbstractTimeSeriesTransformer(AutoMLTransformer):
    """The abstract class, encapsulating common steps in data pre processing."""

    def __init__(self, logger: Optional[logging.Logger] = None, **kwargs: Any) -> None:
        """
        Construct for the class.

        :param logger: Logger to be injected to usage in this class.
        :type: azureml.automl.core.featurization.AutoMLTransformer
        :param kwargs: dictionary contains metadata for TimeSeries.
                   time_column_name: The column containing dates.
                   grain_column_names: The set of columns defining the
                   multiple time series.
                   origin_column_name: latest date from which actual values
                   of all features are assumed to be known with certainty.
                   drop_column_names: The columns which will needs
                   to be removed from the data set.
                   group: the group column name.
                   country_or_region: the data origin coutry used to generate holiday feature
        :type kwargs: dict
        """
        super().__init__()
        if constants.TimeSeries.TIME_COLUMN_NAME not in kwargs.keys():
            raise KeyError("{} must be set".format(constants.TimeSeries.TIME_COLUMN_NAME))
        self.time_column_name = cast(str, kwargs[constants.TimeSeries.TIME_COLUMN_NAME])
        grains = kwargs.get(constants.TimeSeries.GRAIN_COLUMN_NAMES)
        if isinstance(grains, str):
            grains = [grains]
        self.grain_column_names = cast(List[str], grains)
        self.drop_column_names = cast(List[str], kwargs.get(constants.TimeSeries.DROP_COLUMN_NAMES))

        self._init_logger(logger)
        # Used to make data compatible with timeseries dataframe
        self.target_column_name = constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN
        self.origin_column_name = \
            kwargs.get(constants.TimeSeriesInternal.ORIGIN_TIME_COLUMN_NAME, None)
        self.dummy_grain_column = constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN
        self.group_column = kwargs.get(constants.TimeSeries.GROUP_COLUMN, None)

        self.original_order_column = constants.TimeSeriesInternal.DUMMY_ORDER_COLUMN
        self.engineered_feature_names = None                       # type: Optional[List[str]]
        self._fit_column_order = np.array([])
        self._fit_column_order_no_ts_value = np.array([])
        self._engineered_feature_name_objects = {}             # type: Dict[str, Optional[Any]]
        # We keep the list of columns in case if the class is invoked without data frame.
        self._columns = None
        # For the same purpose we need to store the imputer for y values.
        self._y_imputers = {}  # type: Dict[str, TimeSeriesImputer]
        self.dict_latest_date = {}   # type: Dict[str, pd.Timestamp]
        self.country_or_region = kwargs.get(constants.TimeSeries.COUNTRY_OR_REGION, None)

    def _do_construct_pre_processing_pipeline(self,
                                              tsdf: TimeSeriesDataFrame,
                                              drop_column_names: List[str]) -> AzureMLForecastPipeline:
        from .drop_columns import DropColumns
        self._logger_wrapper('info', 'Start construct pre-processing pipeline ({}).'.format(self.__class__.__name__))
        processing_pipeline = self._construct_pre_processing_pipeline(tsdf, drop_column_names)
        # Don't add dropColumn transfomer if there is nothing to drop
        if len(drop_column_names) > 0:
            processing_pipeline.add_pipeline_step('drop_irrelevant_columns',
                                                  DropColumns(drop_column_names, self.logger),
                                                  prepend=True)
        self._logger_wrapper('info', 'Finish Construct Pre-Processing Pipeline ({}).'.format(self.__class__.__name__))
        return processing_pipeline

    @abc.abstractmethod
    def _construct_pre_processing_pipeline(self,
                                           tsdf: TimeSeriesDataFrame,
                                           drop_column_names: List[str]) -> AzureMLForecastPipeline:
        """
        Construct the pre processing pipeline and stores it in self.pipeline.

        :param tsdf: The time series data frame.
        :type tsdf: TimeSeriesDataFrame
        :param drop_column_names: The columns to be dropped.
        :type drop_column_names: list

        """
        pass

    def _impute_target_value(self, tsdf: TimeSeriesDataFrame) -> TimeSeriesDataFrame:
        """Perform the y imputation based on frequency."""
        from .time_series_imputer import TimeSeriesImputer
        target_imputer = TimeSeriesImputer(input_column=tsdf.ts_value_colname,
                                           option='fillna', method='ffill',
                                           freq=self.freq, logger=self.logger)
        return cast(TimeSeriesDataFrame, target_imputer.fit_transform(tsdf))

    @function_debug_log_wrapped
    def fit_transform(self,
                      X: DataInputType,
                      y: Optional[DataSingleColumnInputType] = None, **fit_params: Any) -> pd.DataFrame:
        """
        Wrap fit and transform functions in the Data transformer class.

        :param X: Dataframe representing text, numerical or categorical input.
        :type X: numpy.ndarray or pandas.DataFrame
        :param y: To match fit signature.
        :type y: numpy.ndarray or pandas.DataFrame

        :return: Transformed data.

        """
        self.fit(X, y)
        return self.transform(X, y)

    def construct_tsdf(self,
                       X: DataInputType,
                       y: Optional[DataSingleColumnInputType] = None) -> TimeSeriesDataFrame:
        """Contruct timeseries dataframe."""
        self._columns = X.columns
        if self.grain_column_names is None or len(self.grain_column_names) == 0:
            X[self.dummy_grain_column] = self.dummy_grain_column
            self.grain_column_names = [self.dummy_grain_column]
        # Ensure that grain_column_names is always list.
        if isinstance(self.grain_column_names, str):
            self.grain_column_names = [self.grain_column_names]
        X[self.target_column_name] = y

        # TODO: Currently we are not checking if y values contain NaNs.
        # This is a potential source of bugs. In future we will need to infer the NaNs
        # or drop the columns with NaNs or throw the error.
        try:
            tsdf = self._create_tsdf_from_data(X,
                                               time_column_name=self.time_column_name,
                                               target_column_name=self.target_column_name,
                                               grain_column_names=self.grain_column_names)
        except Exception:
            raise DataException("Exception when creating timeseries dataframe.")
        return tsdf

    @function_debug_log_wrapped
    def fit(self,
            X: DataInputType,
            y: Optional[DataSingleColumnInputType] = None) -> 'AbstractTimeSeriesTransformer':
        """
        Perform the raw data validation and identify the transformations to apply.

        :param X: Dataframe representing text, numerical or categorical input.
        :param y: To match fit signature.

        :return: DataTransform object.
        :raises: ValueError for non-dataframe and empty dataframes.
        """
        tsdf = self.construct_tsdf(X, y)
        all_drop_column_names = [x for x in tsdf.columns if
                                 np.sum(tsdf[x].notnull()) == 0]
        if isinstance(self.drop_column_names, str):
            all_drop_column_names.extend([self.drop_column_names])
        elif self.drop_column_names is not None:
            all_drop_column_names.extend(self.drop_column_names)
        self.drop_column_names = all_drop_column_names
        self.freq = tsdf.infer_freq(True)
        # Create the imputer for y values.
        self._y_imputers = {}
        dfs = []
        for grain, df_one in tsdf.groupby_grain():
            # Save the latest dates for the training set.
            # Create the dictionary on the already created groupby object.
            # For the purposes of fit we need to remove all NaN suffix.
            df_one = df_one[:np.max(np.where(pd.notna(df_one.ts_value))) + 1]
            self.dict_latest_date[grain] = max(df_one.time_index)
            self._y_imputers[grain] = TimeSeriesImputer(
                input_column=[self.target_column_name],
                value={self.target_column_name: df_one[self.target_column_name].median()},
                freq=self.freq, logger=self.logger)
            dfs.append(df_one)
        tsdf = pd.concat(dfs)
        # clean up memory.
        del dfs
        self.pipeline = self._do_construct_pre_processing_pipeline(tsdf, self.drop_column_names)
        transformed_train_df = self.pipeline.fit_transform(tsdf, y)
        self._fit_column_order = transformed_train_df.columns.values
        # We may want to keep the column order without target value,
        # because during prediction this column will not be present and will be
        # only transiently created in LagLeadOperator and in RollingWindow.
        transformed_train_df.drop(transformed_train_df.ts_value_colname, inplace=True, axis=1)
        self._fit_column_order_no_ts_value = transformed_train_df.columns.values
        return self

    @function_debug_log_wrapped
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
        if not self.pipeline:
            raise Exception("fit not called")

        if self.dummy_grain_column in self.grain_column_names:
            df[self.dummy_grain_column] = self.dummy_grain_column

        transformed_data = None
        if y is not None:
            # transform training data
            df[self.target_column_name] = y
            tsdf = self._create_tsdf_from_data(df,
                                               time_column_name=self.time_column_name,
                                               target_column_name=self.target_column_name,
                                               grain_column_names=self.grain_column_names)
            tsdf = self._impute_target_value(tsdf)
            transformed_data = self.pipeline.transform(tsdf)
        else:
            # Dealing with X_test, save the row sequence number then use it to restore the order
            # Drop existing index if there is any
            df.reset_index(inplace=True, drop=True)

            df[self.original_order_column] = df.index
            tsdf = self._create_tsdf_from_data(df,
                                               time_column_name=self.time_column_name,
                                               target_column_name=None,
                                               grain_column_names=self.grain_column_names)
            scoring_freq = tsdf.infer_freq()
            if self.freq is not None and scoring_freq is not None and self.freq != scoring_freq:
                raise DataException(
                    "Scoring data frequency is not consistent with training data.")
            # preserve the index because the input X_test may not be continuous
            transformed_data = self.pipeline.transform(tsdf)
            # We are doing inner join, which will remove the imputed rows and preserve the rows order
            # in the output data frame.
            transformed_data = transformed_data[transformed_data[self.original_order_column].notnull()]
            transformed_data.sort_values(by=[self.original_order_column], inplace=True)
            transformed_data.pop(self.original_order_column)

        # make horizon a feature if available
        if transformed_data.origin_time_index is not None:
            horizon_feature = \
                forecasting_utils.get_period_offsets_from_dates(transformed_data.origin_time_index,
                                                                transformed_data.time_index,
                                                                self.freq)
            transformed_data.insert(
                loc=len(transformed_data.columns),
                column=constants.TimeSeriesInternal.HORIZON_NAME,
                value=horizon_feature)
            # ensure horizon column is kept
            if constants.TimeSeriesInternal.HORIZON_NAME not in self._fit_column_order:
                self._fit_column_order = np.append(
                    self._fit_column_order,
                    constants.TimeSeriesInternal.HORIZON_NAME)
            if constants.TimeSeriesInternal.HORIZON_NAME not in self._fit_column_order_no_ts_value:
                self._fit_column_order_no_ts_value = np.append(
                    self._fit_column_order_no_ts_value,
                    constants.TimeSeriesInternal.HORIZON_NAME)
        if self.engineered_feature_names is None:
            self.engineered_feature_names = transformed_data.columns.values.tolist()
            if self.target_column_name in self.engineered_feature_names:
                self.engineered_feature_names.remove(self.target_column_name)
            # Generate the json objects for engineered features
            self._generate_json_for_engineered_features(tsdf)
        # Make sure that the order of columns is the same as in training set.
        transformed_data = pd.DataFrame(transformed_data)
        if y is not None or self.target_column_name in transformed_data.columns:
            transformed_data = transformed_data[self._fit_column_order]
        else:
            transformed_data = transformed_data[self._fit_column_order_no_ts_value]
        return transformed_data

    @abc.abstractmethod
    def _generate_json_for_engineered_features(self, tsdf: pd.DataFrame) -> None:
        """
        Create the transformer json format for each engineered feature.

        :param tsdf: The time series data frame.
        """
        pass

    def get_engineered_feature_names(self) -> Optional[List[str]]:
        """
        Get the transformed column names.

        :return: list of strings
        """
        return self.engineered_feature_names

    def _create_tsdf_from_data(self,
                               data: pd.DataFrame,
                               time_column_name: str,
                               target_column_name: Optional[str] = None,
                               grain_column_names: Optional[Union[str, List[str]]] = None) -> TimeSeriesDataFrame:
        """
        Given the input data, construct the time series data frame.

        :param data: data used to train the model.
        :type data: pandas.DataFrame
        :param time_column_name: Column label identifying the time axis.
        :type time_column_name: str
        :param target_column_name: Column label identifying the target column.
        :type target_column_name: str
        :param grain_column_names:  Column labels identifying the grain columns.
                                Grain columns are the "group by" columns that identify data
                                belonging to the same grain in the real-world.

                                Here are some simple examples -
                                The following sales data contains two years
                                of annual sales data for two stores. In this example,
                                grain_colnames=['store'].

                                >>>          year  store  sales
                                ... 0  2016-01-01      1     56
                                ... 1  2017-01-01      1     98
                                ... 2  2016-01-01      2    104
                                ... 3  2017-01-01      2    140

        :type grain_column_names: str, list or array-like
        :return: TimeSeriesDataFrame

        """
        from automl.client.core.common.time_series_data_frame import TimeSeriesDataFrame
        data[time_column_name] = pd.to_datetime(data[time_column_name])
        # Drop the entire row if time index not exist
        data = data.dropna(subset=[time_column_name], axis=0).reset_index(drop=True)
        data = data.infer_objects()
        # Check if data has the designated origin column/index
        # If not, don't try to set it since this will trigger an exception in TSDF
        origin_present = self.origin_column_name is not None \
            and (self.origin_column_name in data.index.names or
                 self.origin_column_name in data.columns)
        origin_setting = self.origin_column_name if origin_present else None
        tsdf = TimeSeriesDataFrame(data, time_colname=time_column_name,
                                   ts_value_colname=target_column_name,
                                   origin_time_colname=origin_setting,
                                   grain_colnames=grain_column_names
                                   )
        return tsdf

    @property
    def columns(self) -> Optional[List[str]]:
        """
        Return the list of expected columns.

        :returns: The list of columns.
        :rtype: list

        """
        return self._columns

    @property
    def y_imputers(self) -> Dict[str, TimeSeriesImputer]:
        """
        Return the imputer for target column.

        :returns: imputer for target column.
        :rtype: dict

        """
        return self._y_imputers
