# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Global methods used during an automated machine learning iteration for both remote and local runs."""
import json

import numpy as np
import pandas as pd
import scipy
from automl.client.core.common.datasets import ClientDatasets
from automl.client.core.common import logging_utilities
from azureml.automl.core import data_transformation, fit_pipeline as fit_pipeline_helper
from azureml.automl.core.automl_pipeline import AutoMLPipeline
from azureml.automl.core.data_context import RawDataContext, TransformedDataContext

from azureml.core import Experiment, Run
from azureml.telemetry.activity import log_activity

from . import _constants_azureml
from ._azureautomlsettings import AzureAutoMLSettings
from ._azureautomlruncontext import AzureAutoMLRunContext
from ._cachestorefactory import CacheStoreFactory
from ._logging import get_logger


def _get_problem_info(X, y, task_type, y_transformer=None):
    dataset = ClientDatasets()
    dataset.parse_data("parse", X, y, task_type,
                       init_all_stats=False, y_transformer=y_transformer)
    problem_info = dataset.get_problem_info()
    return problem_info


def _subsampling_recommended(num_samples, num_features):
    """
    Recommend whether subsampling should be on or off based on shape of X.

    :param num_samples: Number of samples after preprocessing.
    :type num_samples: int
    :param num_features: Number of features after preprocessing.
    :type num_features: int
    :return: Flag indicate whether subsampling is recommended for given shape of X.
    :rtype: bool
    """
    # Ideally this number should be on service side.
    # However this number is proportional to the iteration overhead.
    # Which makes this specific number SDK specific.
    # For nativeclient or miroclient, this number will be different due to smaller overhead.
    # We will leave this here for now until we have a way of incorporating
    # hardware and network numbers in our model
    return num_samples * num_features > 300000000


def set_problem_info(X, y, task_type, current_run=None, workspace=None,
                     experiment_name=None, run_id=None, preprocess=False,
                     lag_length=0, transformed_data_context=None,
                     enable_cache=True, subsampling=None,
                     timeseries=False, timeseries_param_dict=None, is_adb_run=False,
                     is_onnx_compatible=False, logger=None, **kwargs):
    """
    Set statistics about user data. Note that this function is deprecated.

    :param X: The training features to use when fitting pipelines during AutoML experiment.
    :type X: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
    :param y: Training labels to use when fitting pipelines during AutoML experiment.
    :type y: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
    :param task_type: 'classification' or 'regression' depending on what kind of ML problem to solve.
    :type task_type: str or azureml.train.automl.constants.Tasks
    :param current_run: The AutoMLRun to set the info for.
    :type current_run: azureml.core.run.Run
    :param workspace: AzureML workspace containing this run.
    :type workspace: azureml.core.workspace.Workspace
    :param experiment_name: The experiment name.
    :type experiment_name: str
    :param run_id: ID of the run to set the info for.
    :type run_id: str
    :param preprocess: Flag whether to preprocess the data.
    :type preprocess: bool
    :param lag_length: How much to lag the features by for Lagging preprocessor.
    :type lag_length: int
    :param transformed_data_context: Containing X, y and other transformed data info.
    :type transformed_data_context: TransformedDataContext
    :param enable_cache: enable preprocessor cache
    :type enable_cache: Boolean
    :param subsampling: Flag to indicate whether this run should use subsampling.
    :type subsampling: bool
    :param timeseries: Flag whether to preprocess the data as timeseries.
    :type timeseries: bool
    :param timeseries_param_dict: Timeseries related parameters.
    :type timeseries_param_dict: dict
    :param is_adb_run: flag whether this is a azure databricks run or not.
    :type is_adb_run: bool
    :param is_onnx_compatible: if works in onnx compatible mode
    :type is_onnx_compatible: bool
    :param logger: the logger.
    :type logger: logging.logger
    :return: None
    """
    if logger:
        logger.warning('set_problem_info() is deprecated. It will be removed in a future release.')
    _set_problem_info(X, y, task_type, current_run, workspace, experiment_name, run_id, preprocess,
                      lag_length, transformed_data_context, enable_cache, subsampling, timeseries,
                      timeseries_param_dict, is_adb_run, is_onnx_compatible, logger, **kwargs)


def _set_problem_info(X, y, task_type, current_run=None, workspace=None,
                      experiment_name=None, run_id=None, preprocess=False,
                      lag_length=0, transformed_data_context=None,
                      enable_cache=True, subsampling=None,
                      timeseries=False, timeseries_param_dict=None, is_adb_run=False,
                      is_onnx_compatible=False, logger=None, **kwargs):
    """
    Set statistics about user data.

    :param X: The training features to use when fitting pipelines during AutoML experiment.
    :type X: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
    :param y: Training labels to use when fitting pipelines during AutoML experiment.
    :type y: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
    :param task_type: 'classification' or 'regression' depending on what kind of ML problem to solve.
    :type task_type: str or azureml.train.automl.constants.Tasks
    :param current_run: The AutoMLRun to set the info for.
    :type current_run: azureml.core.run.Run
    :param workspace: AzureML workspace containing this run.
    :type workspace: azureml.core.workspace.Workspace
    :param experiment_name: The experiment name.
    :type experiment_name: str
    :param run_id: ID of the run to set the info for.
    :type run_id: str
    :param preprocess: Flag whether to preprocess the data.
    :type preprocess: bool
    :param lag_length: How much to lag the features by for Lagging preprocessor.
    :type lag_length: int
    :param transformed_data_context: Containing X, y and other transformed data info.
    :type transformed_data_context: TransformedDataContext
    :param enable_cache: enable preprocessor cache
    :type enable_cache: Boolean
    :param subsampling: Flag to indicate whether this run should use subsampling.
    :type subsampling: bool
    :param timeseries: Flag whether to preprocess the data as timeseries.
    :type timeseries: bool
    :param timeseries_param_dict: Timeseries related parameters.
    :type timeseries_param_dict: dict
    :param is_adb_run: flag whether this is a azure databricks run or not.
    :type is_adb_run: bool
    :param is_onnx_compatible: if works in onnx compatible mode
    :type is_onnx_compatible: bool
    :param logger: the logger.
    :type logger: logging.logger
    :return: None
    """
    x_raw_column_names = None
    if isinstance(X, pd.DataFrame):
        x_raw_column_names = X.columns.values
    if run_id is None and current_run is not None:
        run_id = current_run._run_id
    if logger is not None:
        # logging X and y info
        logging_utilities.log_data_info(logger=logger, data_name="X", data=X, run_id=run_id)
        logging_utilities.log_data_info(logger=logger, data_name="y", data=y, run_id=run_id)
    if transformed_data_context is None:
        raw_data_context = RawDataContext(task_type=task_type,
                                          X=X,
                                          y=y,
                                          x_raw_column_names=x_raw_column_names,
                                          preprocess=preprocess,
                                          lag_length=lag_length,
                                          timeseries=timeseries,
                                          timeseries_param_dict=timeseries_param_dict)
        cache_store = CacheStoreFactory.get_cache_store(enable_cache=enable_cache, run_id=run_id,
                                                        logger=logger)
        transformed_data_context = data_transformation.transform_data(raw_data_context=raw_data_context,
                                                                      cache_store=cache_store,
                                                                      is_onnx_compatible=is_onnx_compatible,
                                                                      logger=logger)
    X = transformed_data_context.X

    if subsampling is None:
        subsampling = _subsampling_recommended(X.shape[0], X.shape[1])

    problem_info_dict = {
        "dataset_num_categorical": 0,
        "dataset_classes": len(np.unique(y)),
        "dataset_features": X.shape[1],
        "dataset_samples": X.shape[0],
        "is_sparse": scipy.sparse.issparse(X),
        "subsampling": subsampling
    }

    problem_info_str = json.dumps(problem_info_dict)
    # This is required since token may expire
    if is_adb_run:
        current_run = Run.get_context()

    if current_run is None:
        experiment = Experiment(workspace, experiment_name)
        current_run = Run(experiment, run_id)

    current_run.add_properties(
        {_constants_azureml.Properties.PROBLEM_INFO: problem_info_str})


def fit_pipeline(pipeline_script,
                 automl_settings,
                 run_id,
                 X=None,
                 y=None,
                 sample_weight=None,
                 X_valid=None,
                 y_valid=None,
                 sample_weight_valid=None,
                 cv_splits_indices=None,
                 train_frac=1,
                 fit_iteration_parameters_dict=None,
                 experiment=None,
                 pipeline_id=None,
                 score_min=None,
                 score_max=None,
                 remote=True,
                 is_adb_run=False,
                 logger=None,
                 child_run_metrics=None,
                 transformed_data_context=None,
                 elapsed_time=None,
                 onnx_cvt=None,
                 **kwargs):
    """
    Run a single iteration of an automated machine learning experiment. Note that this function is deprecated.

    This method is automatically called during a regular Automated Machine Learning
    experiment. fit_pipeline will evaluate the pipeline for this iteration, fit the pipeline with the provided data,
    calculate the various metrics relevant for this experiment, and log all the results in the specified Run's
    history.

    :param pipeline_script: serialized Pipeline returned from the server.
    :type pipeline_script: str
    :param automl_settings: User settings specified when creating AutoMLConfig.
    :type automl_settings: str or dict
    :param run_id: AzureML Child Run id for this fit.
    :type run_id: str
    :param X: Input training data.
    :type X: numpy.ndarray or pandas.DataFrame
    :param y: Input training labels.
    :type y: numpy.ndarray or pandas.DataFrame
    :param sample_weight: Sample weights for training data.
    :type sample_weight: numpy.ndarray or pandas.DataFrame
    :param X_valid: validation data.
    :type X_valid: numpy.ndarray or pandas.DataFrame
    :param y_valid: validation labels.
    :type y_valid: numpy.ndarray or pandas.DataFrame
    :param sample_weight_valid: validation set sample weights.
    :type sample_weight_valid: numpy.ndarray or pandas.DataFrame
    :param cv_splits_indices: Custom indices by which to split the data when running cross validation.
    :type cv_splits_indices: numpy.ndarray or pandas.DataFrame
    :param train_frac: Fraction of training data to use, (0,1].
    :type train_frac: float
    :param fit_iteration_parameters_dict: Remaining data specific parameters for fit such as 'x_raw_column_names'.
    :type fit_iteration_parameters_dict: dict
    :param experiment: The azureml.core experiment.
    :type experiment: azureml.core.experiment.Experiment
    :param pipeline_id: Hash Id of current pipeline being evaluated.
    :type pipeline_id: str
    :param score_min: current min score for the experiment if applicable.
    :type score_min: float or str
    :param score_max: current max score for the experiment if applicable.
    :type score_max: float or str
    :param remote: flag whether this is a remote run or local run.
    :type remote: bool
    :param is_adb_run: flag whether this is a azure databricks run or not.
    :type is_adb_run: bool
    :param logger: logger for info/error messages.
    :param child_run_metrics: child run metrics
    :type child_run_metrics: run context
    :param transformed_data_context: Containing X, y and other transformed data info.
    :type transformed_data_context: TransformedDataContext
    :param elapsed_time: How long this experiment has already taken in minutes
    :type elapsed_time: int
    :param onnx_cvt: The onnx converter.
    :type onnx_cvt: OnnxConverter
    :return: AzureML Run Properties for this child run
    :rtype: dict
    """
    if logger is None:
        logger = get_logger(automl_settings=automl_settings)
    logger.warning('fit_pipeline() is deprecated. It will be removed in a future release.')

    with log_activity(logger=logger, activity_name='fit_pipeline'):
        automl_settings_obj = AzureAutoMLSettings.from_string_or_dict(automl_settings, experiment=experiment)
        if fit_iteration_parameters_dict is None and transformed_data_context is None:
            fit_iteration_parameters_dict = {
                'X': X,
                'y': y,
                'X_valid': X_valid,
                'y_valid': y_valid,
                'sample_weight': sample_weight,
                'sample_weight_valid': sample_weight_valid,
                'cv_splits_indices': cv_splits_indices,
                'x_raw_column_names': None
            }
        if child_run_metrics is None and remote:
            child_run_metrics = Run.get_context()

        automl_run_context = AzureAutoMLRunContext(child_run_metrics, is_adb_run)
        automl_pipeline = AutoMLPipeline(automl_run_context, pipeline_script, pipeline_id, train_frac)

        return fit_pipeline_helper.fit_pipeline(
            automl_pipeline,
            automl_settings_obj,
            automl_run_context,
            fit_iteration_parameters_dict,
            remote,
            logger,
            transformed_data_context,
            elapsed_time,
            onnx_cvt).get_output_dict()
