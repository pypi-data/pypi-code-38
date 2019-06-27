# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Preprocessing class that can be added in pipeline for input."""
from typing import cast, Dict, List, Optional, Tuple, Type, Any

import json
import logging
import math
import gc
import pickle
import os
import uuid

import numpy as np
import pandas as pd
from pandas.core.indexes.base import Index
from pandas.core.series import Series
from sklearn_pandas import DataFrameMapper
from sklearn.pipeline import Pipeline, make_pipeline
from scipy import sparse

from automl.client.core.common import constants, logging_utilities, memory_utilities, utilities
from automl.client.core.common.types import TransformerType, DataSingleColumnInputType
from automl.client.core.common.types import FeaturizationSummaryType, DataInputType
from automl.client.core.common.exceptions import DataException
from automl.client.core.common import pickler

from .._experiment_observer import ExperimentStatus, ExperimentObserver, NullExperimentObserver
from .._engineered_feature_names import _GenerateEngineeredFeatureNames, \
    FeatureTypeRecognizer, _Transformer, _TransformationFunctionNames, _FeatureTransformers, _OperatorNames
from ..column_purpose_detection.types import StatsAndColumnPurposeType
from ..column_purpose_detection.columnpurpose_detector import ColumnPurposeDetector
from ..column_purpose_detection.columnpurpose_sweeper import ColumnPurposeSweeper
from ..stats_computation import PreprocessingStatistics as _PreprocessingStatistics

from ..featurizer.transformer import AutoMLTransformer, CategoricalFeaturizers, DateTimeFeaturesTransformer,\
    GenericFeaturizers, get_ngram_len, TextFeaturizers
from .generic_transformer import GenericTransformer
from .text_transformer import TextTransformer
from .transformer_and_mapper import TransformerAndMapper
from ..featurizer.transformer import featurization_utilities


class DataTransformer(AutoMLTransformer):
    """
    Preprocessing class that can be added in pipeline for input.

    This class does the following:
    1. Numerical inputs treated as it is.
    2. For dates: year, month, day and hour are features
    3. For text, tfidf features
    4. Small number of unique values for a column that is not float become
        categoricals

    :param task: 'classification' or 'regression' depending on what kind of
    ML problem to solve.
    :param is_onnx_compatible: if works in onnx compatible mode.
    """

    DEFAULT_DATA_TRANSFORMER_TIMEOUT_SEC = 3600 * 24  # 24 hours

    def __init__(self,
                 task: Optional[str] = constants.Tasks.CLASSIFICATION,
                 is_onnx_compatible: bool = False,
                 logger: Optional[logging.Logger] = None,
                 observer: Optional[ExperimentObserver] = None,
                 enable_feature_sweeping: bool = False,
                 feature_sweeping_timeout: int = DEFAULT_DATA_TRANSFORMER_TIMEOUT_SEC) -> None:
        """
        Initialize for data transformer for pre-processing raw user data.

        :param task: 'classification' or 'regression' depending on what kind
        of ML problem to solve.
        :type task: str or azureml.train.automl.constants.Tasks
        :param is_onnx_compatible: if works in onnx compatible mode.
        :param logger: External logger handler.
        :type logger: logging.Logger
        """
        super().__init__()
        if task not in constants.Tasks.ALL:
            raise ValueError("Unknown task")

        self._task_type = task
        self._is_onnx_compatible = is_onnx_compatible
        self.mapper = None  # type: Optional[DataFrameMapper]
        self._init_logger(logger)  # External logger if None, then no logs
        # list of TrasformerAndMapper objects
        self.transformer_and_mapper_list = []  # type: List[TransformerAndMapper]
        # Maintain a list of raw feature names
        self._raw_feature_names = []  # type: List[str]
        # Maintain engineered feature name class
        self._engineered_feature_names_class = _GenerateEngineeredFeatureNames()
        # Maintain statistics about the pre-processing stage
        self._pre_processing_stats = _PreprocessingStatistics()
        # Text transformer
        self._text_transformer = None  # type: Optional[TextTransformer]
        # Stats and column purpose
        self.stats_and_column_purposes = None  # type: Optional[List[StatsAndColumnPurposeType]]
        # Generic transformer
        # TODO Need to enable this later
        self._generic_transformer = None  # type: Optional[GenericTransformer]
        self._observer = observer or NullExperimentObserver()  # type: ExperimentObserver
        self._enable_feature_sweeping = enable_feature_sweeping
        self._feature_sweeping_timeout = feature_sweeping_timeout
        self._logger_wrapper("info", "Feature sweeping enabled: {}".format(self._enable_feature_sweeping))
        self._logger_wrapper("info", "Feature sweeping timeout: {}".format(self._feature_sweeping_timeout))

        # Used for injecting test transformers.
        self._test_transforms = []  # type: List[Any]
        self._columns_types_mapping = None  # type: Optional[Dict[str, np.dtype]]

    @logging_utilities.function_debug_log_wrapped
    def _learn_transformations(self, df: DataInputType,
                               stats_and_column_purposes: List[StatsAndColumnPurposeType],
                               y: DataSingleColumnInputType = None) -> None:
        """
        Learn data transformation to be done on the raw data.

        :param df: Dataframe representing text, numerical or categorical input.
        :param stats_and_column_purposes: Statistics and column purposes of the given data.
        :param y: To match fit signature.
        """
        utilities.check_input(df)
        if isinstance(df, np.ndarray):
            df = pd.DataFrame(df)

        if self._engineered_feature_names_class is None:
            # Create class for engineered feature names
            self._engineered_feature_names_class = _GenerateEngineeredFeatureNames()

        # Column purpose determination and stats computation
        self._observer.report_status(
            ExperimentStatus.DatasetEvaluation, "Gathering dataset statistics.")

        transforms = self._get_transforms(df, stats_and_column_purposes, y)
        if self._is_onnx_compatible:
            self.mapper = DataFrameMapper(transforms, input_df=True, sparse=True)
        else:
            self.transformer_and_mapper_list = []
            for transformers in transforms:
                transform_and_mapper = TransformerAndMapper(transformers=transformers[1],
                                                            mapper=DataFrameMapper([transformers],
                                                                                   input_df=True, sparse=True))
                self.transformer_and_mapper_list.append(transform_and_mapper)

    def _add_test_transforms(self, transforms: List[Any]) -> None:
        self._test_transforms.extend(transforms)

    def fit_transform_with_logger(self, X, y=None, logger=None, **fit_params):
        """
        Wrap the fit_transform function for the Data transformer class.

        :param X: Dataframe representing text, numerical or categorical input.
        :type X:numpy.ndarray or pandas.DataFrame
        :param y: To match fit signature.
        :type y: numpy.ndarray or pandas.DataFrame
        :param fit_params: Additional parameters for fit_transform().
        :param logger: External logger handler.
        :type logger: logging.Logger
        :return: Transformed data.
        """
        # Init the logger
        self.logger = logger
        # Call the fit and transform function
        return self.fit_transform(X, y, **fit_params)

    @logging_utilities.function_debug_log_wrapped
    def fit(self, df: DataInputType, y: DataSingleColumnInputType = None) -> "DataTransformer":
        """
        Perform the raw data validation and identify the transformations to apply.

        :param df: Dataframe representing text, numerical or categorical input.
        :param y: To match fit signature.
        :return: DataTransform object.
        :raises: Value Error for non-dataframe and empty dataframes.
        """
        utilities.check_input(df)
        if isinstance(df, np.ndarray):
            df = pd.DataFrame(df)

        if self._columns_types_mapping is None:
            self._columns_types_mapping = self._get_pandas_columns_types_mapping(df)

        # checking two conditions due onnx compatibilty issues.
        if (self._is_onnx_compatible and not self.mapper) or (not self.transformer_and_mapper_list):
            self._logger_wrapper(
                'info', 'Featurizer mapper not found so learn all ' +
                        'the transforms')
            self.stats_and_column_purposes = ColumnPurposeDetector.get_raw_stats_and_column_purposes(
                df)
            self._learn_transformations(df, self.stats_and_column_purposes, y)

        if self._is_onnx_compatible and self.mapper is not None:
            self.mapper.fit(df, y)
        else:
            for transformer_mapper in self.transformer_and_mapper_list:
                transformer_mapper.mapper.fit(df, y)

                steps = transformer_mapper.transformers.steps \
                    if isinstance(transformer_mapper.transformers, Pipeline) else transformer_mapper.transformers

                transform_count = len(steps)
                if transform_count == 0:
                    continue
                # Only last transformer gets applied, all other are input to next transformer.
                last_transformer = steps[transform_count - 1]
                last_transformer = last_transformer[1] if isinstance(last_transformer, tuple) and len(
                    last_transformer) > 1 else last_transformer
                memory_estimate = (0 if not issubclass(type(last_transformer), AutoMLTransformer)
                                   else last_transformer.get_memory_footprint(df, y))
                transformer_mapper.memory_footprint_estimate = memory_estimate

        return self

    @logging_utilities.function_debug_log_wrapped
    def transform(self, df):
        """
        Transform the input raw data with the transformations idetified in fit stage.

        :param df: Dataframe representing text, numerical or categorical input.
        :type df: numpy.ndarray or pandas.DataFrame
        :return: Numpy array.
        """
        utilities.check_input(df)

        if isinstance(df, np.ndarray):
            df = pd.DataFrame(df)

        if self._columns_types_mapping is not None:
            df = self._check_columns_names_and_convert_types(df, self._columns_types_mapping)

        features = self._apply_transforms(df)
        any_sparse = any(sparse.issparse(fea) for fea in features)

        if self._engineered_feature_names_class is not None:
            if not self._engineered_feature_names_class.are_engineered_feature_names_available():
                # Generate engineered feature names if they are not already generated
                if self._is_onnx_compatible:
                    self._engineered_feature_names_class.parse_raw_feature_names(self.mapper.transformed_names_)
                else:
                    names = []  # type: List[str]
                    for tansformer_mapper in self.transformer_and_mapper_list:
                        names.extend(tansformer_mapper.mapper.transformed_names_)
                    self._engineered_feature_names_class.parse_raw_feature_names(
                        names)

        max_available_memory = memory_utilities.get_all_ram()

        if any_sparse:
            current_available_memory = memory_utilities.get_available_physical_memory()
            self._logger_wrapper('info',
                                 'Total ram: {} bytes, Current Available memory: {} bytes. Low memory threshold: {}'
                                 .format(max_available_memory, current_available_memory,
                                         constants.LOW_MEMORY_THRESHOLD))
            if current_available_memory > constants.LOW_MEMORY_THRESHOLD * max_available_memory:
                return sparse.hstack(features).tocsr()
            # Memory is under pressure, trade of diskIO for a more memory-efficient way than hstack to combine
            # feaure sets
            # Solution:
            # 1. convert each feature set into csr matrix, collecting information for the final result arrays,
            #    then dump csr matrix into pickle file
            # 2. release memory held by feature sets
            # 3. allocation memory for final result arrays
            # 4. load csr matrix back from pickle and update the final result arrays
            # 5. construct final csr matrix from final result arrays without any copying
            try:
                self._logger_wrapper(
                    'debug', '1. convert each feature set into csr matrix, \
                    collecting information for the final result arrays, \
                    then dump csr matrix into pickle file')
                final_size = 0
                column_count = 0
                row_count = -1
                offset_by_row = []  # type: List[int]
                dtypes = []
                pickle_files = []

                tmp_dir = 'tmp_{}'.format(uuid.uuid4())
                os.mkdir(tmp_dir)

                for i, fea in enumerate(features):

                    csr = sparse.csr_matrix(fea)
                    # shape info
                    final_size += csr.size
                    column_count += csr.shape[1]

                    if row_count == -1:
                        row_count = csr.shape[0]
                        offset_by_row = np.zeros([row_count], dtype=np.int64)
                    elif not row_count == csr.shape[0]:
                        raise ValueError(
                            "features have inconsistent row count")

                    # offset for first element in each row
                    for row_index in range(row_count):
                        offset_by_row[row_index] += csr.indptr[row_index]

                    # dtype info
                    dtypes.append(csr.dtype)
                    # pickle info
                    file_name = '{}/fea_{}'.format(tmp_dir, i)
                    pickle_files.append(file_name)
                    with open(file_name, 'wb') as pickle_file:
                        pickle.dump(csr, pickle_file, protocol=pickler.DEFAULT_PICKLE_PROTOCOL_VERSION)
                    del csr
                    gc.collect()

                final_shape = (row_count, column_count)
                data_dtype = np.find_common_type(dtypes, [])
                self._logger_wrapper(
                    'debug', '2. release memory held by feature sets')
                del features
                gc.collect()

                self._logger_wrapper(
                    'debug', '3. allocation memory for final result arrays')
                final_data = np.zeros([final_size], dtype=data_dtype)
                final_indices = np.zeros(
                    [final_size], dtype=sparse.sputils.get_index_dtype(maxval=max(final_shape)))
                final_indptr = np.zeros(
                    [row_count + 1], dtype=sparse.sputils.get_index_dtype(maxval=final_size))

                self._logger_wrapper(
                    'debug', "4. load coo matrix back from pickle and update the final result arrays")

                col_offset = 0
                for file_name in pickle_files:
                    with open(file_name, 'rb') as pickle_file:
                        csr = pickle.load(pickle_file)
                    # reference for csr spec:
                    # https://en.wikipedia.org/wiki/Sparse_matrix#Compressed_sparse_row_(CSR,_CRS_or_Yale_format)
                    row_offset = 0

                    for i in range(row_count):
                        row_size = csr.indptr[i + 1] - csr.indptr[i]
                        row_offset += row_size
                        final_indptr[i + 1] += row_offset
                        if row_size == 0:
                            continue
                        from_slice = slice(
                            csr.indptr[i], csr.indptr[i] + row_size)
                        to_slice = slice(
                            offset_by_row[i], offset_by_row[i] + row_size)
                        final_data[to_slice] = csr.data[from_slice]
                        final_indices[to_slice] = csr.indices[from_slice] + col_offset
                        offset_by_row[i] += row_size

                    col_offset += csr.shape[1]
                    del csr
                    gc.collect()

                self._logger_wrapper(
                    'debug', '5. construct csr matrix from final result arrays without any copying')
                # the three numpy arrays won't be copied when constructing sparse matrix
                #  https://docs.scipy.org/doc/numpy/reference/generated/numpy.array.html
                csr = sparse.csr_matrix(
                    (final_data, final_indices, final_indptr), shape=final_shape, copy=False)

                self._logger_wrapper('debug', '6. done')
                return csr

            finally:
                for f in pickle_files:
                    try:
                        if os.path.exists(f):
                            os.remove(f)
                    except Exception as e:
                        self._logger_wrapper(
                            'error', 'Error while removing pickle files in data_transformer.transform: {}'.format(e))

                if len(os.listdir(tmp_dir)) == 0:
                    os.rmdir(tmp_dir)
        else:
            return np.hstack(features)

    def _apply_transforms(self, df: pd.DataFrame) -> List[Any]:
        features = []
        if (self._is_onnx_compatible and not self.mapper) and (not self.transformer_and_mapper_list):
            raise Exception("fit not called")

        if self._is_onnx_compatible:
            assert self.mapper is not None
            transformed_data = self.mapper.transform(df)
            features.append(transformed_data)
        else:
            total_ram = memory_utilities.get_all_ram(self.logger)
            self._logger_wrapper("info", "Starting to apply transforms. Total ram: {} bytes".format(total_ram))
            for transformer_mapper in self.transformer_and_mapper_list:
                current_available_physical_memory = memory_utilities.get_available_physical_memory()
                transform_memory_footprint = transformer_mapper.memory_footprint_estimate
                self._logger_wrapper("info", "Transform memory estimate: {} bytes, Current available memory: {} bytes"
                                     .format(transform_memory_footprint, current_available_physical_memory))
                apply_transform = (transform_memory_footprint < current_available_physical_memory)

                transformer_list = featurization_utilities.get_transform_names(transformer_mapper.transformers)
                transformer_names = ",".join(transformer_list)
                if apply_transform:
                    self._logger_wrapper(
                        "info", "{}: Applying transform.".format(transformer_names))
                    try:
                        transform_output = transformer_mapper.mapper.transform(df)
                        features.append(transform_output)
                        self._logger_wrapper("info",
                                             "{transformers}: Finished applying transform. Shape {shape}".format(
                                                 shape=transform_output.shape,
                                                 transformers=transformer_names))
                    except Exception as e:
                        self._logger_wrapper(
                            "error", "{}: Failed to apply transform. Error: {}".format(transformer_names, e))

                        logging_utilities.log_traceback(e, self.logger, is_critical=False)
                else:
                    self._logger_wrapper("info", "{}: Transform not applied due to memory constraints.".format(
                        transformer_names))
            self._logger_wrapper("info", "Finished applying transforms")

        return features

    def get_engineered_feature_names(self) -> List[str]:
        """
        Get the engineered feature names.

        Return the list of engineered feature names as string after data transformations on the
        raw data have been finished.

        :return: The list of engineered fearure names as strings
        """
        return self._engineered_feature_names_class._engineered_feature_names

    def _get_json_str_for_engineered_feature_name(self,
                                                  engineered_feature_name: str) -> Optional[str]:
        """
        Return JSON string for engineered feature name.

        :param engineered_feature_name: Engineered feature name for
                                        whom JSON string is required
        :return: JSON string for engineered feature name
        """
        engineered_feature_name_json_obj = self._engineered_feature_names_class \
            .get_json_object_for_engineered_feature_name(engineered_feature_name)

        # If the JSON object is not valid, then return None
        if engineered_feature_name_json_obj is None:
            self._logger_wrapper(
                'info', "Not a valid feature name " + engineered_feature_name)
            return None

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
        for engineered_feature_name in engi_feature_name_list:

            json_str = self._get_json_str_for_engineered_feature_name(
                engineered_feature_name)

            if json_str is not None:
                engineered_feature_names_json_str_list.append(json_str)

        # Return the list of JSON strings for engineered feature names
        return engineered_feature_names_json_str_list

    def get_featurization_summary(self) -> FeaturizationSummaryType:
        """
        Return the featurization summary for all the input features seen by DataTransformer.

        :return: List of featurization summary for each input feature.
        """
        return self._engineered_feature_names_class.get_raw_features_featurization_summary()

    def _get_transforms(self, df: pd.DataFrame,
                        stats_and_column_purpose: List[StatsAndColumnPurposeType],
                        y: DataSingleColumnInputType = None) -> List[TransformerType]:
        """
        Identify the transformations for all the columns in the dataframe.

        :param df: Dataframe representing text, numerical or categorical input.
        :param stats_and_column_purposes: Statistics and column purposes of the given data.
        :param y: To match fit signature.
        :return: Transformations that go into datamapper.
        """
        transforms = []  # type: List[TransformerType]

        all_columns = df.columns
        dtypes = df.dtypes

        column_groups = {}  # type: Dict[str, List[str]]
        for _, column_purpose, column in stats_and_column_purpose:
            column_groups.setdefault(column_purpose, []).append(column)

        self._raw_feature_names, all_new_column_names = self._generate_new_column_names(
            all_columns)

        self._logger_wrapper('info', "Start getting transformers.")
        self._observer.report_status(
            ExperimentStatus.FeaturesGeneration, "Generating features for the dataset.")

        for column_purpose in column_groups.keys():
            current_column_transforms = self._get_transforms_per_column_purpose(column_groups[column_purpose],
                                                                                all_columns,
                                                                                dtypes,
                                                                                all_new_column_names,
                                                                                column_purpose,
                                                                                stats_and_column_purpose)

            if current_column_transforms:
                transforms.extend(current_column_transforms)
            else:
                # skip if hashes or ignore case
                self._logger_wrapper(
                    'info', "Hashes or single value column detected. No transforms needed")

        transforms.extend(self._sweep_column_purpose(transforms, all_columns, dtypes,
                                                     stats_and_column_purpose, all_new_column_names))

        sweeped_transforms = self._perform_feature_sweeping(df, y, stats_and_column_purpose, all_new_column_names)

        self._logger_wrapper("info", "Sweeping added the following transforms: {trs}".format(
            trs=sweeped_transforms
        ))
        transforms.extend(sweeped_transforms)

        if not transforms:
            # can happen when we get all hashes
            self._logger_wrapper(
                'warning', "No features could be identified or generated. Please inspect your data.")
            raise ValueError("No features could be identified or generated. Please inspect your data.")

        # Log the transformations done for raw data into the logs
        self._logger_wrapper(
            'info', self._get_transformations_str(all_columns, transforms))

        # Log stats_computation about raw data
        self._logger_wrapper('info',
                             self._pre_processing_stats.get_raw_data_stats())

        self._logger_wrapper('info', "End getting transformers.")

        if self._test_transforms is not None:
            transforms.extend(self._test_transforms)
        return transforms

    def _perform_feature_sweeping(self, df: pd.DataFrame, y: DataSingleColumnInputType,
                                  stats_and_column_purposes: List[StatsAndColumnPurposeType],
                                  all_new_column_names: List[str],
                                  feature_sweeper: Any = None) -> \
            List[TransformerType]:
        """
        Perform feature sweeping and return transforms.

        :param df: Input data frame.
        :param y: Input labels.
        :param stats_and_column_purposes: Stats and column purposes.
        :return: Transformers identified by the sweeping logic.
        """
        transforms = []  # type: List[TransformerType]
        try:
            if self._enable_feature_sweeping:
                self._logger_wrapper("info", "Performing feature sweeping")
                from azureml.automl.core.sweeping.meta_sweeper import MetaSweeper
                if feature_sweeper is None:
                    feature_sweeper = MetaSweeper(logger=self.logger, task=self._task_type,
                                                  timeout_sec=self._feature_sweeping_timeout)

                sweeped_transforms = feature_sweeper.sweep(
                    df, y, stats_and_column_purposes)
                if sweeped_transforms:
                    self._logger_wrapper('info', 'Sweeping added the following transforms: '
                                                 '{sweeped_transforms}'.format(sweeped_transforms=sweeped_transforms))

                    cols_list = []  # type: List[str]
                    for cols, tfs in sweeped_transforms:
                        if not isinstance(cols, list):
                            stats_and_column_purpose = next((x for x in stats_and_column_purposes if x[2] == cols))
                            column_purpose = stats_and_column_purpose[1]
                            index = stats_and_column_purposes.index(stats_and_column_purpose)
                            new_column_name = all_new_column_names[index]
                            cols_list = [str(new_column_name)]
                        else:
                            for col in cols:
                                stats_and_column_purpose = next((x for x in stats_and_column_purposes if x[2] == col))
                                # Assumption here is that all the columns in the list will be of one type
                                column_purpose = stats_and_column_purpose[1]
                                index = stats_and_column_purposes.index(stats_and_column_purpose)
                                new_column_name = all_new_column_names[index]
                                cols_list.append(new_column_name)

                        column_name_alias = self._engineered_feature_names_class. \
                            get_alias_name_from_pipeline_object(cols_list, tfs, column_purpose)

                        transforms.append((cols,
                                           make_pipeline(tfs),
                                           {"alias": str(column_name_alias)}))
            else:
                self._logger_wrapper("info", "Feature sweeping disabled.")
        except Exception as e:
            import traceback
            # Never fail the main run even if sweeping fails.
            self._logger_wrapper("debug", "Sweeping failed with error: {e}, "
                                          "stacktrace: {s}".format(e=e, s=traceback.format_exc()))
        finally:
            return transforms

    def _sweep_column_purpose(self, transforms: List[TransformerType],
                              columns: Index, dtypes: Series,
                              stats_and_column_purposes: List[StatsAndColumnPurposeType],
                              new_column_names: List[str]) -> List[TransformerType]:
        """
        Perform column purpose sweeping and return appropriate transforms.

        :param transforms: Current set of transforms.
        :param columns: Current set of columns in the data frame.
        :param dtypes: Current pandas dtypes.
        :param stats_and_column_purposes: Stats and column purposes of various columns.
        :param new_column_names: New columns names for Engineered feature name generation.
        :return:
        """
        column_index = 0
        if not transforms and len(columns) == 1:
            if not np.issubdtype(dtypes[column_index], np.number):
                raw_stats, column_purpose, column = stats_and_column_purposes[column_index]
                alternate_column_purpose = ColumnPurposeSweeper.safe_convert_column_type(
                    column_purpose)
                if alternate_column_purpose:
                    self._logger_wrapper(
                        "info",
                        "Column index: {column_index}, current column purpose: {detected_column_purpose}, "
                        "Alternate column purpose: {alternate_column_purpose}".format(
                            detected_column_purpose=column_purpose,
                            column_index=column_index,
                            alternate_column_purpose=alternate_column_purpose))
                    stats_and_column_purposes[column_index] = raw_stats, alternate_column_purpose, column
                    return self._get_transforms_per_column_purpose([columns[column_index]],
                                                                   columns, dtypes,
                                                                   new_column_names,
                                                                   alternate_column_purpose,
                                                                   stats_and_column_purposes)

        return []

    def _get_transforms_per_column_purpose(
            self,
            columnspurpose: List[str],
            columns: Index, dtypes: Series,
            new_column_names: List[str],
            detected_column_purpose: str,
            stats_and_column_purposes: List[StatsAndColumnPurposeType]) -> List[TransformerType]:
        """Obtain transformations based on column purpose and feature stats.

        :param column: Column name.
        :param new_column_name: New column name for engineered features.
        :param detected_column_purpose: Column purpose detected.
        :param raw_stats: Raw statistics of the column.
        :return: List of transformations to be done on this column.
        """
        tr = []  # type: List[TransformerType]
        for column in columnspurpose:
            stats_and_column_purpose = next(
                (x for x in stats_and_column_purposes if x[2] == column))
            index = stats_and_column_purposes.index(stats_and_column_purpose)
            raw_stats, _, _ = stats_and_column_purposes[index]
            new_column_name = new_column_names[index]
            if detected_column_purpose == FeatureTypeRecognizer.Numeric:
                tr.extend(self._get_numeric_transforms(
                    column, new_column_name))
                # if there are lot of imputed values, add an imputation marker
                if raw_stats.num_na > 0.01 * raw_stats.total_number_vals:
                    tr.extend(self._get_imputation_marker_transforms(
                        column, new_column_name))
            if detected_column_purpose == FeatureTypeRecognizer.DateTime:
                tr.extend(self._get_datetime_transforms(
                    column, new_column_name))
            if detected_column_purpose == FeatureTypeRecognizer.CategoricalHash:
                tr.extend(self._get_categorical_hash_transforms(
                    column, new_column_name, raw_stats.num_unique_vals))

            if detected_column_purpose == FeatureTypeRecognizer.Categorical:
                tr.extend(self._get_categorical_transforms(
                    column, new_column_name, raw_stats.num_unique_vals))

            if detected_column_purpose == FeatureTypeRecognizer.Text:
                self._text_transformer = self._text_transformer or TextTransformer(self._task_type, self.logger,
                                                                                   self._is_onnx_compatible)
                tr.extend(self._text_transformer.get_transforms(column, new_column_name,
                                                                get_ngram_len(
                                                                    raw_stats.lengths),
                                                                self._engineered_feature_names_class))

            if detected_column_purpose in FeatureTypeRecognizer.DROP_SET:
                tr.extend(self._get_drop_column_transform(
                    column, new_column_name, detected_column_purpose))

            column_loc = columns.get_loc(column)

            utilities._log_raw_data_stat(
                raw_stats, self.logger,
                prefix_message="[XColNum:{}]".format(
                    column_loc
                )
            )

            self._logger_wrapper(
                'info',
                "Preprocess transformer for col {}, datatype: {}, detected "
                "datatype {}".format(
                    column_loc,
                    str(dtypes[index]),
                    str(detected_column_purpose)
                )
            )
            # Update pre-processing stats_computation
            self._pre_processing_stats.update_raw_feature_stats(
                detected_column_purpose)

        return tr

    def _get_drop_column_transform(
            self,
            column: str,
            column_name: str,
            column_purpose: str) -> List[TransformerType]:

        tr = []  # type:  List[TransformerType]

        # Add the transformations to be done and get the alias name
        # for the drop transform.
        drop_transformer = _Transformer(
            parent_feature_list=[str(column_name)],
            transformation_fnc=_TransformationFunctionNames.Drop,
            operator=None,
            feature_type=column_purpose,
            should_output=True)
        # Create an object to convert transformations into JSON object
        feature_transformers = \
            _FeatureTransformers([drop_transformer])

        # Create the JSON object
        json_obj = feature_transformers.encode_transformations_from_list()
        # Persist the JSON object for later use
        self._engineered_feature_names_class.get_raw_feature_alias_name(json_obj)

        return tr

    def _get_categorical_hash_transforms(
            self,
            column: str,
            column_name: str,
            num_unique_categories: int) -> List[TransformerType]:
        """
        Create a list of transforms for categorical hash data.

        :param column: Column name in the data frame.
        :param column_name: Name of the column for engineered feature names
        :param num_unique_categories: Number of unique categories
        :return: Categorical hash transformations to use in a list.
        """
        # Add the transformations to be done and get the alias name
        # for the hashing one hot encode transform.
        categorical_hash_string_cast_transformer = _Transformer(
            parent_feature_list=[str(column_name)],
            transformation_fnc=_TransformationFunctionNames.StringCast,
            operator=None,
            feature_type=FeatureTypeRecognizer.CategoricalHash,
            should_output=False)
        # This transformation depends on the previous# transformation
        categorical_hash_onehot_encode_transformer = _Transformer(
            parent_feature_list=[1],
            transformation_fnc=_TransformationFunctionNames.HashOneHotEncode,
            operator=None, feature_type=None,
            should_output=True)
        # Create an object to convert transformations into JSON object
        feature_transformers = \
            _FeatureTransformers(
                [categorical_hash_string_cast_transformer,
                 categorical_hash_onehot_encode_transformer])

        # Create the JSON object
        json_obj = feature_transformers.encode_transformations_from_list()
        # Persist the JSON object for later use and obtain an alias name
        alias_column_name = self._engineered_feature_names_class.get_raw_feature_alias_name(
            json_obj)

        # Add the transformations to be done and get the alias name
        # for the raw column.
        number_of_bits = pow(2, int(math.log(num_unique_categories, 2)))
        tr = []  # type:  List[TransformerType]
        tr = [(column, [TextFeaturizers.string_cast(logger=self.logger),
                        CategoricalFeaturizers.hashonehot_vectorizer(
                            hashing_seed_val=constants.hashing_seed_value,
                            num_cols=int(number_of_bits),
                            logger=self.logger)],
               {'alias': str(alias_column_name)})]

        return tr

    def _get_datetime_transforms(
            self,
            column: str,
            column_name: str) -> List[TransformerType]:
        """
        Create a list of transforms for date time data.

        :param column: Column name in the data frame.
        :param column_name: Name of the column for engineered feature names
        :return: Date time transformations to use in a list.
        """
        # Add the transformations to be done and get the alias name
        # for the date time transform.
        datatime_imputer_transformer = _Transformer(
            parent_feature_list=[str(column_name)],
            transformation_fnc=_TransformationFunctionNames.Imputer,
            operator=_OperatorNames.Mode,
            feature_type=FeatureTypeRecognizer.DateTime,
            should_output=True)
        # This transformation depends on the previous transformation
        datatime_string_cast_transformer = _Transformer(
            parent_feature_list=[1],
            transformation_fnc=_TransformationFunctionNames.StringCast,
            operator=None, feature_type=None,
            should_output=False)
        # This transformation depends on the previous transformation
        datatime_datetime_transformer = _Transformer(
            parent_feature_list=[2],
            transformation_fnc=_TransformationFunctionNames.DateTime,
            operator=None, feature_type=None,
            should_output=False)
        # Create an object to convert transformations into JSON object
        feature_transformers = _FeatureTransformers(
            [datatime_imputer_transformer,
             datatime_string_cast_transformer,
             datatime_datetime_transformer])
        # Create the JSON object
        json_obj = \
            feature_transformers.encode_transformations_from_list()
        # Persist the JSON object for later use and obtain an alias name
        alias_column_name = \
            self._engineered_feature_names_class.get_raw_feature_alias_name(
                json_obj)

        # Add the transformations to be done and get the alias name
        # for the raw column.
        tr = []  # type:  List[TransformerType]
        tr = [(column,
               [CategoricalFeaturizers.cat_imputer(logger=self.logger),
                TextFeaturizers.string_cast(logger=self.logger),
                DateTimeFeaturesTransformer(logger=self.logger)],
               {'alias': str(alias_column_name)})]

        return tr

    def _get_categorical_transforms(
            self,
            column: str,
            column_name: str,
            num_unique_categories: int) -> List[TransformerType]:
        """
        Create a list of transforms for categorical data.

        :param column: Column name in the data frame.
        :param column_name: Name of the column for engineered feature names
        :param num_unique_categories: Number of unique categories
        :return: Categorical transformations to use in a list.
        """
        tr = []  # type:  List[TransformerType]
        if num_unique_categories <= 2:

            # Add the transformations to be done and get the alias name
            # for the hashing label encode transform.
            cat_two_category_imputer_transformer = _Transformer(
                parent_feature_list=[str(column_name)],
                transformation_fnc=_TransformationFunctionNames.Imputer,
                operator=_OperatorNames.Mode,
                feature_type=FeatureTypeRecognizer.Categorical,
                should_output=True)
            # This transformation depends on the previous transformation
            cat_two_category_string_cast_transformer = _Transformer(
                parent_feature_list=[1],
                transformation_fnc=_TransformationFunctionNames.StringCast,
                operator=None, feature_type=None,
                should_output=False)
            # This transformation depends on the previous transformation
            cat_two_category_label_encode_transformer = _Transformer(
                parent_feature_list=[2],
                transformation_fnc=_TransformationFunctionNames.LabelEncoder,
                operator=None, feature_type=None,
                should_output=True)
            # Create an object to convert transformations into JSON object
            feature_transformers = _FeatureTransformers(
                [cat_two_category_imputer_transformer,
                 cat_two_category_string_cast_transformer,
                 cat_two_category_label_encode_transformer])
            # Create the JSON object
            json_obj = \
                feature_transformers.encode_transformations_from_list()
            # Persist the JSON object for later use and obtain an alias name
            alias_column_name = self._engineered_feature_names_class.get_raw_feature_alias_name(
                json_obj)

            # Add the transformations to be done and get the alias name
            # for the raw column.
            tr = [(column,
                   [CategoricalFeaturizers.cat_imputer(logger=self.logger),
                    TextFeaturizers.string_cast(logger=self.logger),
                    CategoricalFeaturizers.labelencoder(
                        hashing_seed_val=constants.hashing_seed_value,
                        logger=self.logger)],
                   {'alias': str(alias_column_name)})]

            return tr
        else:
            # Add the transformations to be done and get the alias name
            # for the hashing one hot encode transform.
            cat_multiple_category_string_cast_transformer = _Transformer(
                parent_feature_list=[str(column_name)],
                transformation_fnc=_TransformationFunctionNames.StringCast,
                operator=None, feature_type=FeatureTypeRecognizer.Categorical,
                should_output=False)
            # This transformation depends on the previous transformation
            cat_multiple_category_countvec_transformer = _Transformer(
                parent_feature_list=[1],
                transformation_fnc=_TransformationFunctionNames.CountVec,
                operator=_OperatorNames.CharGram, feature_type=None,
                should_output=True)
            # Create an object to convert transformations into JSON object
            feature_transformers = _FeatureTransformers([
                cat_multiple_category_string_cast_transformer,
                cat_multiple_category_countvec_transformer])
            # Create the JSON object
            json_obj = feature_transformers.encode_transformations_from_list()
            # Persist the JSON object for later use and obtain an alias name
            alias_column_name = self._engineered_feature_names_class.get_raw_feature_alias_name(
                json_obj)

            # use CountVectorizer for both Hash and CategoricalHash for now
            tr = [(column,
                   [TextFeaturizers.string_cast(logger=self.logger),
                    TextFeaturizers.count_vectorizer(tokenizer=self._wrap_in_lst, binary=True)],
                   {'alias': str(alias_column_name)})]

            return tr

    def _get_numeric_transforms(
            self,
            column: str,
            column_name: str) -> List[TransformerType]:
        """
        Create a list of transforms for numerical data.

        :param column: Column name in the data frame.
        :param column_name: Name of the column for engineered feature names
        :return: Numerical transformations to use in a list.
        """
        # Add the transformations to be done and get the alias name
        # for the numerical transform
        numeric_transformer = _Transformer(
            parent_feature_list=[str(column_name)],
            transformation_fnc=_TransformationFunctionNames.Imputer,
            operator=_OperatorNames.Mean,
            feature_type=FeatureTypeRecognizer.Numeric,
            should_output=True)
        # Create an object to convert transformations into JSON object
        feature_transformers = _FeatureTransformers([numeric_transformer])
        # Create the JSON object
        json_obj = feature_transformers.encode_transformations_from_list()
        # Persist the JSON object for later use and obtain an alias name
        alias_column_name = \
            self._engineered_feature_names_class.get_raw_feature_alias_name(
                json_obj)

        # Add the transformations to be done and get the alias name
        # for the imputation marker transform.
        # floats or ints go as they are, we only fix NaN
        tr = [([column], [GenericFeaturizers.imputer()],
               {'alias': str(alias_column_name)})]

        return cast(List[TransformerType], tr)

    def _get_imputation_marker_transforms(self, column, column_name):
        """
        Create a list of transforms for numerical data.

        :param column: Column name in the data frame.
        :param column_name: Name of the column for engineered feature names
        :return: Numerical transformations to use in a list.
        """
        # Add the transformations to be done and get the alias name
        # for the imputation marker transform.
        imputation_transformer = _Transformer(
            parent_feature_list=[str(column_name)],
            transformation_fnc=_TransformationFunctionNames.ImputationMarker,
            operator=None, feature_type=FeatureTypeRecognizer.Numeric,
            should_output=True)
        # Create an object to convert transformations into JSON object
        feature_transformers = _FeatureTransformers([imputation_transformer])
        # Create the JSON object
        json_obj = feature_transformers.encode_transformations_from_list()
        # Persist the JSON object for later use and obtain an alias name
        alias_column_name = \
            self._engineered_feature_names_class.get_raw_feature_alias_name(
                json_obj)

        # Add the transformations to be done and get the alias name
        # for the imputation marker transform.
        tr = [([column],
               [GenericFeaturizers.imputation_marker(logger=self.logger)],
               {'alias': str(alias_column_name)})]

        return tr

    def _wrap_in_lst(self, x):
        """
        Wrap an element in list.

        :param x: Element like string or integer.
        """
        return [x]

    def _get_pandas_columns_types_mapping(self, df: pd.DataFrame) -> Dict[str, np.dtype]:
        columns_types_mapping = {}  # type: Dict[str, np.dtype]
        for col in df.columns:
            columns_types_mapping[col] = df[col].dtype
        return columns_types_mapping

    def _check_columns_names_and_convert_types(self,
                                               df: pd.DataFrame,
                                               columns_types_mapping: Dict[str, np.dtype]) -> pd.DataFrame:
        curr_columns_types_mapping = self._get_pandas_columns_types_mapping(df)
        if len(curr_columns_types_mapping) != len(columns_types_mapping):
            raise DataException("The fitted data has {} columns but the input data has {} columns.".
                                format(len(curr_columns_types_mapping), len(columns_types_mapping)))
        type_converted_columns = {}  # type: Dict[str, np.dtype]
        for col, col_type in curr_columns_types_mapping.items():
            if col not in columns_types_mapping:
                print("Input column {} not found in the fitted columns.".format(col))
                raise DataException("Input column not found in the fitted columns.")
            if col_type != columns_types_mapping[col]:
                type_converted_columns[col] = columns_types_mapping[col]
        if len(type_converted_columns) > 0:
            for col, col_type in type_converted_columns.items():
                try:
                    df[col] = df[col].astype(col_type)
                except Exception as e:
                    print("Error converting the column {} as input column does not match the fitted "
                          "column type {}. ErrorMessage:\n{}".format(col, col_type, e))
                    raise DataException("Error converting the input column as column does not match the "
                                        "fitted column type.")
        return df

    def _get_transformations_str(
            self,
            columns: Index,
            transforms: List[TransformerType]) -> str:
        """
        Get the data transformations recorded for raw columns as strings.

        :param df: Input dataframe.
        :type df:numpy.ndarray or pandas.DataFrame or sparse matrix
        :param transforms: List of applied transformations for various raw
        columns as a string.
        :type transforms: List
        """
        transformation_str = 'Transforms:\n'
        list_of_transforms_as_list = []

        num_transforms = len(transforms)
        # Walk all columns in the input dataframe
        for column in columns:
            # Get all the indexes of transformations for the current column
            column_matches_transforms = [i for i in range(
                num_transforms) if transforms[i][0] == column]

            # If no matches for column name is found, then look for list having
            # this column name
            if len(column_matches_transforms) == 0:
                column_matches_transforms = [i for i in range(
                    num_transforms) if transforms[i][0] == [column]]

            # look for list of columns having this column name
            column_matches_transforms = \
                [i for i in range(0, len(transforms))
                 if isinstance(transforms[i][0], list) and column in transforms[i][0]]

            # Walk all the transformations found for the current column and add
            # to a string
            for transform_index in column_matches_transforms:

                transformers_list = transforms[transform_index][1]
                if isinstance(transformers_list, Pipeline):
                    transformers_list = [t[1] for t in transformers_list.steps]

                some_str = 'col {}, transformers: {}'.format(
                    columns.get_loc(column), '\t'.join([tf.__class__.__name__ for tf in transformers_list]))

                list_of_transforms_as_list.append(some_str)

        transformation_str += '\n'.join(list_of_transforms_as_list)

        # Return the string representation of all the transformations
        return transformation_str

    @classmethod
    def _generate_new_column_names(cls: Type["DataTransformer"], columns: List[str]) -> Tuple[List[str], List[str]]:
        # In case column names are not specified by the user,
        # append the prefix with a counter to generate a raw feature name
        generated_column_name_prefix = 'C'
        index_raw_columns = 0

        new_column_names = []  # type: List[str]
        raw_feature_names = []  # type: List[str]
        for column in columns:
            # If column name is not an integer, then record it in the raw feature name
            if not isinstance(column, (int, np.integer)):
                raw_feature_names.append(column)
                new_column_name = column
            else:
                # TODO When there is a string column name present, we should be re-using it rather
                # than generating a new one that is completely devoid of the name

                # If the column name is missing, create a new column name for the transformations
                index_raw_columns += 1
                new_column_name = '{prefix}{index}'.format(prefix=generated_column_name_prefix,
                                                           index=index_raw_columns)

            new_column_names.append(new_column_name)
        return raw_feature_names, new_column_names

    def __getstate__(self):
        """
        Get state picklable objects.

        :return: state
        """
        base_sanitized_state = super(DataTransformer, self).__getstate__()
        state = dict(base_sanitized_state)
        # Remove the unpicklable entries.
        del state['_observer']
        return state

    def __setstate__(self, state):
        """
        Set state for object reconstruction.

        :param state: pickle state
        """
        state['_observer'] = NullExperimentObserver()
        new_data_transformer = DataTransformer()
        new_data_transformer.logger = None
        for k, v in new_data_transformer.__dict__.items():
            if k not in state:
                state[k] = v
        super(DataTransformer, self).__setstate__(state)
