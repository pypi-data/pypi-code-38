# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""AutoML object in charge of orchestrating various AutoML runs for predicting models."""
from typing import Any, cast, Dict, List, Optional
import json
import math
import os
import os.path
import sys
import warnings
from datetime import datetime

from msrest.exceptions import HttpOperationError
import numpy as np
import pandas as pd
import pytz
import sklearn

from automl.client.core.common import logging_utilities
from automl.client.core.common import memory_utilities
from automl.client.core.common import model_wrappers
from automl.client.core.common import pipeline_spec
from automl.client.core.common import utilities as common_utilities
from automl.client.core.common.constants import TelemetryConstants
from automl.client.core.common.exceptions import ClientException, DataException, ConfigException, ServiceException
from automl.client.core.common.limit_function_call_exceptions import TimeoutException
from automl.client.core.common.logging_utilities import BLACKLISTED_LOGGING_KEYS
from azureml.automl.core import data_transformation
from azureml.automl.core import dataprep_utilities
from azureml.automl.core import dataset_utilities
from azureml.automl.core import fit_pipeline as fit_pipeline_helper
from azureml.automl.core import training_utilities
from azureml.automl.core._experiment_observer import ExperimentStatus
from azureml.automl.core.automl_pipeline import AutoMLPipeline
from azureml.automl.core.console_interface import ConsoleInterface
from azureml.automl.core.data_context import RawDataContext
from azureml.automl.core.systemusage_telemetry import SystemResourceUsageTelemetryFactory
from azureml.automl.core.onnx_convert import OnnxConverter

from azureml._restclient.service_context import ServiceContext
from azureml._restclient import JasmineClient, ExperimentClient
from azureml._restclient.models.create_parent_run_dto import CreateParentRunDto
from azureml.core import Run
from azureml.core.compute_target import AbstractComputeTarget
from azureml.core.runconfig import RunConfiguration
from azureml.core._serialization_utils import _serialize_to_dict
from azureml.exceptions import ServiceException as AzureMLServiceException
from azureml.telemetry import get_diagnostics_collection_info, is_diagnostics_collection_info_available
from azureml.telemetry.activity import log_activity

from . import automl, constants
from ._adb_driver_node import _AdbDriverNode
from ._adb_run_experiment import adb_run_experiment
from ._azureautomlruncontext import AzureAutoMLRunContext
from ._azureautomlsettings import AzureAutoMLSettings
from ._azure_experiment_observer import AzureExperimentObserver
from ._cachestorefactory import CacheStoreFactory
from ._environment_utilities import log_user_sdk_dependencies, modify_run_configuration
from ._remote_console_interface import RemoteConsoleInterface
from ._logging import get_logger, TELEMETRY_AUTOML_COMPONENT_KEY
from .automl_adb_run import AutoMLADBRun
from .run import AutoMLRun
from .utilities import friendly_http_exception, _get_package_version, _load_user_script


class AzureAutoMLClient:
    """Client to run AutoML experiments on Azure Machine Learning platform."""

    # Caches for querying and printing child runs
    run_map = {}
    metric_map = {}
    properties_map = {}

    def __init__(self,
                 experiment,
                 **kwargs):
        """
        Construct the AzureMLClient class.

        :param experiment: The azureml.core experiment
        :param kwargs: dictionary of keyword args
        :keyword something: something
        :keyword iterations: Number of different pipelines to test
        :keyword data_script: File path to the script containing get_data()
        :keyword primary_metric: The metric that you want to optimize.
        :keyword task_type: Field describing whether this will be a classification or regression experiment
        :keyword compute_target: The AzureML compute to run the AutoML experiment on
        :keyword validation_size: What percent of the data to hold out for validation
        :keyword n_cross_validations: How many cross validations to perform
        :keyword y_min: Minimum value of y for a regression experiment
        :keyword y_max: Maximum value of y for a regression experiment
        :keyword num_classes: Number of classes in the label data
        :keyword preprocess: Flag whether AutoML should preprocess your data for you
        :keyword lag_length: How many rows to lag data when preprocessing time series data
        :keyword max_cores_per_iteration: Maximum number of threads to use for a given iteration
        :keyword iteration_timeout_minutes: Maximum time in minutes that each iteration before it terminates
        :keyword mem_in_mb: Maximum memory usage of each iteration before it terminates
        :keyword enforce_time_on_windows: flag to enforce time limit on model training at each iteration under windows.
        :keyword blacklist_algos: List of algorithms to ignore for AutoML experiment
        :keyword exclude_nan_labels: Flag whether to exclude rows with NaN values in the label
        :keyword auto_blacklist: Flag whether AutoML should try to exclude algorithms
            that it thinks won't perform well.
        :keyword verbosity: Verbosity level for AutoML log file
        :keyword enable_tf: Flag to enable/disable Tensorflow  algorithms
        :keyword enable_subsampling: Flag to enable/disable subsampling. Note that even if it's true,
            subsampling would not be enabled for small datasets or iterations.
        :keyword subsample_seed: random_state used to sample the data.
        :keyword debug_log: File path to AutoML logs
        """
        if experiment is None:
            raise TypeError('AzureML experiment must be passed for AutoML.')

        self.automl_settings = AzureAutoMLSettings(experiment=experiment, **kwargs)

        self.experiment = experiment

        self._status = constants.Status.NotStarted
        self._loop = None
        self._score_max = None
        self._score_min = None
        self._score_best = None
        self._console_logger = open(os.devnull, "w")

        self.parent_run_id = None
        self.current_iter = None
        self.input_data = None
        self._adb_thread = None

        self._check_create_folders(self.automl_settings.path)

        telemetry_set_by_user = True
        # turn on default telemetry collection, if user is not set
        if not is_diagnostics_collection_info_available():
            telemetry_set_by_user = False

        self.logger = get_logger(
            self.automl_settings.debug_log,
            self.automl_settings.verbosity,
            automl_settings=self.automl_settings)

        if not telemetry_set_by_user:
            self.logger.info("Telemetry collection is not set, turning it on by default.")

        send_telemetry, level = get_diagnostics_collection_info(component_name=TELEMETRY_AUTOML_COMPONENT_KEY)
        self.automl_settings.telemetry_verbosity = level
        self.automl_settings.send_telemetry = send_telemetry
        self._usage_telemetry = SystemResourceUsageTelemetryFactory.get_system_usage_telemetry(
            self.logger)
        self._usage_telemetry.start()

        self.experiment_start_time = None

        if not self.automl_settings.show_warnings:
            # sklearn forces warnings, so we disable them here
            warnings.simplefilter('ignore', DeprecationWarning)
            warnings.simplefilter('ignore', RuntimeWarning)
            warnings.simplefilter('ignore', UserWarning)
            warnings.simplefilter('ignore', FutureWarning)
            warnings.simplefilter('ignore', sklearn.exceptions.UndefinedMetricWarning)

        module_path = self.automl_settings.data_script
        if self.automl_settings.data_script is not None:
            if not os.path.exists(self.automl_settings.data_script) and self.automl_settings.path is not None:
                script_path = os.path.join(
                    self.automl_settings.path, self.automl_settings.data_script)
                if os.path.exists(script_path):
                    module_path = script_path
                else:
                    raise DataException("Could not find data script with name '{0}' or '{1}'"
                                        .format(self.automl_settings.data_script, script_path))
            try:
                self.user_script = _load_user_script(module_path, self.logger)
                self.input_data = common_utilities.extract_user_data(self.user_script)
                training_utilities.auto_blacklist(self.input_data, self.automl_settings)
                if self.automl_settings.exclude_nan_labels:
                    self.input_data = common_utilities._y_nan_check(self.input_data)
            except ConfigException:
                raise
            except Exception:
                pass
        else:
            self.user_script = None

        # Set up clients to communicate with AML services
        self._jasmine_client = JasmineClient(self.experiment.workspace.service_context, experiment.name,
                                             host=self.automl_settings.service_url)
        self.experiment_client = ExperimentClient(self.experiment.workspace.service_context, experiment.name,
                                                  host=self.automl_settings.service_url)

        self.current_run = None     # type: Optional[AutoMLRun]

    def __del__(self):
        """Clean up AutoML loggers and close files."""
        try:
            logging_utilities.cleanup_log_map(self.automl_settings.debug_log,
                                              self.automl_settings.verbosity)

            if self._usage_telemetry is not None:
                self._usage_telemetry.stop()
        except Exception:
            # last chance, nothing can be done, so ignore any exception
            pass

    def cancel(self):
        """
        Cancel the ongoing local run.

        :return: None
        """
        self._status = constants.Status.Terminated

    def fit(self,
            run_configuration: Optional[RunConfiguration] = None,
            compute_target: Optional[AbstractComputeTarget] = None,
            X: Optional[Any] = None,
            y: Optional[Any] = None,
            sample_weight: Optional[Any] = None,
            X_valid: Optional[Any] = None,
            y_valid: Optional[Any] = None,
            sample_weight_valid: Optional[Any] = None,
            data: Optional[pd.DataFrame] = None,
            label: Optional[str] = None,
            columns: Optional[List[str]] = None,
            cv_splits_indices: Optional[List[Any]] = None,
            show_output: bool = False,
            existing_run: bool = False) -> AutoMLRun:
        """
        Start a new AutoML execution on the specified compute target.

        :param run_configuration: The run confiuguration used by AutoML, should contain a compute target for remote
        :type run_configuration: Azureml.core RunConfiguration
        :param compute_target: The AzureML compute node to run this experiment on
        :type compute_target: azureml.core.compute.AbstractComputeTarget
        :param X: Training features
        :type X: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow or
                 azureml.core.Dataset, azureml.data.dataset_definition.DatasetDefinition
        :param y: Training labels
        :type y: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow or
                 azureml.core.Dataset, azureml.data.dataset_definition.DatasetDefinition
        :param sample_weight:
        :type sample_weight: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
        :param X_valid: validation features
        :type X_valid: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow or
                       azureml.core.Dataset, azureml.data.dataset_definition.DatasetDefinition
        :param y_valid: validation labels
        :type y_valid: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow or
                       azureml.core.Dataset, azureml.data.dataset_definition.DatasetDefinition
        :param sample_weight_valid: validation set sample weights
        :type sample_weight_valid: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
        :param data: Training features and label
        :type data: pandas.DataFrame
        :param label: Label column in data
        :type label: str
        :param columns: whitelist of columns in data to use as features
        :type columns: list(str)
        :param cv_splits_indices: Indices where to split training data for cross validation
        :type cv_splits_indices: list(int), or list(Dataflow) in which each Dataflow represent a train-valid set
                                 where 1 indicates record for training and 0 indicates record for validation
        :param show_output: Flag whether to print output to console
        :type show_output: bool
        :param existing_run: Flag whether this is a continuation of a previously completed experiment
        :type existing_run: bool
        :return: AutoML parent run
        :rtype: azureml.train.automl.AutoMLRun
        """
        self._status = constants.Status.Started

        if show_output:
            self._console_logger = sys.stdout

        if run_configuration is None:
            run_configuration = RunConfiguration()
            if compute_target is not None:
                run_configuration.name = compute_target.name
                self._console_logger.write('No run_configuration provided, running on {0} with default configuration\n'
                                           .format(compute_target.name))
            else:
                self._console_logger.write(
                    'No run_configuration provided, running locally with default configuration\n')

        if run_configuration.framework.lower() != 'python':
            raise ConfigException('AutoML requires the run configuration framework to be set to "Python".')

        self.automl_settings.compute_target = run_configuration.target

        X, y, X_valid, y_valid = dataset_utilities.convert_inputs(X, y, X_valid, y_valid)

        if self.automl_settings.spark_context:
            self._init_adb_driver_run(run_configuration=run_configuration, X=X, y=y, sample_weight=sample_weight,
                                      X_valid=X_valid, y_valid=y_valid, sample_weight_valid=sample_weight_valid,
                                      cv_splits_indices=cv_splits_indices, show_output=show_output)
        elif run_configuration.target == 'local':
            if self.automl_settings.path is None:
                self.automl_settings.path = '.'
            name = run_configuration._name if run_configuration._name else "local"
            run_configuration.save(self.automl_settings.path, name)
            self._console_logger.write('Running on local machine\n')
            self._fit_local(X=X, y=y, sample_weight=sample_weight, X_valid=X_valid, y_valid=y_valid,
                            data=data, label=label, columns=columns, cv_splits_indices=cv_splits_indices,
                            existing_run=existing_run, sample_weight_valid=sample_weight_valid)
        else:
            if self.automl_settings.enable_onnx_compatible_models:
                raise ValueError('ONNX models is not enabled on remote compute target, '
                                 'please use local compute target to run.')

            self._console_logger.write('Running on remote compute: ' + str(run_configuration.target) + '\n')
            self._fit_remote(run_configuration, X=X, y=y, sample_weight=sample_weight,
                             X_valid=X_valid, y_valid=y_valid, sample_weight_valid=sample_weight_valid,
                             cv_splits_indices=cv_splits_indices, show_output=show_output)
        assert self.current_run is not None
        return self.current_run

    def _init_adb_driver_run(self,
                             run_configuration=None,
                             X=None,
                             y=None,
                             sample_weight=None,
                             X_valid=None,
                             y_valid=None,
                             sample_weight_valid=None,
                             cv_splits_indices=None,
                             show_output=False,
                             existing_run=False):

        self._console_logger.write(
            'Running on ADB cluster experiment {0}.\n'.format(self.automl_settings.name))

        # Forecasting runs will fail if caching is turned off (ADB only)
        if self.automl_settings.is_timeseries and not self.automl_settings.enable_cache:
            raise ConfigException(
                'Time-series forecasting requires `enable_cache=True` on Databricks.')

        try:
            if not existing_run:
                self._fit_remote_core(run_configuration, X=X, y=y, sample_weight=sample_weight, X_valid=X_valid,
                                      y_valid=y_valid, sample_weight_valid=sample_weight_valid,
                                      cv_splits_indices=cv_splits_indices)
            # This should be refactored to have RunHistoryClient and make call on it to get token
            token_res = self.experiment_client._client.run.\
                get_token(experiment_name=self.automl_settings.name,
                          resource_group_name=self.automl_settings.resource_group,
                          subscription_id=self.automl_settings.subscription_id,
                          workspace_name=self.automl_settings.workspace_name,
                          run_id=self.current_run.run_id)
            aml_token = token_res.token
            aml_token_expiry = token_res.expiry_time_utc

            service_context = ServiceContext(
                subscription_id=self.automl_settings.subscription_id,
                resource_group_name=self.automl_settings.resource_group,
                workspace_name=self.automl_settings.workspace_name,
                workspace_id=self.experiment.workspace._workspace_id,
                authentication=self.experiment.workspace._auth_object)

            run_history_url = service_context._get_run_history_url()
            fn_script = None
            if self.automl_settings.data_script:
                with open(self.automl_settings.data_script, "r") as f:
                    fn_script = f.read()

            dataprep_json = dataprep_utilities.get_dataprep_json(
                X=X,
                y=y,
                sample_weight=sample_weight,
                X_valid=X_valid,
                y_valid=y_valid,
                sample_weight_valid=sample_weight_valid,
                cv_splits_indices=cv_splits_indices)
            # build dictionary of context
            run_context = {"subscription_id": self.automl_settings.subscription_id,
                           "resource_group": self.automl_settings.resource_group,
                           "location": self.experiment.workspace.location,
                           "workspace_name": self.automl_settings.workspace_name,
                           "experiment_name": self.automl_settings.name,
                           "parent_run_id": self.current_run.run_id,
                           "aml_token": aml_token,
                           "aml_token_expiry": aml_token_expiry,
                           "service_url": run_history_url,
                           "automl_settings_str": json.dumps(self.automl_settings._as_serializable_dict()),
                           'dataprep_json': dataprep_json,
                           "get_data_content": fn_script}
            adb_automl_context = [(index, run_context) for index in range(
                0, self.automl_settings.max_concurrent_iterations)]

            if not hasattr(self.automl_settings, 'is_run_from_test'):
                adb_thread = _AdbDriverNode("ADB Experiment: {0}".format(self.experiment.name),
                                            adb_automl_context,
                                            self.automl_settings.spark_context,
                                            self.automl_settings.max_concurrent_iterations,
                                            self.current_run.run_id)
                adb_thread.start()
                self.current_run = AutoMLADBRun(self.experiment, self.parent_run_id, adb_thread)
            else:
                automlRDD = self.automl_settings.\
                    spark_context.parallelize(adb_automl_context,
                                              self.automl_settings.max_concurrent_iterations)
                automlRDD.map(adb_run_experiment).collect()

            if show_output:
                RemoteConsoleInterface._show_output(self.current_run,
                                                    self._console_logger,
                                                    self.logger,
                                                    self.automl_settings.primary_metric)
        except Exception as ex:
            logging_utilities.log_traceback(ex, self.logger)
            raise

    def _create_parent_run(self, X=None, y=None, sample_weight=None, X_valid=None, y_valid=None,
                           sample_weight_valid=None, data=None, label=None, columns=None, cv_splits_indices=None,
                           existing_run=False):
        """
        Create parent run in Run History containing AutoML experiment information.

        :return: AutoML parent run
        :rtype: azureml.train.automl.AutoMLRun
        """
        #  Prepare data before entering for loop
        self.logger.info("Extracting user Data")
        self.input_data = training_utilities.format_training_data(X, y, sample_weight, X_valid, y_valid,
                                                                  sample_weight_valid, data, label, columns,
                                                                  cv_splits_indices, self.user_script,
                                                                  automl_settings=self.automl_settings,
                                                                  logger=self.logger, is_adb_run=True)

        training_utilities.validate_training_data_dict(self.input_data, self.automl_settings)
        training_utilities.auto_blacklist(self.input_data, self.automl_settings)
        if self.automl_settings.exclude_nan_labels:
            self.input_data = common_utilities._y_nan_check(self.input_data)
        training_utilities.set_task_parameters(self.input_data.get('y'), self.automl_settings)

        if not existing_run:
            # min to sec conversion
            timeout = None
            if self.automl_settings.iteration_timeout_minutes:
                timeout = self.automl_settings.iteration_timeout_minutes * 60

            # Call Jasmine to create experiment and parent run history entries
            parent_run_dto = CreateParentRunDto(target=constants.ComputeTargets.LOCAL,
                                                num_iterations=self.automl_settings.iterations,
                                                training_type=None,  # use self.training_type when jasmine supports it
                                                acquisition_function=None,
                                                metrics=['accuracy'],
                                                primary_metric=self.automl_settings.primary_metric,
                                                train_split=self.automl_settings.validation_size,
                                                max_time_seconds=timeout,
                                                acquisition_parameter=0.0,
                                                num_cross_validation=self.automl_settings.n_cross_validations,
                                                raw_aml_settings_string=str(
                                                    self.automl_settings._as_serializable_dict()),
                                                aml_settings_json_string=json.dumps(
                                                    self.automl_settings._as_serializable_dict()),
                                                enable_subsampling=self.automl_settings.enable_subsampling)
            try:
                self.logger.info("Start creating parent run with DTO: {0}."
                                 .format(self.automl_settings._format_selective(BLACKLISTED_LOGGING_KEYS)))
                self.parent_run_id = self._jasmine_client.post_parent_run(parent_run_dto)
                self.logger.update_default_property('parent_run_id', self.parent_run_id)
            except (AzureMLServiceException, HttpOperationError) as e:
                logging_utilities.log_traceback(e, self.logger)
                friendly_http_exception(e, constants.API.CreateParentRun)
            except Exception as e:
                logging_utilities.log_traceback(e, self.logger)
                raise ClientException(
                    "Error when trying to create parent run in automl service") from None

            self.current_run = AutoMLRun(self.experiment,
                                         self.parent_run_id,
                                         host=self.automl_settings.service_url)
            # TODO: Remove with task 416022
            self._add_display_task()
            # only log user sdk dependencies on initial parent creation
            log_user_sdk_dependencies(self.current_run, self.logger)

        else:
            self.current_run = AutoMLRun(self.experiment,
                                         self.parent_run_id,
                                         host=self.automl_settings.service_url)

        if self.user_script:
            self.logger.info("[ParentRunID:{}] Local run using user script.".format(self.parent_run_id))
        else:
            self.logger.info("[ParentRunID:{}] Local run using input X and y.".format(self.parent_run_id))

        self._console_logger.write("Parent Run ID: {}\n".format(self.parent_run_id))
        self.logger.info("Parent Run ID: " + self.parent_run_id)

        self._status = constants.Status.InProgress

        self._log_data_stat(self.input_data.get("X"), 'X', prefix="[ParentRunId:{}]".format(self.parent_run_id))
        self._log_data_stat(self.input_data.get("y"), 'y', prefix="[ParentRunId:{}]".format(self.parent_run_id))
        dataset_utilities.log_dataset("X", X, self.current_run)
        dataset_utilities.log_dataset("y", y, self.current_run)
        dataset_utilities.log_dataset("X_valid", X_valid, self.current_run)
        dataset_utilities.log_dataset("y_valid", y_valid, self.current_run)

    def _get_transformed_context(self, experiment_observer):
        with log_activity(logger=self.logger, activity_name=TelemetryConstants.PRE_PROCESS_NAME):
            if self.input_data.get("X_valid") is not None:
                self._log_data_stat(
                    self.input_data.get("X_valid"), 'X_valid', prefix="[ParentRunId:{}]".format(self.parent_run_id)
                )
            if self.input_data.get("y_valid") is not None:
                self._log_data_stat(
                    self.input_data.get("y_valid"), 'y_valid', prefix="[ParentRunId:{}]".format(self.parent_run_id)
                )

            raw_data_context = RawDataContext(task_type=self.automl_settings.task_type,
                                              X=self.input_data.get("X"),
                                              y=self.input_data.get("y"),
                                              X_valid=self.input_data.get("X_valid"),
                                              y_valid=self.input_data.get("y_valid"),
                                              sample_weight=self.input_data.get("sample_weight"),
                                              sample_weight_valid=self.input_data.get("sample_weight_valid"),
                                              x_raw_column_names=self.input_data.get("x_raw_column_names"),
                                              preprocess=self.automl_settings.preprocess,
                                              lag_length=self.automl_settings.lag_length,
                                              cv_splits_indices=self.input_data.get("cv_splits_indices"),
                                              automl_settings_obj=self.automl_settings)

            cache_store = CacheStoreFactory.get_cache_store(enable_cache=self.automl_settings.enable_cache,
                                                            run_id=self.parent_run_id, logger=self.logger)
            transformed_data_context = data_transformation.transform_data(
                raw_data_context=raw_data_context,
                experiment_observer=experiment_observer,
                logger=self.logger,
                cache_store=cache_store,
                is_onnx_compatible=self.automl_settings.enable_onnx_compatible_models,
                enable_feature_sweeping=self.automl_settings.enable_feature_sweeping)

            return transformed_data_context

    def _fit_local(self, X=None, y=None, sample_weight=None, X_valid=None, y_valid=None, sample_weight_valid=None,
                   data=None, label=None, columns=None, cv_splits_indices=None, existing_run=False):
        self._create_parent_run(X=X, y=y, sample_weight=sample_weight, X_valid=X_valid, y_valid=y_valid,
                                data=data, label=label, columns=columns,
                                cv_splits_indices=cv_splits_indices, existing_run=existing_run,
                                sample_weight_valid=sample_weight_valid)
        # Init the onnx converter with the original X.
        pkg_ver = _get_package_version()
        self.onnx_cvt = OnnxConverter(logger=self.logger,
                                      version=pkg_ver,
                                      is_onnx_compatible=self.automl_settings.enable_onnx_compatible_models)
        onnx_mdl_name = 'AutoML_ONNX_Model_[{}]'.format(self.parent_run_id)
        onnx_mdl_desc = {
            'ParentRunId': self.parent_run_id
        }
        self.onnx_cvt.initialize_input(X=self.input_data.get("X"),
                                       x_raw_column_names=self.input_data.get("x_raw_column_names"),
                                       model_name=onnx_mdl_name,
                                       model_desc=onnx_mdl_desc)

        experiment_observer = AzureExperimentObserver(self.current_run, self._console_logger, self.logger)
        transformed_data_context = self._get_transformed_context(experiment_observer)

        if not existing_run:
            self._jasmine_client.set_parent_run_status(
                self.parent_run_id, constants.RunState.START_RUN)

            # set the problem info, so the JOS can use it to get pipelines.
            automl._set_problem_info(transformed_data_context.X, transformed_data_context.y,
                                     self.automl_settings.task_type,
                                     current_run=self.current_run,
                                     preprocess=self.automl_settings.preprocess,
                                     lag_length=self.automl_settings.lag_length,
                                     transformed_data_context=transformed_data_context,
                                     enable_cache=self.automl_settings.enable_cache,
                                     subsampling=self.automl_settings.enable_subsampling,
                                     is_onnx_compatible=self.automl_settings.enable_onnx_compatible_models,
                                     logger=self.logger)

        subsampling = self.current_run._get_problem_info_dict().get('subsampling', False)

        try:
            #  Set up interface to print execution progress
            ci = ConsoleInterface("score", self._console_logger, mask_sampling=not subsampling)
        except Exception as e:
            logging_utilities.log_traceback(e, self.logger)
            raise

        self.experiment_start_time = datetime.utcnow()

        experiment_observer.report_status(ExperimentStatus.ModelSelection, "Beginning model selection.")
        ci.print_descriptions()
        ci.print_columns()
        if existing_run:
            self.current_iter = len(
                list(self.current_run.get_children(_rehydrate_runs=False)))
        else:
            self.current_iter = 0
        try:
            self.logger.info("Start local loop.")

            while self.current_iter < self.automl_settings.iterations:
                self.logger.info("Start iteration: {0}".format(self.current_iter))
                if self._status == constants.Status.Terminated:
                    self._console_logger.write(
                        "Stopping criteria reached at iteration {0}. Ending experiment.".format(self.current_iter - 1))
                    self.logger.info(
                        "Stopping criteria reached at iteration {0}. Ending experiment.".format(self.current_iter - 1))
                    self._jasmine_client.set_parent_run_status(self.parent_run_id, constants.RunState.COMPLETE_RUN)
                    return AutoMLRun(self.experiment, self.parent_run_id, host=self.automl_settings.service_url)
                with log_activity(logger=self.logger, activity_name=TelemetryConstants.FIT_ITERATION_NAME):
                    self._fit_iteration(ci,
                                        transformed_data_context=transformed_data_context)

            self._status = constants.Status.Completed
        except KeyboardInterrupt:
            self._status = constants.Status.Terminated
            self.logger.info(
                "[ParentRunId:{}]Received interrupt. Returning now.".format(self.parent_run_id))
            self._console_logger.write("Received interrupt. Returning now.")
            self._jasmine_client.set_parent_run_status(self.parent_run_id, constants.RunState.CANCEL_RUN)
        finally:
            # turn off system usage collection on run completion or failure
            if self._usage_telemetry is not None:
                self._usage_telemetry.stop()
            if not existing_run and self._status != constants.Status.Terminated:
                self._jasmine_client.set_parent_run_status(
                    self.parent_run_id, constants.RunState.COMPLETE_RUN)
            # cleanup transformed, preprocessed data cache
            if transformed_data_context is not None:
                transformed_data_context.cleanup()

        self.logger.info("Run Complete.")

    def _fit_iteration(self, ci, transformed_data_context=None):
        start_iter_time = datetime.utcnow()

        #  Query Jasmine for the next set of pipelines to run
        task_dto = self._get_task()

        if task_dto.is_experiment_over:
            self.logger.info("Complete task received. Completing experiment")
            self.cancel()
            return

        run_id = task_dto.childrun_id
        self.logger.update_default_property("child_run_id", run_id)

        pipeline_id = task_dto.pipeline_id
        pipeline_script = task_dto.pipeline_spec
        train_frac = float(task_dto.training_percent or 100) / 100

        """
        # TODO: Fix pipeline spec logging (#438111)
        self.logger.info(
            "Received pipeline: {0}".format(
                logging_utilities.remove_blacklisted_logging_keys_from_json_str(
                    pipeline_script
                )
            )
        )
        """
        self.logger.info('Received pipeline ID {}'.format(pipeline_id))

        ci.print_start(self.current_iter)
        errors = []
        child_run_metrics = None
        try:
            child_run = Run(self.experiment, run_id)
            # get total run time in seconds and convert to minutes
            elapsed_time = math.floor(int((datetime.utcnow() - self.experiment_start_time).total_seconds()) / 60)
            child_run.start()

            automl_run_context = AzureAutoMLRunContext(child_run)
            automl_pipeline = AutoMLPipeline(automl_run_context, pipeline_script, pipeline_id, train_frac)

            # copy the Run information to environment variables
            # this allows the child process that we spawn to be able to reconstruct the run object.
            self._set_environment_variables_for_reconstructing_run(child_run)

            fit_output = fit_pipeline_helper.fit_pipeline(
                automl_pipeline=automl_pipeline,
                automl_settings=self.automl_settings,
                automl_run_context=automl_run_context,
                remote=False,
                logger=self.logger,
                transformed_data_context=transformed_data_context,
                elapsed_time=elapsed_time,
                onnx_cvt=self.onnx_cvt)

            if fit_output.errors:
                err_type = next(iter(fit_output.errors))
                exception_info = fit_output.errors[err_type]
                exception_obj = cast(BaseException, exception_info['exception'])
                if err_type == 'model_explanation' and isinstance(exception_obj, ImportError):
                    errors.append('Could not explain model due to missing dependency. Please run: pip install '
                                  'azureml-sdk[explain]')
                elif isinstance(exception_obj, TimeoutException):
                    errors.append('Fit operation exceeded provided timeout, terminating and moving onto the next '
                                  'iteration. Please consider increasing the iteration_timeout_minutes parameter.')
                else:
                    errors.append('Run {} failed with exception "{}".'.format(run_id, str(exception_obj)))

            score = fit_output.score
            preprocessor = fit_output.run_preprocessor
            model_name = fit_output.run_algorithm
        except Exception as e:
            logging_utilities.log_traceback(e, self.logger)
            score = constants.Defaults.DEFAULT_PIPELINE_SCORE
            preprocessor = ''
            model_name = ''
            errors.append('Run {} failed with exception "{}".'.format(run_id, str(e)))

        ci.print_pipeline(preprocessor, model_name, train_frac)
        self._update_internal_scores_after_iteration(score)

        end_iter_time = datetime.utcnow()
        end_iter_time = end_iter_time.replace(tzinfo=pytz.UTC)
        start_iter_time = start_iter_time.replace(tzinfo=pytz.UTC)
        if child_run_metrics is not None:
            created_time = child_run_metrics._run_dto['created_utc']
            if isinstance(created_time, str):
                created_time = datetime.strptime(created_time, '%Y-%m-%dT%H:%M:%S.%fZ')
            start_iter_time = created_time.replace(tzinfo=pytz.UTC)
            details = child_run_metrics.get_details()
            if 'endTimeUtc' in details:
                end_iter_time = datetime.strptime(details['endTimeUtc'],
                                                  '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=pytz.UTC)
        iter_duration = str(end_iter_time - start_iter_time).split(".")[0]

        ci.print_end(iter_duration, score, self._score_best)
        self.current_iter = self.current_iter + 1

        for error in errors:
            ci.print_error(error)

    def _fit_remote(self, run_configuration, X=None, y=None, sample_weight=None, X_valid=None, y_valid=None,
                    sample_weight_valid=None, cv_splits_indices=None, show_output=False):

        self._fit_remote_core(run_configuration, X=X, y=y, sample_weight=sample_weight, X_valid=X_valid,
                              y_valid=y_valid, sample_weight_valid=sample_weight_valid,
                              cv_splits_indices=cv_splits_indices)
        if show_output:
            RemoteConsoleInterface._show_output(self.current_run,
                                                self._console_logger,
                                                self.logger,
                                                self.automl_settings.primary_metric)

    def _fit_remote_core(self, run_configuration, X=None, y=None, sample_weight=None, X_valid=None, y_valid=None,
                         sample_weight_valid=None, cv_splits_indices=None):
        if isinstance(run_configuration, str):
            run_config_object = RunConfiguration.load(
                self.automl_settings.path, run_configuration)
        else:
            # we alread have a run configuration object
            run_config_object = run_configuration
            run_configuration = run_config_object.target

        run_config_object = modify_run_configuration(self.automl_settings, run_config_object, self.logger)

        dataprep_json = dataprep_utilities.get_dataprep_json(X=X, y=y,
                                                             sample_weight=sample_weight,
                                                             X_valid=X_valid,
                                                             y_valid=y_valid,
                                                             sample_weight_valid=sample_weight_valid,
                                                             cv_splits_indices=cv_splits_indices)
        if dataprep_json is not None:
            # escape quotations in json_str before sending to jasmine
            dataprep_json = dataprep_json.replace('\\', '\\\\').replace('"', '\\"')

        # min to sec conversion
        timeout = None
        if self.automl_settings.iteration_timeout_minutes:
            timeout = self.automl_settings.iteration_timeout_minutes * 60
        parent_run_dto = CreateParentRunDto(target=run_configuration,
                                            num_iterations=self.automl_settings.iterations,
                                            training_type=None,  # use self.training_type when jasmine supports it
                                            acquisition_function=None,
                                            metrics=['accuracy'],
                                            primary_metric=self.automl_settings.primary_metric,
                                            train_split=self.automl_settings.validation_size,
                                            max_time_seconds=timeout,
                                            acquisition_parameter=0.0,
                                            num_cross_validation=self.automl_settings.n_cross_validations,
                                            raw_aml_settings_string=str(
                                                self.automl_settings._as_serializable_dict()),
                                            aml_settings_json_string=json.dumps(
                                                self.automl_settings._as_serializable_dict()),
                                            data_prep_json_string=dataprep_json,
                                            enable_subsampling=self.automl_settings.enable_subsampling)

        try:
            self.logger.info(
                "Start creating parent run with DTO: {0}.".format(
                    self.automl_settings._format_selective(BLACKLISTED_LOGGING_KEYS)))
            self.parent_run_id = self._jasmine_client.post_parent_run(
                parent_run_dto)
        except (AzureMLServiceException, HttpOperationError) as e:
            logging_utilities.log_traceback(e, self.logger)
            friendly_http_exception(e, constants.API.CreateParentRun)
        except Exception as e:
            logging_utilities.log_traceback(e, self.logger)
            raise ClientException(
                "Error occurred when trying to create new parent run in AutoML service.") from None

        if self.user_script:
            self.logger.info(
                "[ParentRunID:{}] Remote run using user script.".format(self.parent_run_id))
        else:
            self.logger.info(
                "[ParentRunID:{}] Remote run using input X and y.".format(self.parent_run_id))

        if self.current_run is None:
            self.current_run = AutoMLRun(self.experiment, self.parent_run_id, host=self.automl_settings.service_url)

        # TODO: Remove with task 416022
        self._add_display_task()
        log_user_sdk_dependencies(self.current_run, self.logger)

        self._console_logger.write("Parent Run ID: " + self.parent_run_id)
        self.logger.info("Parent Run ID: " + self.parent_run_id)

        snapshotId = ""
        if self.automl_settings.path is not None:
            snapshotId = self.current_run.take_snapshot(self.automl_settings.path)
        self.logger.info("Snapshotted folder: {0} with snapshot_id: {1}".format(
            self.automl_settings.path, snapshotId))

        definition = {
            "Configuration": _serialize_to_dict(run_config_object)
        }

        # BUG: 287204
        del definition["Configuration"]["environment"]["python"]["condaDependenciesFile"]
        definition["Configuration"]["environment"]["python"]["condaDependencies"] = \
            run_config_object.environment.python.conda_dependencies._conda_dependencies

        self.logger.info("Starting a snapshot run (snapshotId : {0})".format(snapshotId))
        try:
            self._jasmine_client.post_remote_jasmine_snapshot_run(self.parent_run_id,
                                                                  json.dumps(definition),
                                                                  snapshotId)
        except (AzureMLServiceException, HttpOperationError) as e:
            logging_utilities.log_traceback(e, self.logger)
            friendly_http_exception(e, constants.API.StartRemoteSnapshotRun)
        except Exception as e:
            logging_utilities.log_traceback(e, self.logger)
            raise ClientException("Error occurred when trying to submit a remote run to AutoML Service.") \
                from None

    def _get_task(self):
        """
        Query Jasmine for the next task.

        :return: dto containing task details
        """
        with log_activity(logger=self.logger, activity_name=TelemetryConstants.GET_PIPELINE_NAME):
            try:
                self.logger.info("Querying Jasmine for next task.")
                return self._jasmine_client.get_next_task(self.parent_run_id)
            except (AzureMLServiceException, HttpOperationError) as e:
                logging_utilities.log_traceback(e, self.logger)
                friendly_http_exception(e, constants.API.GetNextPipeline)
            except Exception as e:
                logging_utilities.log_traceback(e, self.logger)
                raise ServiceException("Error occurred when trying to fetch next iteration from AutoML service.") \
                    from None

    def _check_create_folders(self, path):
        if path is None:
            path = os.getcwd()
        # Expand out the path because os.makedirs can't handle '..' properly
        aml_config_path = os.path.abspath(os.path.join(path, '.azureml'))
        os.makedirs(aml_config_path, exist_ok=True)

    def _update_internal_scores_after_iteration(self, score):
        if self._score_max is None or np.isnan(self._score_max) or score > self._score_max:
            self._score_max = score
        if self._score_min is None or np.isnan(self._score_min) or score < self._score_min:
            self._score_min = score

        if self.automl_settings.metric_operation == constants.OptimizerObjectives.MINIMIZE:
            self._score_best = self._score_min
        elif self.automl_settings.metric_operation == constants.OptimizerObjectives.MAXIMIZE:
            self._score_best = self._score_max

    def _log_data_stat(self, data, data_name, prefix=None):
        if prefix is None:
            prefix = ""
        if type(data) is not np.ndarray and type(data) is not np.array and type(data) is not pd.DataFrame:
            try:
                data = data.to_pandas_dataframe()
            except AttributeError:
                self.logger.warning("The data type is not supported for logging.")
                return
        self.logger.info(
            "{}Input {} datatype is {}, shape is {}, datasize is {}.".format(
                prefix, data_name, type(data), data.shape,
                memory_utilities.get_data_memory_size(data)
            )
        )

    def _add_display_task(self) -> None:
        """Add display task property."""
        task = self.automl_settings.task_type
        if self.automl_settings.is_timeseries:
            task = constants.Tasks.FORECASTING
        # This property is to temporarily fix: 362194.
        # It should be removed promptly.
        assert self.current_run is not None
        self.current_run.add_properties({'display_task_type': task})

    @staticmethod
    def _set_environment_variables_for_reconstructing_run(run):
        os.environ['AZUREML_ARM_SUBSCRIPTION'] = run.experiment.workspace.subscription_id
        os.environ["AZUREML_RUN_ID"] = run.id
        os.environ["AZUREML_ARM_RESOURCEGROUP"] = run.experiment.workspace.resource_group
        os.environ["AZUREML_ARM_WORKSPACE_NAME"] = run.experiment.workspace.name
        os.environ["AZUREML_ARM_PROJECT_NAME"] = run.experiment.name
        os.environ['AZUREML_RUN_TOKEN'] = run._client.run.get_token().token
        os.environ["AZUREML_SERVICE_ENDPOINT"] = run._client.run.get_cluster_url()

    @staticmethod
    def _is_tensorflow_module_present():
        try:
            return pipeline_spec.tf_wrappers.tf_found
        except Exception:
            return False

    @staticmethod
    def _is_xgboost_module_present():
        try:
            return model_wrappers.xgboost_present
        except Exception:
            return False
