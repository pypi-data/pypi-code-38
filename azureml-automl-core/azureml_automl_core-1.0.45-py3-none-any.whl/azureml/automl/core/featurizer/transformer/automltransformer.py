# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Base logger class for all the transformers."""
from typing import List, Optional, Dict, Any
import logging

from sklearn.base import BaseEstimator, TransformerMixin

from automl.client.core.common.types import DataSingleColumnInputType, DataInputType
from azureml.automl.core.column_purpose_detection.types import StatsAndColumnPurposeType


class AutoMLTransformer(BaseEstimator, TransformerMixin):
    """Base logger class for all the transformers."""

    def __init__(self, *args, **kwargs):
        """Init the logger class."""
        self.logger = None  # type: Optional[logging.Logger]

    @property
    def operator_name(self) -> Optional[str]:
        """Operator name for the engineering feature names."""
        return self._get_operator_name()

    def _get_operator_name(self) -> Optional[str]:
        return None

    @property
    def transformer_name(self) -> str:
        """Transform function name for the engineering feature names."""
        return self._get_transformer_name()

    def _get_transformer_name(self) -> str:
        # TODO Remove this and make it abstract
        return self.__class__.__name__

    def __getstate__(self):
        """
        Overridden to remove logger object when pickling.

        :return: this object's state as a dictionary
        """
        state = super(AutoMLTransformer, self).__getstate__()
        newstate = {**state, **self.__dict__}
        newstate['logger'] = None
        return newstate

    def _to_dict(self):
        """
        Create dict from transformer for  serialization usage.

        :return: a dictionary
        """
        dct = {"args": [], "kwargs": {}}  # type: Dict[str, Any]
        return dct

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

    def get_memory_footprint(self, X: DataInputType, y: DataSingleColumnInputType) -> int:
        """
        Obtain memory footprint by adding this featurizer.

        :param X: Input data.
        :param y: Input label.
        :return: Amount of memory taken in bytes.
        """
        # TODO Make this method abstract once we have all featurizers implementing this method.
        return 0
