import os
import pathlib

from PySide2 import QtCore

import vstreamer_utils


def get_config_directory(subdir_name):
    uid = os.getuid()
    base_config_dir = None
    if uid == 0:
        base_config_dir = "/etc"
    else:
        base_config_dir = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.GenericConfigLocation)
    return pathlib.Path(base_config_dir) / subdir_name


class ConfigException(Exception):
    def __init__(self, message, filename=None):
        super().__init__(message + "'%s'" % filename)
        self.filename = filename


class Configuration:
    class Path:
        def __init__(self, directory, file):
            self.directory = directory
            self.file = file

    class Config:
        BASE_DIRECTORY = "Config/BaseDirectory"
        STARTING_PORT = "Config/StartingPort"

        def __init__(self):
            self.base_directory = "/srv/video"
            self.starting_port = vstreamer_utils.SERVER_PORT

    def __init__(self, config_directory):
        self.path = Configuration.Path(pathlib.Path(config_directory), pathlib.Path(config_directory) / "config.ini")
        self.config = Configuration.Config()

        self._create_missing()
        self.read_config()

    def read_config(self):
        settings = QtCore.QSettings(str(self.path.file), QtCore.QSettings.IniFormat)
        self.config.base_directory = settings.value(Configuration.Config.BASE_DIRECTORY, self.config.base_directory)
        self.config.starting_port = int(settings.value(Configuration.Config.STARTING_PORT, str(self.config.starting_port)))
        if settings.status() != QtCore.QSettings.NoError:
            raise ConfigException("Could not read configuration file", str(self.path.file))
        vstreamer_utils.log_info("Read configuration from '%s'" % str(self.path.file))

    def write_config(self):
        settings = QtCore.QSettings(str(self.path.file), QtCore.QSettings.IniFormat)
        settings.setValue(Configuration.Config.BASE_DIRECTORY, self.config.base_directory)
        settings.setValue(Configuration.Config.STARTING_PORT, str(self.config.starting_port))
        settings.sync()
        if settings.status() != QtCore.QSettings.NoError:
            raise ConfigException("Could not write configuration file", str(self.path.file))
        vstreamer_utils.log_info("Saved configuration to '%s'" % str(self.path.file))

    def _create_missing(self):
        if not self.path.directory.exists():
            self.path.directory.mkdir(parents=True, exist_ok=True)
        if not self.path.file.exists():
            self.path.file.touch(exist_ok=True)
