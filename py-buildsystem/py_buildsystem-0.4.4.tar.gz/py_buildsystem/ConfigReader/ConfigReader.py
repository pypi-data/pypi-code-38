import yaml

from abc import ABC, abstractmethod


class ConfigReader(ABC):
    def __init__(self, config_yaml_file):
        self.read_config_file(config_yaml_file)

        self._check_config()

    def read_config_file(self, config_yaml_file):
        try:
            with open(config_yaml_file, 'r') as config_file:
                self.configuration = yaml.load(config_file)
        except FileNotFoundError:
            raise Exception('Given configuration file does not exist.')

    @abstractmethod
    def _check_config(self):
        pass  # pragma: no cover
