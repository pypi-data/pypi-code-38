from abc import abstractmethod, ABCMeta

from py_buildsystem.ConfigReader.ConfigReader import ConfigReader


class Step(ConfigReader):
    __metaclass__ = ABCMeta

    @abstractmethod
    def perform(self):
        pass  # pragma: no cover

    @abstractmethod
    def get_type(self):
        pass  # pragma: no cover

    def get_name(self):
        return self.step_name

    def get_exit_code(self):
        return self.exit_code
