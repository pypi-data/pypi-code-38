# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Class to hold sampler configuration."""
from typing import Any, Dict, Optional

import logging

from automl.client.core.common import logging_utilities
from automl.client.core.common.exceptions import ConfigException


class SamplerConfig:
    """Class to hold sampler configuration."""

    def __init__(self, _id: str, logger: Optional[logging.Logger] = None,
                 sampler_args: Any = [], sampler_kwargs: Any = {}) -> None:
        """
        Initialize all attributes.

        :param _id: Id of the sampler.
        :param _args: Arguments to be send to the sampler.
        :param _kwargs: Keyword arguments to be send to the sampler.
        """
        self._logger = logger or logging_utilities.get_logger()
        self._id = _id
        self._args = sampler_args or []
        self._kwargs = sampler_kwargs or {}
        logger_key = "logger"
        self._kwargs[logger_key] = self._kwargs.get(logger_key, logger)

    @classmethod
    def from_dict(cls, dct: Dict[str, Any]) -> "SamplerConfig":
        """
        Load from dictionary.

        :param dct: Dictionary holding all the needed params.
        :return: Created object.
        """
        if 'id' in dct:
            obj = SamplerConfig(dct['id'], sampler_args=dct.get('args', []), sampler_kwargs=dct.get('kwargs', {}))
        else:
            raise ConfigException("Invalid sampler configuration. Cannot find `id'.")
        return obj

    @property
    def id(self) -> str:
        """
        Get the id of the object.

        :return: The id.
        """
        return self._id.lower()

    @property
    def sampler_args(self) -> Any:
        """
        Get the sampler args to be sent to the instance of the sampler.

        :return: The args.
        """
        return self._args

    @property
    def sampler_kwargs(self) -> Any:
        """
        Get the sampler kwargs to be sent to the instance of the sampler.

        :return: The key word arguments.
        """
        return self._kwargs
