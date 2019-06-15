import yaml

from abc import ABC, abstractmethod

from py_buildsystem.common import logger


class ConfigReader(ABC):

    def __init__(self, config_yaml_file):
        self.read_config_file(config_yaml_file)

        self._check_config()

    def read_config_file(self, config_yaml_file):
        try:
            with open(config_yaml_file, 'r') as config_file:
                self.configuration = yaml.load(config_file)
        except FileNotFoundError:
            logger.error('Given configuration file does not exist.')
            exit(-1)

    @abstractmethod
    def _check_config(self):
        pass  # pragma: no cover
