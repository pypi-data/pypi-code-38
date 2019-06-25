# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Template-based implementation of AutoML training."""
from typing import Any, cast, List, Optional
from threading import Timer
import json
import warnings

import numpy as np
import pandas as pd
import scipy
import sklearn

from automl.client.core.common import constants
from automl.client.core.common import logging_utilities
from automl.client.core.common import utilities
from automl.client.core.common.activity_logger import Activities
from automl.client.core.common.limit_function_call_exceptions import TimeoutException
from . import data_transformation
from . import training_utilities
from .automl_job import AutoMLJob
from .automl_scenario import AutoMLScenario
from .automl_base_settings import AutoMLBaseSettings
from .data_context import RawDataContext
from .data_context import TransformedDataContext
from .systemusage_telemetry import SystemResourceUsageTelemetryFactory


class AutoMLReferenceClient:
    """Base client implementation that can be extended by providing a scenario object."""

    def __init__(self, scenario: AutoMLScenario, settings: AutoMLBaseSettings) -> None:
        """
        Create an AutoMLReferenceClient.

        :param scenario: the AutoML scenario object
        :param settings: the AutoML settings
        """
        self.scenario = scenario
        self.settings = settings
        self.current_job = None   # type: Optional[AutoMLJob]
        self.usage_telemetry = SystemResourceUsageTelemetryFactory.get_system_usage_telemetry(
            self.scenario.get_logger(self.settings))

        if not self.settings.show_warnings:
            warnings.simplefilter('ignore', DeprecationWarning)
            warnings.simplefilter('ignore', RuntimeWarning)
            warnings.simplefilter('ignore', UserWarning)
            warnings.simplefilter('ignore', FutureWarning)
            warnings.simplefilter('ignore', sklearn.exceptions.UndefinedMetricWarning)

    def fit_params(
            self,
            X: Any = None,
            y: Any = None,
            sample_weight: Optional[Any] = None,
            X_valid: Optional[Any] = None,
            y_valid: Optional[Any] = None,
            sample_weight_valid: Optional[Any] = None,
            data: Optional[pd.DataFrame] = None,
            label: Optional[str] = None,
            columns: Optional[List[str]] = None,
            cv_splits_indices: Optional[np.ndarray] = None,
            user_script: Optional[str] = None) -> AutoMLJob:
        """
        Create a raw data context then call fit.

        :param X: Training features.
        :param y: Training labels.
        :param sample_weight: Sample weights for training data.
        :param X_valid: validation features.
        :param y_valid: validation labels.
        :param sample_weight_valid: validation set sample weights.
        :param data: Training features and label.
        :param label: Label column in data.
        :param columns: whitelist of columns in data to use as features.
        :param cv_splits_indices:
            Indices where to split training data for cross validation.
            Each row is a separate cross fold and within each crossfold, provide 2 arrays,
            the first with the indices for samples to use for training data and the second
            with the indices to use for validation data. i.e [[t1, v1], [t2, v2], ...]
            where t1 is the training indices for the first cross fold and v1 is the validation
            indices for the first cross fold.
        :param user_script: File path to script containing get_data()
        :return: the job object
        """
        # TODO: Clean this up
        # When data is ingested via dprep, we shouldn't convert to numpy arrays. So setting the
        # is_adb_run to True.
        input_data = training_utilities.format_training_data(X,
                                                             y,
                                                             sample_weight,
                                                             X_valid,
                                                             y_valid,
                                                             sample_weight_valid,
                                                             data,
                                                             label,
                                                             columns,
                                                             cv_splits_indices,
                                                             user_script,
                                                             is_adb_run=True,
                                                             automl_settings=self.settings,
                                                             logger=self.scenario.get_logger(self.settings))
        training_utilities.validate_training_data_dict(input_data, self.settings)
        training_utilities.auto_blacklist(input_data, self.settings)
        if self.settings.exclude_nan_labels:
            input_data = utilities._y_nan_check(input_data)
        training_utilities.set_task_parameters(y=input_data.get('y'),
                                               automl_settings=self.settings)

        timeseries_param_dict = utilities._get_ts_params_dict(self.settings)
        raw_data_context = RawDataContext(
            task_type=self.settings.task_type,
            X=input_data.get("X"),
            y=input_data.get("y"),
            X_valid=input_data.get("X_valid"),
            y_valid=input_data.get("y_valid"),
            sample_weight=input_data.get("sample_weight"),
            sample_weight_valid=input_data.get("sample_weight_valid"),
            x_raw_column_names=input_data.get("x_raw_column_names"),
            lag_length=self.settings.lag_length,
            cv_splits_indices=input_data.get("cv_splits_indices"),
            preprocess=self.settings.preprocess,
            validation_size=self.settings.validation_size,
            timeseries=self.settings.is_timeseries,
            timeseries_param_dict=timeseries_param_dict,
            num_cv_folds=self.settings.n_cross_validations)
        return self.fit(raw_data_context)

    def fit(self, raw_data_context: RawDataContext) -> AutoMLJob:
        """
        Run a model fitting job using the given data.

        :param raw_data_context: the raw data to be used for training
        :return: a job object containing metadata and results for all iterations
        """
        # TODO: Store dependencies (maybe should go in the scenario object instead of here)
        self.scenario.before_job_creation(self.settings)
        job = AutoMLJob(settings=self.settings,
                        parent_run_context=self.scenario.get_parent_run_context(self.settings),
                        logger=self.scenario.get_logger(self.settings))

        # We need to keep a reference to the job so we can cancel it
        self.current_job = job

        activity_logger = self.scenario.get_activity_logger(job.settings)
        transformed_data_context = None

        # Begin resource usage telemetry
        with self.usage_telemetry, activity_logger.log_activity(job.logger, Activities.Fit):
            try:
                # Setup the job
                job.start()

                transformed_data_context = self._job_setup(job, raw_data_context)

                # Training iterations
                job.status = constants.Status.InProgress
                self._start_timeout_timer(job)
                while job.remaining_iterations > 0:
                    with activity_logger.log_activity(job.logger, Activities.FitIteration):
                        self._fit_iteration(job, transformed_data_context)

                # Handle early exit (timeout, exit score, manually cancelled, etc)
                if not job.is_running:
                    job.logger.info('Stopping criteria reached. Ending experiment.')
                    self.scenario.on_exit_criteria_met(job)

                # Everything done!
                job.logger.info('Run complete.')
                job.complete()
                self.scenario.on_job_success(job)
            except KeyboardInterrupt:
                # Handle Ctrl+C when running locally
                job.logger.info('Received keyboard interrupt, ending now.')
                self.cancel()
            except Exception as e:
                # Handle errors raised during job execution
                job.terminate()
                logging_utilities.log_traceback(e, job.logger)
                self.scenario.on_job_failure(job, e)
            finally:
                if transformed_data_context:
                    transformed_data_context.cleanup()
                self.current_job = None

        return job

    def _fit_iteration(self, job: AutoMLJob, data_context: TransformedDataContext) -> None:
        """
        Run a training iteration. The result is saved to the job object.

        :param job: the job currently being run
        :param data_context: the preprocessed data to use
        :return: the training output
        """
        pipeline = self.scenario.get_pipeline(job)
        self.scenario.on_before_fit_iteration(job, pipeline)

        job.logger.info('Executing pipeline.')
        fit_output = self.scenario.execute_pipeline(job, pipeline, data_context)
        job.add_iteration(fit_output)

        # TODO: Make this better (expose multiple errors, don't stringly type) - task #366269
        if len(fit_output.errors) > 0:
            err_type = next(iter(fit_output.errors))
            exception_info = fit_output.errors[err_type]
            exception_obj = cast(BaseException, exception_info['exception'])
            if isinstance(exception_obj, TimeoutException):
                self.scenario.on_fit_iteration_timeout(job, fit_output)
            else:
                self.scenario.on_fit_iteration_error(job, fit_output, exception_obj)
        else:
            self.scenario.on_fit_iteration_success(job, fit_output)

    def _job_setup(self, job: AutoMLJob, raw_data_context: RawDataContext) -> TransformedDataContext:
        """
        Set up the job by validating and preprocessing data.

        :param job: the job currently being run
        :param raw_data_context: the raw data to use
        :return: preprocessed and validated data
        """
        self.scenario.on_before_job_setup(job, raw_data_context)
        activity_logger = self.scenario.get_activity_logger(job.settings)

        with activity_logger.log_activity(job.logger, Activities.Preprocess):
            self.scenario.on_before_preprocess(job, raw_data_context)

            cache_store = self.scenario.get_cache_store(job.settings)
            transformed_data_context = data_transformation.transform_data(
                raw_data_context=raw_data_context,
                preprocess=job.settings.preprocess,
                logger=job.logger,
                cache_store=cache_store,
                enable_feature_sweeping=job.settings.enable_feature_sweeping)

            self.scenario.on_after_preprocess(job, transformed_data_context)

        # Set problem info
        X = transformed_data_context.X
        num_samples = X.shape[0]
        subsampling = job.settings.enable_subsampling and utilities.subsampling_recommended(num_samples)
        problem_info_dict = {
            "dataset_num_categorical": 0,
            "dataset_classes": len(np.unique(transformed_data_context.y)),
            "dataset_features": X.shape[1],
            "dataset_samples": num_samples,
            "is_sparse": scipy.sparse.issparse(X),
            "subsampling": subsampling
        }
        with job.parent_run_context.get_run() as parent_run:
            parent_run.add_properties({'ProblemInfoJsonString': json.dumps(problem_info_dict)})

        self.scenario.on_after_job_setup(job, transformed_data_context)
        return transformed_data_context

    @staticmethod
    def _start_timeout_timer(job: AutoMLJob) -> None:
        """
        Start a timer that will automatically cancel the given job if it is still running after a timeout period.

        :param job: the job object to start a timer for
        """
        if job.settings.experiment_timeout_minutes is not None:
            # Construct a closure so we can cancel this particular job (in case fit is called again)
            def experiment_timeout():
                if job.is_running:
                    job.logger.info('Experiment timeout reached.')
                    job.terminate()
            timeout_timer = Timer(job.settings.experiment_timeout_minutes, experiment_timeout)
            timeout_timer.daemon = True
            timeout_timer.start()

    def cancel(self) -> None:
        """Cancel the currently running given job."""
        # Cancelling a job that is not running should do nothing
        if self.current_job is None or not self.current_job.is_running:
            return

        self.current_job.terminate()
        self.scenario.on_job_cancellation(self.current_job)
        self.current_job = None
