# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Hold sweeper configuration."""
from typing import Any, cast, Dict, List, Optional

import logging
import json
import os

from automl.client.core.common import activity_logger, logging_utilities
from automl.client.core.common.exceptions import ConfigException
from .._downloader import Downloader


class SweeperConfig:
    """Holder for sweeper configurations."""

    CONFIG_DOWNLOAD_PREFIX = "https://aka.ms/automl-resources/configs/"
    CONFIG_DOWNLOAD_FILE = "config_v1.2.json"

    DEFAULT_CONFIG_PATH = "../../sweeping/config.json"

    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        """Initialize all attributes."""
        self._enabled = False
        self._type = ''
        self._sampler = {}  # type: Dict[str, Any]
        self._estimator = ''
        self._scorer = ''
        self._baseline = {}     # type: Dict[str, Any]
        self._experiment = {}   # type: Dict[str, Any]
        self._column_purposes = []  # type: List[Dict[str, Any]]
        self._epsilon = 0.0
        self._logger = logger or logging_utilities.get_logger()

    @classmethod
    def from_dict(cls, dct: Dict[str, Any]) -> "SweeperConfig":
        """
        Load from dictionary.

        :param dct: The dictionary containing all the needed params.
        :return: Created sweeper configuration.
        """
        obj = SweeperConfig()
        obj._enabled = dct.get('enabled', False)
        obj._type = dct.get('type', '')
        obj._sampler = dct.get('sampler', {})
        obj._estimator = dct.get('estimator', '')
        obj._scorer = dct.get('scorer', '')
        obj._baseline = cast(Dict[str, Any], dct.get('baseline'))
        obj._experiment = cast(Dict[str, Any], dct.get('experiment'))
        obj._column_purposes = dct.get('column_purposes', [])
        obj._epsilon = dct.get('epsilon', 0.0)
        return obj

    @classmethod
    def _validate(cls, config: "SweeperConfig") -> None:
        """Validate the configuration."""
        assert config._type is not None
        assert config._sampler is not None
        assert config._estimator is not None
        assert config._baseline is not None
        assert config._experiment is not None
        assert config._column_purposes is not None
        assert len(config._column_purposes) > 0, "At least one column purpose should be specified"
        assert config._scorer is not None

    def get_config(self) -> Dict[str, Any]:
        """Provide configuration."""
        try:
            file_path = Downloader.download(self.CONFIG_DOWNLOAD_PREFIX, self.CONFIG_DOWNLOAD_FILE, os.getcwd())
            if file_path is None:
                raise ConfigException("Configuration url: {prefix}{file_path} is not accessible!.")

            with open(file_path, 'r') as f:
                cfg = json.load(f)  # type: Dict[str, Any]
                return cfg
        except Exception as e:
            self._logger.debug("Exception when trying to load config from the remote: "
                               "{prefix}{file_path} with error {e}".format(prefix=self.CONFIG_DOWNLOAD_PREFIX,
                                                                           file_path=self.CONFIG_DOWNLOAD_FILE,
                                                                           e=e))
            return self.default()

    @classmethod
    def default(cls) -> Dict[str, Any]:
        """Return the default back up configuration."""
        default_config_path = os.path.abspath(os.path.join(__file__, cls.DEFAULT_CONFIG_PATH))
        with open(default_config_path, "r") as f:
            result = json.loads(f.read())  # type: Dict[str, Any]
            return result

    @classmethod
    def set_default(cls, overide_config_path: str) -> None:
        """
        Override configuration path.

        :param overide_config_path: Overriden config path.
        """
        cls.DEFAULT_CONFIG_PATH = overide_config_path

    def __getstate__(self):
        """
        Get state picklable objects.

        :return: state
        """
        state = dict(self.__dict__)
        # Remove the unpicklable entries. TelemetryActivityLogger is pickleable
        if not isinstance(self._logger, activity_logger.TelemetryActivityLogger):
            state['_logger'] = None
        return state

    def __setstate__(self, state):
        """
        Set state for object reconstruction.

        :param state: pickle state
        """
        self.__dict__.update(state)
        self._logger = self._logger or logging_utilities.get_logger()

    def __json__(self) -> Dict[str, Any]:
        """JSON representation of the class."""
        return {
            "type": self._type,
            "sampler": self._sampler,
            "estimator": self._estimator,
            "scorer": self._scorer,
            "baseline": self._baseline,
            "experiment": self._experiment,
            "column_purposes": self._column_purposes,
            "epsilon": self._epsilon
        }

    def __str__(self) -> str:
        """Human readable representation of this object."""
        return json.dumps(self.__json__())
