# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Config module
"""
import logging
import os
from os import getenv
from os.path import expanduser, isfile

from .constants import BACKEND_URL

try:
    # python2
    from ConfigParser import RawConfigParser, Error as ConfigError
except ImportError:
    # python3
    from configparser import RawConfigParser, Error as ConfigError

LOGGER = logging.getLogger(__name__)

HOME_FILE_PATH = expanduser("~/.sqreen.ini")


CONFIG_DEFAULT_VALUE = {
    # The backend URL
    "URL": BACKEND_URL,
    # Default token to use
    "TOKEN": None,
    # If the token is an org token, default app_name
    "APP_NAME": None,
    # Proxy to use if needed
    "PROXY_URL": None,
    # Should the client check the rules signatures
    "RULES_SIGNATURE": True,
    # Custom rules to be used in development
    "RULES": None,
    # Log configuration
    "LOG_LEVEL": "CRITICAL",
    "LOG_LOCATION": None,
    # Should sqreen protection run while application is tested?
    "RUN_IN_TEST": False,
    # Should sqreen report callback performance on newrelic?
    "REPORT_PERF_NR": False,
    # Initial features usually given by the environment
    "INITIAL_FEATURES": "{}",
    # Custom IP headers
    "IP_HEADER": None,
    # Enable PII scrubbing (password, ...)
    "STRIP_SENSITIVE_DATA": True,
    # Sensitive keys to strip
    "STRIP_SENSITIVE_KEYS": "password, secret, passwd, authorization, api_key, apikey, access_token",
    # Sensitive regexp (matches items like credit cards)
    "STRIP_SENSITIVE_REGEX": r"^(?:\d[ -]*?){13,16}$"
}


class Config(object):
    """ Config class to parse several sources of config and merge them

    This try to load configuration by different ways.
    1. Default value
    2. By file, which overrides whatever result we found in 1:
      a. From path in environment variable SQREEN_CONFIG_FILE
      b. From local directory sqreen.ini
      c. From home in ~/.sqreen.ini
    3. From Django configuration directly
    4. From the environment, which overrides whatever result we found in 1 or 2.
    """

    FILE_ENV_VAR = "SQREEN_CONFIG_FILE"
    HOME_FILE_PATH = HOME_FILE_PATH

    def __init__(self, default_values=None):
        self.config = {}

        if default_values is None:
            default_values = CONFIG_DEFAULT_VALUE

        self.default_values = default_values

        self.loaders = [
            self.load_from_default_values,
            self.load_from_file,
            self.load_from_env,
        ]

        self.config_path = None

    def load(self):
        """ Call each loaders and update the config at the end
        """
        base_config = {}

        for loader in self.loaders:
            loaded = loader()

            if loaded:
                base_config.update(loaded)

        self.config = base_config

    def load_from_default_values(self):
        """ Returns default values
        """
        return self.default_values

    def load_from_file(self):
        """ Load from ONE config file, the file path is explained in class
        docstring
        """

        file_path = (
            self.config_path
            or self._file_path_from_env()
            or self._file_path_from_home()
            or self._file_path_from_local()
        )

        if not file_path:
            return {}

        config = RawConfigParser()

        try:
            config.read(file_path)

            config_dict = {}
            for option in config.options("sqreen"):
                config_dict[option.upper()] = config.get("sqreen", option)

            return config_dict
        except ConfigError:
            LOGGER.debug("Error parsing config file %s", file_path)
            return {}

    @staticmethod
    def load_from_env():
        """ Load configuration from os environment variables, variables
        must be prefixed with SQREEN_ to be detected.
        """
        env_config = {}
        for env_var in os.environ:
            if env_var.startswith("SQREEN_"):
                env_config[env_var.replace("SQREEN_", "", 1)] = os.environ[
                    env_var
                ]

        return env_config

    def _file_path_from_env(self):
        """ Return file path if os environement was set and file exists
        """
        path = getenv(self.FILE_ENV_VAR, default=None)

        if path and isfile(path):
            return path

    def _file_path_from_home(self):
        """ Return file path if file exists in home directory
        """
        if self.HOME_FILE_PATH and isfile(self.HOME_FILE_PATH):
            return self.HOME_FILE_PATH

    @staticmethod
    def _file_path_from_local():
        """ Return file path if file exists locally on the project
        """
        if isfile("sqreen.ini"):
            return os.path.join(os.getcwd(), "sqreen.ini")

    def __getitem__(self, name):
        return self.config[name]


CONFIG = Config()
CONFIG.load()
