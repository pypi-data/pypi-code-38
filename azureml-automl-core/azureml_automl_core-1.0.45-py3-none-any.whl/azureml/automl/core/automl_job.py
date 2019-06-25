# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Job class that encapsulates an AutoML job's state."""
from typing import List, Optional
from datetime import datetime
import logging

import numpy as np

from automl.client.core.common import constants
from automl.client.core.common import metrics
from automl.client.core.common.exceptions import ConfigException, DataException
from .automl_base_settings import AutoMLBaseSettings
from .automl_run_context import AutoMLAbstractRunContext
from .fit_output import FitOutput


class AutoMLJob:
    """Job class that encapsulates an AutoML job's state."""

    def __init__(self,
                 settings: AutoMLBaseSettings,
                 parent_run_context: AutoMLAbstractRunContext,
                 logger: Optional[logging.Logger] = None) -> None:
        """
        Create an AutoMLJob object.

        :param settings: the settings to use for this job
        :param parent_run_context: the parent run context for this job
        :param logger: the logger to use for this job
        """
        self.settings = settings
        self.outputs = []                                       # type: List[FitOutput]
        self._current_iteration = 0                             # type: int
        self.status = constants.Status.NotStarted               # type: str
        self.start_time = None                                  # type: Optional[datetime]
        self.end_time = None                                    # type: Optional[datetime]
        self.best_output = None                                 # type: Optional[FitOutput]
        self.logger = logger or logging.getLogger(__name__)     # type: logging.Logger
        self.parent_run_context = parent_run_context

    def add_iteration(self, output: FitOutput) -> None:
        """
        Add the results of a job iteration.

        :param output:
        """
        self.outputs.append(output)
        self._select_best_output(output)

        self._current_iteration += 1

        if self.settings.experiment_exit_score is not None:
            if self.settings.metric_operation == constants.OptimizerObjectives.MINIMIZE:
                if output.score < self.settings.experiment_exit_score:
                    self.terminate()
            elif self.settings.metric_operation == constants.OptimizerObjectives.MAXIMIZE:
                if output.score > self.settings.experiment_exit_score:
                    self.terminate()

        if self.settings.iterations <= self._current_iteration:
            self.terminate()

    def start(self) -> None:
        """Mark this job as started."""
        self.status = constants.Status.Started
        self.start_time = datetime.utcnow()

    def complete(self) -> None:
        """Mark this job as completed."""
        self.end_time = datetime.utcnow()
        self.status = constants.Status.Completed

    def terminate(self) -> None:
        """Mark this job as terminated early (cancelled, exit criteria met, etc)."""
        self.end_time = datetime.utcnow()
        self.status = constants.Status.Terminated

    def get_fit_output(self, iteration: Optional[int] = None, metric: Optional[str] = None) -> FitOutput:
        """
        Retrieve the best pipeline output tested so far.

        :param iteration: The iteration number of the correspond pipeline spec and fitted model to return.
        :param metric: The metric to use to return the best pipeline spec and fitted model to return.
        :return: the output meeting the above criteria
        """
        if iteration and metric:
            raise ConfigException('Cannot specify both metric and iteration to register.')

        if iteration is not None:
            total_runs = len(self.outputs)

            if not isinstance(iteration, int) or iteration >= total_runs \
                    or iteration < 0:
                raise ConfigException("Invalid iteration {2}. Run {0} has {1} iterations."
                                      .format(self.parent_run_context.run_id, total_runs, iteration))

            best_output = self.outputs[iteration]
            return best_output

        metric = metric or self.settings.primary_metric
        objective = metrics.minimize_or_maximize(metric)

        scores = np.array([output.scores.get(metric, np.nan) for output in self.outputs])

        if len(scores[~np.isnan(scores)]) == 0:
            raise DataException("Could not find model with valid score for metric '{0}'".format(metric))

        if objective == constants.OptimizerObjectives.MAXIMIZE:
            max_idx = np.nanargmax(scores)     # type: int
            return self.outputs[max_idx]
        elif objective == constants.OptimizerObjectives.MINIMIZE:
            min_idx = np.nanargmin(scores)     # type: int
            return self.outputs[min_idx]
        else:
            raise ConfigException(
                "Maximization or Minimization could not be determined based "
                "on current metric.")

    @property
    def is_running(self) -> bool:
        """
        Get the running state of this job.

        :return: True if the job is currently executing, False otherwise.
        """
        return self.status == constants.Status.InProgress

    @property
    def total_iterations(self) -> int:
        """
        Get the total number of iterations.

        :return: the number of iterations
        """
        return self.settings.iterations

    @property
    def current_iteration(self) -> int:
        """
        Get the job's current iteration number.

        This number cannot be changed except by calling add_iteration() to increase the iteration count.

        :return: the current iteration number
        """
        return self._current_iteration

    @property
    def remaining_iterations(self) -> int:
        """
        Get the number of iterations remaining.

        This number will be 0 if the job was cancelled early, even if the total number of iterations was not run.

        :return: the number of remaining iterations
        """
        if not self.is_running:
            return 0
        if self._early_stopping_reached():
            if self.outputs[-1].pipeline_id not in constants.EnsembleConstants.ENSEMBLE_PIPELINE_IDS:
                return 1
            return 0
        return self.total_iterations - self.current_iteration

    @property
    def elapsed_time_min(self) -> int:
        """
        Get the number of minutes spent executing this job.

        :return: the elapsed time in minutes
        """
        if self.start_time is None:
            raise ValueError('Job has not started yet.')

        end_time = self.end_time or datetime.utcnow()
        return int((end_time - self.start_time).total_seconds() / 60)

    def _early_stopping_reached(self) -> bool:
        """
        Determine if early stopping criteria has been met.

        :return: whether execution should stop early
        """
        invalid_score = float('nan')

        if not self.settings.enable_early_stopping:
            return False

        if self.current_iteration <= (self.settings.early_stopping_n_iters + constants.EARLY_STOPPING_NUM_LANDMARKS):
            return False

        if self.best_output is None:
            return False

        lookback = -1 * self.settings.early_stopping_n_iters
        lookback_pipelines = self.outputs[lookback:]
        best_score = self.best_output.score

        for pipeline in lookback_pipelines:
            if pipeline.score == invalid_score:
                continue
            elif pipeline.score == best_score:
                return False
        return True

    def _select_best_output(self, candidate: FitOutput) -> None:
        """
        Given output of pipeline execution, select and save the best output.

        :param candidate: the output to evaluate
        """
        if self.best_output is None or np.isnan(self.best_output.score):
            self.best_output = candidate

        if self.settings.metric_operation == constants.OptimizerObjectives.MAXIMIZE and \
                candidate.score > self.best_output.score:
            self.best_output = candidate
        elif self.settings.metric_operation == constants.OptimizerObjectives.MINIMIZE and \
                candidate.score < self.best_output.score:
            self.best_output = candidate
