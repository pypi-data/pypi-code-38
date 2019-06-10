# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Manages settings for AutoML experiment."""
from typing import Any, Dict, Optional, Union
import logging

from automl.client.core.common import constants
from automl.client.core.common.exceptions import ConfigException
from azureml.automl.core.automl_base_settings import AutoMLBaseSettings

from azureml.core.compute import ComputeTarget, DatabricksCompute
from azureml.core.experiment import Experiment


class AzureAutoMLSettings(AutoMLBaseSettings):
    """Persist and validate settings for an AutoML experiment."""

    def __init__(self,
                 experiment=None,
                 path=None,
                 iterations=None,
                 data_script=None,
                 primary_metric=None,
                 task_type=None,
                 compute_target=None,
                 spark_context=None,
                 validation_size=None,
                 n_cross_validations=None,
                 y_min=None,
                 y_max=None,
                 num_classes=None,
                 preprocess=False,
                 lag_length=0,
                 max_cores_per_iteration=1,
                 max_concurrent_iterations=1,
                 iteration_timeout_minutes=None,
                 mem_in_mb=None,
                 enforce_time_on_windows=None,
                 experiment_timeout_minutes=None,
                 experiment_exit_score=None,
                 enable_early_stopping=False,
                 blacklist_models=None,
                 whitelist_models=None,
                 auto_blacklist=True,
                 exclude_nan_labels=True,
                 verbosity=logging.INFO,
                 debug_log='automl.log',
                 debug_flag=None,
                 enable_ensembling=True,
                 enable_stack_ensembling=True,
                 ensemble_iterations=None,
                 model_explainability=False,
                 enable_tf=True,
                 enable_cache=True,
                 enable_subsampling=None,
                 subsample_seed=None,
                 cost_mode=constants.PipelineCost.COST_NONE,
                 is_timeseries=False,
                 enable_onnx_compatible_models=False,
                 **kwargs):
        """
        Manage settings used by AutoML components.

        :param experiment: The azureml.core experiment
        :param path: Full path to the project folder
        :param iterations: Number of different pipelines to test
        :param data_script: File path to the script containing get_data()
        :param primary_metric: The metric that you want to optimize.
        :param task_type: Field describing whether this will be a classification or regression experiment
        :param compute_target: The AzureML compute to run the AutoML experiment on
        :param spark_context: Spark context, only applicable when used inside azure databricks/spark environment.
        :type spark_context: SparkContext
        :param validation_size: What percent of the data to hold out for validation
        :param n_cross_validations: How many cross validations to perform
        :param y_min: Minimum value of y for a regression experiment
        :param y_max: Maximum value of y for a regression experiment
        :param num_classes: Number of classes in the label data
        :param preprocess: Flag whether AutoML should preprocess your data for you
        :param lag_length: How many rows to lag data when preprocessing time series data
        :param max_cores_per_iteration: Maximum number of threads to use for a given iteration
        :param max_concurrent_iterations:
            Maximum number of iterations that would be executed in parallel.
            This should be less than the number of cores on the AzureML compute. Formerly concurrent_iterations.
        :param iteration_timeout_minutes: Maximum time in seconds that each iteration before it terminates
        :param mem_in_mb: Maximum memory usage of each iteration before it terminates
        :param enforce_time_on_windows: flag to enforce time limit on model training at each iteration under windows.
        :param experiment_timeout_minutes: Maximum amount of time that all iterations combined can take
        :param experiment_exit_score:
            Target score for experiment. Experiment will terminate after this score is reached.
        :param enable_early_stopping: flag to turn early stopping on when AutoML scores are not progressing.
        :param blacklist_models: List of algorithms to ignore for AutoML experiment
        :param whitelist_models: List of model names to search for AutoML experiment
        :param exclude_nan_labels: Flag whether to exclude rows with NaN values in the label
        :param auto_blacklist: Flag whether AutoML should try to exclude algorithms
            that it thinks won't perform well.
        :param verbosity: Verbosity level for AutoML log file
        :param debug_log: File path to AutoML logs
        :param enable_ensembling: Flag to enable/disable an extra iteration for model ensembling
        :param ensemble_iterations: Number of models to consider for the ensemble generation
        :param model_explainability: Flag whether to explain AutoML model
        :param enable_TF: Flag to enable/disable Tensorflow algorithms
        :param enable_cache: Flag to enable/disable disk cache for transformed, preprocessed data.
        :param enable_subsampling: Flag to enable/disable subsampling. Note that even if it's true,
            subsampling would not be enabled for small datasets or iterations.
        :param subsample_seed: random_state used to sample the data.
        :param cost_mode: Flag to set cost prediction modes. COST_NONE stands for none cost prediction,
            COST_FILTER stands for cost prediction per iteration.
        :type cost_mode: int or automl.client.core.common.constants.PipelineCost
        :param is_timeseries: Flag whether AutoML should process your data as time series data.
        :type is_timeseries: bool
        :param enable_onnx_compatible_models: Flag to enable/disable enforcing the onnx compatible models.
        :param kwargs:
        """
        if experiment is None:
            self.name = None
            self.path = None
            self.subscription_id = None
            self.resource_group = None
            self.workspace_name = None
            self.region = None
        else:
            # This is used in the remote case values are populated through AMLSettings
            self.name = experiment.name
            self.path = path
            self.subscription_id = experiment.workspace.subscription_id
            self.resource_group = experiment.workspace.resource_group
            self.workspace_name = experiment.workspace.name
            self.region = experiment.workspace.location
        self.compute_target = compute_target
        self.spark_context = spark_context
        self.spark_service = 'adb' if self.spark_context else None

        # if enable_subsampling is specified to be True or False, we do whatever the user wants
        # otherwise we will follow the following rules:
        #   off if iterations is specified
        #   off if it is timeseries
        #   otherwise we leave it for automl._subsampling_recommended() to decide
        #   based off num_samples and num_features after featurization stage
        if enable_subsampling is None:
            if iterations is not None or is_timeseries:
                enable_subsampling = False

        if iterations is None and experiment_timeout_minutes is None:
            enable_early_stopping = True

        if iterations is None:
            iterations = 1000

        if is_timeseries:
            # We are currently have diverged from common core AutoMLBaseSettings because
            # rolling window and lag-lead operator features are still under review.
            kwargs[constants.TimeSeries.TARGET_ROLLING_WINDOW_SIZE] = \
                kwargs.pop(constants.TimeSeries.TARGET_ROLLING_WINDOW_SIZE, None)
            kwargs[constants.TimeSeries.TARGET_LAGS] = kwargs.pop(constants.TimeSeries.TARGET_LAGS, None)

        # Set the rest of the instance variables and have base class verify settings
        super().__init__(
            path=path,
            iterations=iterations,
            data_script=data_script,
            primary_metric=primary_metric,
            task_type=task_type,
            compute_target=compute_target,
            validation_size=validation_size,
            n_cross_validations=n_cross_validations,
            y_min=y_min,
            y_max=y_max,
            num_classes=num_classes,
            preprocess=preprocess,
            lag_length=lag_length,
            max_cores_per_iteration=max_cores_per_iteration,
            max_concurrent_iterations=max_concurrent_iterations,
            iteration_timeout_minutes=iteration_timeout_minutes,
            mem_in_mb=mem_in_mb,
            enforce_time_on_windows=enforce_time_on_windows,
            experiment_timeout_minutes=experiment_timeout_minutes,
            experiment_exit_score=experiment_exit_score,
            enable_early_stopping=enable_early_stopping,
            blacklist_models=blacklist_models,
            whitelist_models=whitelist_models,
            auto_blacklist=auto_blacklist,
            exclude_nan_labels=exclude_nan_labels,
            verbosity=verbosity,
            debug_log=debug_log,
            debug_flag=debug_flag,
            enable_ensembling=enable_ensembling,
            enable_stack_ensembling=enable_stack_ensembling,
            ensemble_iterations=ensemble_iterations,
            model_explainability=model_explainability,
            enable_tf=enable_tf,
            enable_cache=enable_cache,
            enable_subsampling=False,
            subsample_seed=subsample_seed,
            cost_mode=cost_mode,
            is_timeseries=is_timeseries,
            enable_onnx_compatible_models=enable_onnx_compatible_models,
            **kwargs)

        # temporary measure to bypass the typecheck in base settings in common core
        # will remove once changes are in common core
        self.enable_subsampling = enable_subsampling

    def _verify_settings(self) -> None:
        """
        Verify that input automl_settings are sensible.

        TODO (#357763): Reorganize the checks here and in AutoMLConfig and see what's redundant/can be reworked.

        :return:
        :rtype: None
        """
        # Base settings object will do most of the verification. Only add AzureML-specific checks here.
        super()._verify_settings()
        if self.enable_onnx_compatible_models and self.spark_context:
            raise ValueError('ONNX models is not enabled on ADB yet, please use local compute target to run.')
        if self.compute_target is not None and not isinstance(self.compute_target, str) and \
                not isinstance(self.compute_target, ComputeTarget):
            raise ConfigException('Input parameter \"compute_target\" needs to be an AzureML compute target. '
                                  'Received \"{0}\". You may have intended to pass a run configuration, '
                                  'if so, please pass it as \"run_configuration=\'{1}\'\".'
                                  .format(type(self.compute_target), self.compute_target))

        if isinstance(self.compute_target, DatabricksCompute) or \
                (isinstance(self.compute_target, str) and self.compute_target.lower() == 'databricks'):
            raise ConfigException('Databricks compute cannot be directly attached for AutoML runs. Please pass in a '
                                  'spark context instead using the spark_context parameter and set compute_target to '
                                  '"local".')

    @staticmethod
    def from_string_or_dict(val: Union[str, Dict[str, Any], AutoMLBaseSettings],
                            experiment: Optional[Experiment] = None) -> 'AzureAutoMLSettings':
        """
        Convert a string or dictionary containing settings to an AzureAutoMLSettings object.

        If the provided value is already an AzureAutoMLSettings object, it is simply passed through.

        :param val: the input data to convert
        :param experiment: the experiment being run
        :return: an AzureAutoMLSettings object
        """
        if isinstance(val, str):
            val = eval(val)
        if isinstance(val, dict):
            val = AzureAutoMLSettings(experiment=experiment, **val)

        if isinstance(val, AzureAutoMLSettings):
            return val
        else:
            raise ValueError("`input` parameter is not of type string or dict")

    def as_serializable_dict(self) -> Dict[str, Any]:
        # This code is duplicated to mark this code as being used by an external package. Do not remove.
        return self._as_serializable_dict()
