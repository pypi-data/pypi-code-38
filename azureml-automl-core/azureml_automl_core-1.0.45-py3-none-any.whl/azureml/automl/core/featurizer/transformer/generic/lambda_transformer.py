# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Lambda function based transformer."""
from typing import Any, Callable, Optional
import logging

import numpy as np

from automl.client.core.common.logging_utilities import function_debug_log_wrapped
from ..automltransformer import AutoMLTransformer


class LambdaTransformer(AutoMLTransformer):
    """
    Transforms column through a lambda function.

    :param func: The lambda function to use in the transformation.
    :type func: function
    """

    def __init__(self, func: Callable[[np.ndarray], Any] = lambda x: x, logger: Optional[logging.Logger] = None):
        """
        Construct the LambdaTransformer.

        :param func: The lambda function to use in the transformation.
        :param logger: Logger to be injected to usage in this class.
        :return:
        """
        super().__init__()
        self.func = func
        self._init_logger(logger)

    def __getstate__(self):
        """
        Overriden to remove func object when pickling.

        :return: this object's state as a dictionary
        """
        state = super(LambdaTransformer, self).__getstate__()
        newstate = {**state, **self.__dict__}
        newstate['func'] = None
        return newstate

    def _to_dict(self):
        """
        Create dict from transformer for  serialization usage.

        :return: a dictionary
        """
        dct = super(LambdaTransformer, self)._to_dict()
        dct['id'] = "lambda_featurizer"
        dct['type'] = "generic"

        return dct

    @function_debug_log_wrapped
    def fit(self, x, y=None):
        """
        Fit function for lambda transform.

        :param x: Input array.
        :type x: numpy.ndarray
        :param y: Target values.
        :type y: numpy.ndarray
        :return: The instance object: self.
        """
        return self

    @function_debug_log_wrapped
    def transform(self, x):
        """
        Lambda transform which calls the lambda function over the input.

        :param x: Input array.
        :type x: numpy.ndarray
        :return: Result of lambda transform.
        """
        return self.func(x)
