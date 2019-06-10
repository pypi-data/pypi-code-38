# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Class to hold feature configuration."""
from typing import Any, Dict, Optional

import logging

from automl.client.core.common import logging_utilities
from automl.client.core.common.exceptions import ConfigException


class FeatureConfig:
    """Class to hold feature configuration."""

    def __init__(self, _id: Optional[str] = None, _type: Optional[str] = None,
                 logger: Optional[logging.Logger] = None, _args: Any = [], _kwargs: Any = {}) -> None:
        """
        Initialize all attributes.

        :param _id: Id of the featurizer.
        :param _type: Type or column purpose the featurizer works on.
        :param _args: Arguments to be send to the featurizer.
        :param _kwargs: Keyword arguments to be send to the featurizer.
        """
        self._logger = logger or logging_utilities.get_logger()
        self._id = _id
        self._type = _type
        self._args = _args or []
        self._kwargs = _kwargs or {}
        logger_key = "logger"
        self._kwargs[logger_key] = self._kwargs.get(logger_key, logger)

    @classmethod
    def from_dict(cls, dct: Dict[str, Any]) -> "FeatureConfig":
        """
        Load from dictionary.

        :param dct: Dictionary holding all the needed params.
        :return: Created object.
        """
        obj = FeatureConfig()
        if 'id' in dct and 'type' in dct:
            obj._id = dct.get('id')
            obj._type = dct.get('type')
            obj._args = dct.get('args', [])
            obj._kwargs = dct.get('kwargs', {})
        else:
            raise ConfigException("Invalid featurizer configuration. Cannot find `id' or `type'.")
        return obj

    @property
    def id(self) -> Optional[str]:
        """
        Get the id of the object.

        :return: The id.
        """
        return self._id.lower() if self._id else None

    @property
    def featurizer_type(self) -> Optional[str]:
        """
        Get the feature type of the object.

        :return: The feature type.
        """
        return self._type.lower() if self._type else None

    @property
    def featurizer_args(self) -> Any:
        """
        Get the featurizer args to be sent to the instance of the featurizer.

        :return: The args.
        """
        return self._args

    @property
    def featurizer_kwargs(self) -> Any:
        """
        Get the featurizer kwargs to be sent to the instance of the featurizer.

        :return: The key word arguments.
        """
        return self._kwargs
