# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Scenario template class that provides hooks and placeholders for implementing AutoML in various contexts."""
from abc import ABC, abstractmethod
import logging
from automl.client.core.common.activity_logger import ActivityLogger
from .automl_job import AutoMLJob
from .automl_pipeline import AutoMLPipeline
from .automl_base_settings import AutoMLBaseSettings
from .automl_run_context import AutoMLAbstractRunContext
from .data_context import RawDataContext, TransformedDataContext
from .fit_output import FitOutput
from automl.client.core.common.cache_store import CacheStore


class AutoMLScenario(ABC):
    """
    Scenario template class that provides hooks and placeholders for implementing AutoML in various contexts.

    Note that scenarios are stateful objects, but the only state that should be maintained in them should be stuff
    that is scenario-specific (for example: console output interfaces, caching expensive objects, etc).
    """

    @abstractmethod
    def get_logger(self, settings: AutoMLBaseSettings) -> logging.Logger:
        """
        Get a logger object to be used for general logging.

        This function may be called more than once during a job's lifetime.

        :param settings: the job's settings
        :return: a logger object
        """
        raise NotImplementedError

    @abstractmethod
    def get_activity_logger(self, settings: AutoMLBaseSettings) -> ActivityLogger:
        """
        Get an activity logger object to be used for telemetry.

        This function may be called more than once during a job's lifetime.

        :param settings: the job's settings
        :return: an activity logger object
        """
        raise NotImplementedError

    @abstractmethod
    def get_cache_store(self, settings: AutoMLBaseSettings) -> CacheStore:
        """
        Get a cache store to be used for caching preprocessed data.

        This function may be called more than once during a job's lifetime.

        :param settings: the job's settings
        :return: a cache store object
        """
        raise NotImplementedError

    @abstractmethod
    def get_pipeline(self, job: AutoMLJob) -> AutoMLPipeline:
        """
        Fetch a new pipeline to execute for the given job.

        :param job: the currently executing job
        :return: a pipeline object
        """
        raise NotImplementedError

    @abstractmethod
    def get_parent_run_context(self, settings: AutoMLBaseSettings) -> AutoMLAbstractRunContext:
        """
        Get a parent run context to associate with a job.

        This function should only be called once during a job's lifetime.

        :param settings: the settings for the job
        :return: a run context wrapping a parent run
        """
        raise NotImplementedError

    @abstractmethod
    def execute_pipeline(self,
                         job: AutoMLJob,
                         pipeline: AutoMLPipeline,
                         data_context: TransformedDataContext) -> FitOutput:
        """
        Execute this pipeline (possibly using remote compute) and return the output from execution.

        :param job: the currently executing job
        :param pipeline: the pipeline to be executed
        :param data_context: the preprocessed and validated data to use during pipeline execution
        :return: the output from execution
        """
        raise NotImplementedError

    def before_job_creation(self, settings: AutoMLBaseSettings) -> None:
        """
        Perform actions before the job is created.

        :param settings: the settings for the job
        """
        pass

    def on_job_failure(self, job: AutoMLJob, error: BaseException) -> None:
        """
        Perform actions when the job fails.

        :param job: the job that failed
        :param error: the exception that was raised
        """
        pass

    def on_job_success(self, job: AutoMLJob) -> None:
        """
        Perform actions when the job succeeds.

        :param job: the job that succeeded
        """
        pass

    def on_job_cancellation(self, job: AutoMLJob) -> None:
        """
        Perform actions when the job is cancelled by the user.

        :param job: the job that was cancelled
        """
        pass

    def on_exit_criteria_met(self, job: AutoMLJob) -> None:
        """
        Perform actions when the job finishes early due to early stopping, exit score met, or other criteria.

        :param job: the job that succeeded early
        """
        pass

    def on_before_job_setup(self, job: AutoMLJob, data_context: RawDataContext) -> None:
        """
        Perform actions before job setup begins.

        :param job: the currently executing job
        :param data_context: the data before preprocessing
        """
        pass

    def on_after_job_setup(self, job: AutoMLJob, data_context: TransformedDataContext) -> None:
        """
        Perform actions after job setup finishes.

        :param job: the currently executing job
        :param data_context: the data after validation (and preprocessing, if enabled)
        """
        pass

    def on_before_preprocess(self, job: AutoMLJob, data_context: RawDataContext) -> None:
        """
        Perform actions before preprocessing occurs.

        This callback will not be fired if preprocessing is disabled.

        :param job: the currently executing job
        :param data_context: the data before preprocessing
        """
        pass

    def on_after_preprocess(self, job: AutoMLJob, transformed_data_context: TransformedDataContext) -> None:
        """
        Perform actions after preprocessing occurs.

        This callback will not be fired if preprocessing is disabled.

        :param job: the currently executing job
        :param transformed_data_context: the data after validation and preprocessing
        """
        pass

    def on_before_fit_iteration(self, job: AutoMLJob, pipeline: AutoMLPipeline) -> None:
        """
        Perform actions before a training iteration begins.

        :param job: the currently executing job
        :param pipeline: the pipeline to be executed
        """
        pass

    def on_fit_iteration_success(self, job: AutoMLJob, fit_output: FitOutput) -> None:
        """
        Perform actions after a training iteration finishes successfully.

        This callback will not be fired if the iteration fails.

        :param job: the currently executing job
        :param fit_output: the output from pipeline execution
        """
        pass

    def on_fit_iteration_error(self, job: AutoMLJob, fit_output: FitOutput, error: BaseException) -> None:
        """
        Perform actions when a training iteration fails.

        Note that there may have been more than one exception (see #366269); only the first one will be passed here.
        TODO: Pass all errors (see task 366269).

        :param job: the currently executing job
        :param fit_output: the output from pipeline execution
        :param error: the exception that was raised
        """
        pass

    def on_fit_iteration_timeout(self, job: AutoMLJob, fit_output: FitOutput) -> None:
        """
        Perform actions when a training iteration times out.

        :param job: the currently executing job
        :param fit_output: the output from pipeline execution
        """
        pass
