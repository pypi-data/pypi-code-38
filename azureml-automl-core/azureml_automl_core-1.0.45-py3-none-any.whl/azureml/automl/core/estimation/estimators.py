# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""IoC container of all estimators."""
from typing import Any, Optional
from sklearn.base import BaseEstimator
from sklearn.linear_model import LogisticRegression, LinearRegression
import lightgbm as lgb

from automl.client.core.common import utilities


class Estimators:
    """IoC container of all estimators."""

    @classmethod
    def get(cls, estimator_name: str, *args: Any, **kwargs: Any) -> Optional[BaseEstimator]:
        """
        Create and return the request estimator.

        :param estimator_name: Name of the requested estimator.
        """
        if hasattr(cls, estimator_name):
            member = getattr(cls, estimator_name)
            if callable(member):  # Make sure the member is a callable.
                return member(*args, **kwargs)

        return None

    @classmethod
    def default(cls) -> BaseEstimator:
        """Create and return default estimator."""
        return cls.logistic_regression()

    @classmethod
    def logistic_regression(cls, *args: Any, **kwargs: Any) -> LogisticRegression:
        """Create a Logistic regression estimator."""
        if not kwargs:
            kwargs = {"C": 1.0}

        # Remove logger for logistic_regression
        kwargs.pop('logger', None)

        return LogisticRegression(*args, **kwargs)

    @classmethod
    def linear_regression(cls, *args: Any, **kwargs: Any) -> LinearRegression:
        """Create a Linear regression estimator."""
        return LinearRegression(*args, **kwargs)

    @classmethod
    def lgbm_classifier(cls, *args: Any, **kwargs: Any) -> lgb.LGBMClassifier:
        """Create a LightGBM classification estimator."""
        return lgb.LGBMClassifier(*args, **kwargs)

    @classmethod
    def lgbm_regressor(cls, *args: Any, **kwargs: Any) -> lgb.LGBMRegressor:
        """Create a LightGBM regression estimator."""
        return lgb.LGBMRegressor(*args, **kwargs)
