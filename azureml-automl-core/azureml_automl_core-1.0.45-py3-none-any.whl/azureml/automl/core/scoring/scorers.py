# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Factory for scorers."""
from typing import Any

from automl.client.core.common import constants

from .abstract_scorer import AbstractScorer
from .classification_scorer import ClassificationScorer
from .regression_scorer import RegressionScorer


class Scorers:
    """Factory for scorers."""

    @classmethod
    def get(cls, metric_name: str, task: str, *args: Any, **kwargs: Any) -> Any:
        """
        Create and return the request sweeper.

        :param metric_name: Name of the requested sweeper.
        :param task: Task type.
        :param args: Positional arguments.
        :param kwargs: Keyword arguments.
        """
        if task == constants.Tasks.CLASSIFICATION:
            return cls.classification(metric_name=metric_name, *args, **kwargs)
        if task == constants.Tasks.REGRESSION:
            return cls.regression(metric_name=metric_name, *args, **kwargs)
        return None

    @classmethod
    def classification(cls, *args: Any, **kwargs: Any) -> AbstractScorer:
        """Create and return the default scorer."""
        return ClassificationScorer(*args, **kwargs)

    @classmethod
    def regression(cls, *args: Any, **kwargs: Any) -> AbstractScorer:
        """Create and return the default scorer."""
        return RegressionScorer(*args, **kwargs)
