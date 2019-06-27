# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Scorer for Accuracy."""
from typing import Any, Dict, Optional, cast

from automl.client.core.common import constants
from automl.client.core.common.exceptions import DataException
from automl.client.core.common.metrics import is_better, compute_metrics_classification
from .abstract_scorer import AbstractScorer

import numpy as np
from sklearn.base import BaseEstimator


class ClassificationScorer(AbstractScorer):
    """Scorer for Accuracy."""

    def __init__(self, *args: Any, metric_name: str = "accuracy", task: str = constants.Tasks.CLASSIFICATION,
                 **kwargs: Any) -> None:
        """Initialize the object."""
        # Required for methods inherited from AbstractScorer to work
        super(ClassificationScorer, self).__init__(metric_name,
                                                   task, *args, **kwargs)

        # Constraint such that required additive lift can never be less than this
        self._min_lift_req = 0.001

        # Constraint such that maximum additive lift can never be greater than this
        self._max_lift_req = 0.03

        # Small number to avoid divide by zero errors when accuracy is 1.
        self._smoothing = 0.0001

    def score(self, estimator: BaseEstimator,
              valid_features: np.ndarray,
              y_actual: np.ndarray
              ) -> float:
        """Calculate the performance of an estimator."""
        y_pred = estimator.predict_proba(valid_features)
        self._n_rows = len(y_actual)
        class_labels = np.unique(np.concatenate((y_actual, estimator.classes_)))
        ret = cast(float, compute_metrics_classification(y_pred_probs=y_pred,
                                                         y_test=y_actual,
                                                         class_labels=class_labels,
                                                         trained_class_labels=estimator.classes_,
                                                         metrics=[self.metric_name],
                                                         logger=self._logger)[self.metric_name])
        self._logger.info("Feature sweep calculation: {metric_name} = {metric_value}.".format(
            metric_name=self.metric_name, metric_value=ret))
        return ret

    def _get_required_delta(self,
                            n_rows: Optional[int],
                            epsilon: float) -> float:
        """
        Heuristic for what delta is big enough for an experiment to be better than default.

        We assume error on scores goes as 1/sqrt(n_rows).
        This is a binomial probability inspired *heuristic*.
        For a 10000 row evaluation data set, the binomial standard deviation would be ~ 0.01, thus with the below
        parameterization epsilon should be set at ~ 0.01.  This would mean for 10000 row evaluation
        data sets, a 0.01 increase in score is needed to justify the expense of adding a non-default
        transform. On the other hand, for 2000 row evaluation data sets, the required delta
        would be ~ 0.022 to justify new transforms.

        :param n_rows: number of rows in the dataset
        :param epsilon: the required absolute score increase at 10000 rows.
        """
        # Binomial prob inspired *heuristic* for standard deviation and fixed p.
        # This is maximized at p = 0.5.  At 10000 rows, this error would be ~ 0.01, thus
        # epsilon should be of order 0.01.
        delta_req = epsilon * (np.sqrt(10000)) / np.sqrt(n_rows)

        # Add min and max clipping logic on delta_req to avoid it being too small or big
        result = np.clip(delta_req, a_min=self._min_lift_req, a_max=self._max_lift_req)  # type: float
        self._logger.debug("Feature sweeping required additive delta = {}".format(result))
        return result

    def calculate_lift(self, baseline_score: float, experiment_score: float) -> float:
        """
        Calculate improvement in *error* rate.

        Calculating lift from error rate (as opposed to accuracy) means transforms
        that give lift on columns with high information content/high scores will be considered
        more important.  Example: Transforms that move some columns from 0.95 --> 0.96 will have
        higher lift than other transforms that move some columns from 0.6 --> 0.65

        :param baseline_score: The baseline score.
        :param experiment_score: Experiment score.
        :return: the relative improvement in error rate
        """
        if 0 <= baseline_score <= 1. and 0 <= experiment_score <= 1.:
            ret = (experiment_score - baseline_score) / (1 - baseline_score + self._smoothing)
        else:
            raise ValueError(
                "The baseline_score and experiment_score should be between 0 and 1 inclusive.")
        return ret

    def is_experiment_better_than_baseline(self, baseline_score: float, experiment_score: float,
                                           epsilon: float) -> bool:
        """
        Override this to provide comparison between two experiment outputs.

        :param baseline_score: The baseline score.
        :param experiment_score: Experiment score.
        :param epsilon: Minimum delta considered gain/loss.
        :return: Whether or not the experiment score is better than baseline.
        """
        if self._n_rows is None:
            raise DataException("{cls} score method should be called first.".format(cls=self.__class__.__name__))
        return self.is_experiment_score_better(
            baseline_score + self._get_required_delta(self._n_rows, epsilon),
            experiment_score)
