import os

from .base import ConfigStoreBase


def _config_files(path):
    for dir_entry in os.scandir(path):
        if dir_entry.is_file() and dir_entry.name.endswith(".conf"):
            yield dir_entry.path


class FileStore(ConfigStoreBase):
    __slots__ = ["base_directory", "configuration"]

    def __init__(self, parser, arguments):
        """Initialize connection to filestore

        :param parser: Configuration file/data parser
        :type parser: minty.config.parser.Base
        :param directory: location of configuration files
        :type directory: str
        """

        self.parser = parser
        self.base_directory = arguments["directory"]

        self._load_config()

    def _load_config(self):
        new_config = {}

        for configfile in _config_files(self.base_directory):
            self.logger.info(f"Reading configuration from '{configfile}")
            with open(configfile, "r", encoding="utf-8") as file:
                content = file.read()

            config_data = self.parser.parse(content)

            for (key, instance_config) in config_data.items():
                self.logger.info(f"Found main configuration '{key}'")
                new_config[key] = instance_config

                try:
                    aliases = [
                        alias.strip()
                        for alias in instance_config["aliases"].split(",")
                    ]
                except KeyError:
                    # "aliases" is an optional configuration item
                    aliases = []

                for alias in aliases:
                    self.logger.info(f"Found alias configuration '{alias}'")
                    new_config[alias] = instance_config

        self.configuration = new_config

    def retrieve(self, name: str) -> str:
        """Retrieve configuration from a file

        :param name: base name of the configuration file
        :type name: str
        :return: configuration file contents
        :rtype: str
        """

        super().retrieve(name)

        return self.configuration[name]
