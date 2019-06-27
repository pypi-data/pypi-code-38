# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Transforms column using a label encoder to encode categories into numbers."""
from typing import Optional, Any, List
import logging
from sklearn.preprocessing import OneHotEncoder
import numpy as np
import pandas as pd

from automl.client.core.common import constants
from automl.client.core.common.logging_utilities import function_debug_log_wrapped
from automl.client.core.common.model_wrappers import _AbstractModelWrapper
from automl.client.core.common.types import DataSingleColumnInputType, DataInputType

from ..automltransformer import AutoMLTransformer


class OneHotEncoderTransformer(AutoMLTransformer, _AbstractModelWrapper):
    """Convert input to one hot encoded vector."""

    def __init__(self, logger: Optional[logging.Logger] = None,
                 **kwargs: Any) -> None:
        """
        Initialize for onehotencoding transform.

        :param logger: Logger to be injected to usage in this class.
        :param args: args for transform.
        :param kwargs: kwargs for transform.
        :return:
        """
        super().__init__()
        if constants.FeatureSweeping.LOGGER_KEY in kwargs:
            kwargs.pop(constants.FeatureSweeping.LOGGER_KEY)
        if 'dtype' not in kwargs:
            kwargs['dtype'] = np.uint8
        self._onehotencoder = OneHotEncoder(**kwargs)
        self._init_logger(logger)

    def _to_dict(self):
        """
        Create dict from transformer for  serialization usage.

        :return: a dictionary
        """
        dct = super(OneHotEncoderTransformer, self)._to_dict()
        dct['id'] = "onehotencoder"
        dct['type'] = 'categorical'

        return dct

    @function_debug_log_wrapped
    def fit(self, x: DataInputType, y: Optional[DataSingleColumnInputType] = None) -> "OneHotEncoderTransformer":
        """
        Fit function for label encoding transform which learns the labels.

        :param x: Input array of values to be encoded.
        :type x: pandas.DataFrame or numpy.ndarray
        :param y: Target values.
        :type y: numpy.ndarray
        :return: The instance object: self.
        """
        if isinstance(x, np.ndarray) and len(x.shape) == 1:
            x = x.reshape(x.shape[0], 1)
        if isinstance(x, pd.Series):
            x = pd.DataFrame(x)
        self._onehotencoder.fit(x)
        return self

    @function_debug_log_wrapped
    def transform(self, x: DataInputType) -> DataInputType:
        """
        Transform categorical data to onehotencoded value.

        :param x: Input array.
        :type x: pandas.DataFrame or numpy.ndarray
        :return: OneHotEncoded array.
        """
        if isinstance(x, np.ndarray) and len(x.shape) == 1:
            x = x.reshape(x.shape[0], 1)
        if isinstance(x, pd.Series):
            x = pd.DataFrame(x)
        return self._onehotencoder.transform(x)

    def get_model(self) -> OneHotEncoder:
        """
        Return OneHotEncoder model.

        :return: OneHotEncoder model.
        """
        return self._onehotencoder

    def get_feature_names(self) -> List[str]:
        """
        Return names of categories encoded.

        :return: List of encoded properties.
        """
        return list(self._onehotencoder.categories_[0])
