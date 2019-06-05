# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2019 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************

from __future__ import print_function

import io
import logging
import numbers
import os

import six
from everett.manager import (
    NO_VALUE,
    ConfigDictEnv,
    ConfigEnvFileEnv,
    ConfigManager,
    ConfigOSEnv,
    ListOf,
    listify,
    parse_bool,
)

try:  # everett version 1.0.1 or greater
    from everett.ext.inifile import ConfigIniEnv
except ImportError:  # everett version 0.9
    from everett.manager import ConfigIniEnv

LOGGER = logging.getLogger(__name__)

DEBUG = False

# Global experiment placeholder. Should be set by the latest call of Experiment.init()
experiment = None

# Global Optimizer
optimizer = None

DEFAULT_UPLOAD_SIZE_LIMIT = 100 * 1024 * 1024  # 100 MebiBytes

DEFAULT_ASSET_UPLOAD_SIZE_LIMIT = 1000 * 1024 * 1024  # 1GB

DEFAULT_STREAMER_MSG_TIMEOUT = 5 * 60

ADDITIONAL_STREAMER_UPLOAD_TIMEOUT = 10 * 60


def get_global_experiment():
    global experiment
    return experiment


def set_global_experiment(new_experiment):
    global experiment
    experiment = new_experiment


def get_global_optimizer():
    global optimizer
    return optimizer


def set_global_optimizer(new_optimizer):
    global optimizer
    optimizer = new_optimizer


def parse_str_or_identity(_type):
    def parse(value):
        if not isinstance(value, str):
            return value

        return _type(value)

    return parse


PARSER_MAP = {
    str: parse_str_or_identity(str),
    int: parse_str_or_identity(int),
    float: parse_str_or_identity(float),
    bool: parse_str_or_identity(parse_bool),
    list: parse_str_or_identity(ListOf(str)),
}


# Vendor generate_uppercase_key for Python 2
def generate_uppercase_key(key, namespace=None):
    """Given a key and a namespace, generates a final uppercase key."""
    if namespace:
        namespace = [part for part in listify(namespace) if part]
        key = "_".join(namespace + [key])

    key = key.upper()
    return key


class Config(object):
    def __init__(self, config_map):
        self.config_map = config_map
        self.override = {}
        self.backend_override = ConfigDictEnv({})
        self.manager = ConfigManager(
            [  # User-defined overrides
                ConfigOSEnv(),
                ConfigEnvFileEnv(".env"),
                ConfigIniEnv(
                    [os.environ.get("COMET_INI"), "./.comet.config", "~/.comet.config"]
                ),
                # Comet-defined overrides
                self.backend_override,
            ],
            doc=(
                "See https://comet.ml/docs/python-sdk/getting-started/ for more "
                + "information on configuration."
            ),
        )

    def __setitem__(self, name, value):
        self.override[name] = value

    def _set_backend_override(self, cfg, namespace):
        # Reset the existing overrides
        self.backend_override.cfg = {}

        for key, value in cfg.items():
            namespaced_key = "_".join(namespace.split("_") + [key])
            full_key = generate_uppercase_key(namespaced_key)
            self.backend_override.cfg[full_key] = value

    def keys(self):
        return self.config_map.keys()

    def __getitem__(self, name):
        if isinstance(name, numbers.Number):
            return list(self.config_map.keys())[name]
        # Config
        config_type = self.config_map[name].get("type", str)
        parser = PARSER_MAP[config_type]
        config_default = self.config_map[name].get("default", None)

        if name in self.override:
            return self.override[name]

        # Value
        splitted = name.split(".")

        value = self.manager(
            splitted[-1], namespace=splitted[:-1], parser=parser, raise_error=False
        )

        if value == NO_VALUE:
            return parser(config_default)

        return value

    def display(self, display_all=False):
        """
        Show the Comet config variables and values.
        """
        n = 1
        print("=" * 65)
        print("Comet config variables and values, in order of preference:")
        print("    %d) Operating System Variable" % n)
        n += 1
        for path in ["./.env", "~/.comet.config", "./.comet.config"]:
            path = os.path.abspath(os.path.expanduser(path))
            if os.path.exists(path):
                print("    %d) %s" % (n, path))
                n += 1
        print("=" * 65)
        print("Settings:\n")
        last_section = None
        for section, setting in sorted(
            [key.rsplit(".", 1) for key in self.config_map.keys()]
        ):
            key = "%s.%s" % (section, setting)
            value = self[key]
            if "." in section:
                section = section.replace(".", "_")
            if value is None:
                value = "..."
            default_value = self.config_map[key].get("default", None)
            if value == default_value or value == "...":
                if display_all:
                    if section != last_section:
                        if last_section is not None:
                            print()  # break beteen sections
                        print("[%s]" % section)
                        last_section = section
                    print("%s = %s" % (setting, value))
            else:
                if section != last_section:
                    if last_section is not None:
                        print("")  # break beteen sections
                    print("[%s]" % section)
                    last_section = section
                print("%s = %s" % (setting, value))
        print("=" * 65)

    def save(self, directory="./", save_all=False, **kwargs):
        """
        Save the settings to .comet.config (default) or
        other path/filename. Defaults are commented out.

        Args:
            directory: the path to save the .comet.config config settings.
            save_all: save unset variables with defaults too
            kwargs: key=value pairs to save
        """
        directory = os.path.expanduser(directory)
        filename = os.path.abspath(os.path.join(directory, ".comet.config"))
        print('Saving config to "%s"...' % filename, end="")
        with io.open(filename, "w", encoding="utf-8") as ini_file:
            ini_file.write(six.u("# Config file for Comet.ml\n"))
            ini_file.write(
                six.u(
                    "# For help see https://www.comet.ml/docs/python-sdk/getting-started/\n"
                )
            )
            last_section = None
            for section, setting in sorted(
                [key.rsplit(".", 1) for key in self.config_map.keys()]
            ):
                key = "%s.%s" % (section, setting)
                key_arg = "%s_%s" % (section, setting)
                if key_arg in kwargs:
                    value = kwargs[key_arg]
                    del kwargs[key_arg]
                elif key_arg.upper() in kwargs:
                    value = kwargs[key_arg.upper()]
                    del kwargs[key_arg.upper()]
                else:
                    value = self[key]
                if len(kwargs) != 0:
                    raise ValueError(
                        "'%s' is not a valid config key" % list(kwargs.keys())[0]
                    )
                if "." in section:
                    section = section.replace(".", "_")
                if value is None:
                    value = "..."
                default_value = self.config_map[key].get("default", None)
                LOGGER.debug("default value for %s is %s", key, default_value)
                if value == default_value or value == "...":
                    # It is a defaut value
                    # Only save it, if save_all is True:
                    if save_all:
                        if section != last_section:
                            if section is not None:
                                ini_file.write(six.u("\n"))  # break beteen sections
                            ini_file.write(six.u("[%s]\n" % section))
                            last_section = section
                        ini_file.write(six.u("# %s = %s\n" % (setting, value)))
                else:
                    # Not a default value; write it out:
                    if section != last_section:
                        if section is not None:
                            ini_file.write(six.u("\n"))  # break beteen sections
                        ini_file.write(six.u("[%s]\n" % section))
                        last_section = section
                    ini_file.write(six.u("%s = %s\n" % (setting, value)))
        print(" done!")


CONFIG_MAP = {
    "comet.disable_auto_logging": {"type": int, "default": 0},
    "comet.api_key": {"type": str},
    "comet.rest_api_key": {"type": str},
    "comet.offline_directory": {"type": str},
    "comet.offline_sampling_size": {"type": int, "default": 15000},
    "comet.url_override": {"type": str, "default": "https://www.comet.ml/clientlib/"},
    "comet.ws_url_override": {"type": str, "default": None},
    "comet.optimization_override": {
        "type": str,
        "default": "https://optimizer.comet.ml/",
    },
    "comet.predictor_url": {"type": str, "default": "https://predictor.comet.ml/"},
    "comet.experiment_key": {"type": str},
    "comet.project_name": {"type": str},
    # Logging
    "comet.logging.file": {"type": str},
    "comet.logging.file_level": {"type": str, "default": "INFO"},
    # Timeout
    "comet.timeout.cleaning": {"type": int, "default": DEFAULT_STREAMER_MSG_TIMEOUT},
    "comet.timeout.upload": {
        "type": int,
        "default": ADDITIONAL_STREAMER_UPLOAD_TIMEOUT,
    },
    # HTTP Allow header
    "comet.allow_header.name": {"type": str},
    "comet.allow_header.value": {"type": str},
    # Feature flags
    "comet.override_feature.sdk_http_logging": {
        "type": bool
    },  # Leave feature toggle default to None
}


def get_config(setting=None):
    """
    Get a config or setting from the current config
    (os.environment or .env file).

    Note: this is not cached, so every time we call it, it
    re-reads the file. This makes these values always up to date
    at the expense of re-getting the data.
    """
    cfg = Config(CONFIG_MAP)
    if setting is None:
        return cfg
    else:
        return cfg[setting]
