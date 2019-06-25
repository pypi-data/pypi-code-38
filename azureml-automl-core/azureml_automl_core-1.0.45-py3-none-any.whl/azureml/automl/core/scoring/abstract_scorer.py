# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Base class for all scorers."""
from typing import Any, Dict, Optional, cast
from abc import ABC, abstractmethod
from automl.client.core.common import activity_logger, constants, exceptions as ex
from automl.client.core.common.metrics import is_better, compute_metrics
from sklearn.base import BaseEstimator

import logging

import numpy as np

from automl.client.core.common import logging_utilities


class AbstractScorer(ABC):
    """Base class for all scorers."""

    def __init__(self,
                 metric_name: str,
                 task: str,
                 logger: Optional[logging.Logger] = None,
                 *args: Any, **kwargs: Any) -> None:
        """Initialize logger and task to be used by the derived classes."""
        self._task = task
        self.metric_name = metric_name
        self._n_rows = None  # type: Optional[int]
        self._logger = logger or logging_utilities.get_logger()

    @abstractmethod
    def score(self, estimator: BaseEstimator,
              valid_features: np.ndarray,
              y_actual: np.ndarray
              ) -> float:
        """
        Override this method to give a score calculation.

        Calculate the performance of an estimator.
        """
        raise NotImplementedError()

    def is_experiment_score_better(self,
                                   baseline_score_with_mod: float,
                                   experiment_score: float) -> bool:
        """
        Return true if experiment_score is better than baseline_score_with_mod.

        :param baseline_score_with_mod: baseline_score with stat sig mod, e.g. baseline_score + epsilon
        :param experiment_score: score of transform we're experimenting with to see if there's improvement.
        """
        result = is_better(
            experiment_score,
            baseline_score_with_mod,
            metric=self.metric_name,
            task=self._task)  # type: bool
        return result

    @abstractmethod
    def calculate_lift(self, baseline_score: float, experiment_score: float) -> float:
        """
        Override this method to give a lift calculation.

        Should give a apples-to-apples comparison between all different
        transforms operating on different columns.  The output should be
        something like relative score increase or relative improvement on error
        """
        raise NotImplementedError()

    @abstractmethod
    def is_experiment_better_than_baseline(self, baseline_score: float, experiment_score: float,
                                           epsilon: float) -> bool:
        """
        Override this to provide comparison between two experiment outputs.

        :param baseline_score: The baseline score.
        :param experiment_score: Experiment score.
        :param epsilon: Minimum delta considered gain/loss.
        :return: Whether or not the experiment score is better than baseline.
        """
        raise NotImplementedError()

    def __getstate__(self) -> Dict[str, Any]:
        """
        Get state picklable objects.

        :return: state
        """
        state = dict(self.__dict__)
        # Remove the unpicklable entries. TelemetryActivityLogger is pickleable
        if not isinstance(self._logger, activity_logger.TelemetryActivityLogger):
            state['_logger'] = None
        return state

    def __setstate__(self, state: Dict[str, Any]) -> None:
        """
        Set state for object reconstruction.

        :param state: pickle state
        """
        self.__dict__.update(state)
        self._logger = self._logger or logging_utilities.get_logger()
