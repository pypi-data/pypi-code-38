# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Base objects for Transformers and Estimators."""
from typing import Any, Callable, Dict, Optional
from abc import ABCMeta
import logging

from sklearn.base import BaseEstimator, RegressorMixin, TransformerMixin


class AzureMLForecastEstimatorBase(BaseEstimator, metaclass=ABCMeta):
    """Base estimator for all AzureMLForecastSDK."""

    def __init__(self, *args, **kwargs):
        """Construct a base estimator."""
        for dictionary in args:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def __getstate__(self) -> Dict[str, Any]:
        """
        Overriden to remove logger object when pickling.

        :return: this object's state as a dictionary
        """
        state = super(AzureMLForecastEstimatorBase, self).__getstate__()
        newstate = {**state, **self.__dict__}
        newstate['logger'] = None
        return newstate

    @property
    def pipeline_id(self):
        """
        Get or set the pipeline ID.

        :returns: pipeline uuid.
        :rtype: str
        """
        if hasattr(self, '_pipeline_id'):
            # Many transformer constructors are defining their own constructors.
            # We may not have the _pipeline_id defined.
            return self._pipeline_id
        else:
            return "No ID"

    @pipeline_id.setter
    def pipeline_id(self, value):
        """Pipeline ID setter."""
        self._pipeline_id = value

    @property
    def pipeline_run_id(self):
        """
        Get or set the pipeline run ID.

        :returns: pipeline uuid.
        :rtype: str
        """
        if hasattr(self, "_run_id"):
            # Many transformer constructors are defining their own constructors.
            # We may not have the _run_id defined.
            return self._run_id
        else:
            return "No ID"

    @pipeline_run_id.setter
    def pipeline_run_id(self, value):
        """Pipeline run ID setter."""
        # Many transformer constructors are defining their own constructors.
        # Make sure that we have the _run_id defined.
        self._run_id = value

    def _init_logger(self, logger: Optional[logging.Logger]) -> None:
        """
        Init the logger.

        :param logger: the logger handle.
        :type logger: logging.Logger.
        """
        self.logger = logger

    def _logger_wrapper(self, level: str, message: str) -> None:
        """
        Log a message with a given debug level in a log file.

        :param level: log level (info or debug)
        :param message: log message
        """
        # Check if the logger object is valid. If so, log the message
        # otherwise pass
        if self.logger is not None:
            if level == 'info':
                self.logger.info(message)
            elif level == 'warning':
                self.logger.warning(message)
            elif level == 'debug':
                self.logger.debug(message)

    """
    def fit(self, X, y):
        A reference implementation of a fitting function

        Parameters
        ----------
        X : array-like or sparse matrix of shape = [n_samples, n_features]
            The training input samples.
        y : array-like, shape = [n_samples] or [n_samples, n_outputs]
            The target values (class labels in classification, real numbers in
            regression).

        Returns
        -------
        self : object
            Returns self.

        X, y = check_X_y(X, y)
        # Return the estimator
        return self


    def predict(self, X):
        A reference implementation of a predicting function.

        Parameters
        ----------
        X : array-like of shape = [n_samples, n_features]
            The input samples.

        Returns
        -------
        y : array of shape = [n_samples]
            Returns :math:`x^2` where :math:`x` is the first column of `X`.
        X = check_array(X)
        return X[:, 0]**2
        pass
    """


class AzureMLForecastRegressorBase(AzureMLForecastEstimatorBase, RegressorMixin):
    """
    Base classifier for AzureMLForecastSDK.

    :param demo_param: str, optional
        A parameter used for demonstration.

    :Attributes:
    X_ : array, shape = [n_samples, n_features]
        The input passed during :meth:`fit`
    y_ : array, shape = [n_samples]
        The labels passed during :meth:`fit`
    """


class AzureMLForecastTransformerBase(AzureMLForecastEstimatorBase, TransformerMixin):
    """
    Base transformer for AzureMLForecastSDK ..

    :param demo_param: str, optional
        A parameter used for demonstration.

    :Attributes:
    input_shape: tuple
        The shape the data passed to :meth:`fit`

    def fit(self, X, y):
        A reference implementation of a fitting function for a transformer.

        :Parameters:
        X : array-like or sparse matrix of shape = [n_samples, n_features]
            The training input samples.
        y : None
            There is no need of a target in a transformer, yet the pipeline API
            requires this parameter.

        :Returns:
        self: object
            Returns self.

    def transform(self, X):
        A reference implementation of a transform function.

        :Parameters:
        X : array-like of shape = [n_samples, n_features]
            The input samples.

        :Returns:
        X_transformed : array of int of shape = [n_samples, n_features]
            The array containing the element-wise square roots of the values
            in `X`

        # Check is fit had been called
        check_is_fitted(self, ['input_shape_'])

        # Input validation
        X = check_array(X)

        # Check that the input is of the same shape as the one passed
        # during fit.
        if X.shape != self.input_shape_:
            raise ValueError('Shape of input is different from what was seen'
                             'in `fit`')
        return np.sqrt(X)
    """
