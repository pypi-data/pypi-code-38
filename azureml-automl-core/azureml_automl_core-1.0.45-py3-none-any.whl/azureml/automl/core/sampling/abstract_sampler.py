# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Base class for all samplers."""
from typing import Any, Dict, Optional, Tuple

from abc import ABC, abstractmethod
import logging

from automl.client.core.common import constants
from automl.client.core.common import activity_logger, logging_utilities
from automl.client.core.common.types import DataInputType, DataSingleColumnInputType
from . import SplittingConfig


class AbstractSampler(ABC):
    """Base class for all samplers."""

    def __init__(self,
                 logger: Optional[logging.Logger] = None,
                 task: str = constants.Tasks.CLASSIFICATION,
                 *args: Any, **kwargs: Any) -> None:
        """Initialize logger for the sub class."""
        self._task = task
        self._logger = logger or logging_utilities.get_logger()

    @abstractmethod
    def sample(self, X: DataInputType, y: DataSingleColumnInputType) \
            -> Tuple[DataInputType, DataSingleColumnInputType, SplittingConfig]:
        """All sub classes should implement this."""
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
