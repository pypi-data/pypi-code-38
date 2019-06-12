from functools import partial
import logging
import os

import yaml
import click

from spell.configs.config_classes import GlobalConfig


class ConfigHandler(object):

    def __init__(self, spell_dir, logger=None):
        self.spell_dir = os.path.expanduser(spell_dir)
        self.config_file_path = os.path.join(self.spell_dir, "config")
        self.config = None
        self.logger = logger

    def load_default_config(self, type):
        self._log("loading default {} config".format(type))
        class_ = self.get_config_class(type)
        if class_ is None:
            raise ConfigException("Invalid type specified: {}".format(type))
        self.config = class_()

    def load_config_from_file(self, loader=yaml.safe_load):
        if not os.path.isfile(self.config_file_path):
            raise ConfigException("config file {} does not exist".format(self.config_file_path))
        try:
            self._log("reading config file {} from disk".format(self.config_file_path))
            with open(self.config_file_path, 'r') as f:
                conf = loader(f)
        except (yaml.YAMLError, IOError) as e:
            raise ConfigException("error reading config file {}: {}".format(
                                  self.config_file_path, e))
        if not isinstance(conf, dict) or "type" not in conf:
            raise ConfigException("error reading config file {}: could not identify a 'type'".
                                  format(self.config_file_path))
        class_ = self.get_config_class(conf["type"])
        if class_ is None:
            raise ConfigException("error reading config file {}: invalid value for type: '{}'".
                                  format(self.config_file_path, conf["type"]))

        valid, error = class_.is_valid_dict(conf)
        if not valid:
            raise ConfigException("{} config file {} not valid: {}.".format(
                                  conf["type"], self.config_file_path, error))

        self.config = class_.make_config_from_dict(conf)

    def remove_config_file(self):
        os.remove(self.config_file_path)

    def write(self, writer=partial(yaml.safe_dump, default_flow_style=False)):
        # create directory if necessary
        dir_ = os.path.dirname(self.config_file_path)
        if not os.path.isdir(dir_):
            self._log("creating directory to write {} config file: {}".format(self.config.type, dir_))
            try:
                os.makedirs(dir_)
            except OSError as e:
                raise ConfigException("Could not create directories "
                                      "for {} when attempting to write {} config file: {}".format(dir_,
                                                                                                  self.config.type, e))
        # write file
        try:
            with open(self.config_file_path, 'w') as f:
                self._log("writing {} config file to disk at {}".format(self.config.type,
                                                                        self.config_file_path))
                writer(self.config.to_dict(), f)
        except (yaml.YAMLError, IOError) as e:
            raise ConfigException("Could not write {} config file to disk at {}: {}".format(self.config.type,
                                  self.config_file_path, e))

    @staticmethod
    def get_config_class(type):
        if type == "global":
            return GlobalConfig
        return None

    def _log(self, msg, level=logging.INFO):
        if self.logger:
            self.logger.log(level, msg)


class ConfigException(Exception):

    def __init__(self, message):
        self.message = message
        super(ConfigException, self).__init__(message)


def default_config_dir():
    return os.path.join(click.get_app_dir("spell", force_posix=True))
