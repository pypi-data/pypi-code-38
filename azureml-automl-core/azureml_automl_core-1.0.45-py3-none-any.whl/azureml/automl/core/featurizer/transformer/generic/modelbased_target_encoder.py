# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Generic target encoder."""
from typing import Any, Dict, Optional, Type
import logging

import numpy as np
from sklearn.base import BaseEstimator
from sklearn.naive_bayes import MultinomialNB
from automl.client.core.common.exceptions import ConfigException
from ..automltransformer import AutoMLTransformer
from automl.client.core.common.logging_utilities import function_debug_log_wrapped
from automl.client.core.common.model_wrappers import _AbstractModelWrapper
from automl.client.core.common.types import DataSingleColumnInputType


class ModelBasedTargetEncoder(AutoMLTransformer, _AbstractModelWrapper):
    """Generic target encoder."""

    def __init__(self, logger: Optional[logging.Logger] = None,
                 model_class: 'Optional[Type[BaseEstimator]]' = None,
                 model_params: Optional[Dict[str, Any]] = None,
                 *args: Any, **kwargs: Any) -> None:
        """Construct the target encoder.

        :param logger: The logger.
        :param model_class: The class to be instantiated for the model.
        :param model_params: Params to be passed to the model when initiating.
        """
        super().__init__()
        self._init_logger(logger)
        if not model_class:
            self._logger_wrapper("WARN", "Model required for " + self.__class__.__name__)
            raise ConfigException("model_class cannot be None when instantiating: " + self.__class__.__name__)

        self._model_class = model_class
        self._model_params = model_params or {}
        self._model = None                              # type: Optional[BaseEstimator]

    def _to_dict(self):
        """
        Create dict from transformer for  serialization usage.

        :return: a dictionary
        """
        dct = super(ModelBasedTargetEncoder, self)._to_dict()
        if self._model_class and self._model_class == MultinomialNB:
            dct['id'] = "naive_bayes"
        else:
            dct['id'] = "text_target_encoder"
        if self._model_class:
            dct['kwargs']['model_class'] = "{}.{}".format(str(self._model_class.__module__),
                                                          self._model_class.__name__)
        if self._model_params and len(self._model_params) > 0:
            dct['kwargs']['model_params'] = self._model_params
        dct['type'] = 'text'

        return dct

    @function_debug_log_wrapped
    def fit(self, X: DataSingleColumnInputType, y: Optional[DataSingleColumnInputType] = None) \
            -> "ModelBasedTargetEncoder":
        """
        Instantiate and train on the input data.

        :param X: The data to transform.
        :param y: Target values.
        :return: The instance object: self.
        """
        self._model = self._model_class(**self._model_params)
        self._model.fit(X, y)
        return self

    @function_debug_log_wrapped
    def transform(self, X: DataSingleColumnInputType) -> np.ndarray:
        """
        Transform data x.

        :param X: The data to transform.
        :return: Prediction probability values from input model.
        """
        # TODO How do we do this in case of regression.
        if X is not None and self._model is not None:
            return self._model.predict_proba(X)
        else:
            return np.array([])

    def get_model(self):
        """
        Return the inner model object.

        :return: An inner model object.
        """
        return self._model
