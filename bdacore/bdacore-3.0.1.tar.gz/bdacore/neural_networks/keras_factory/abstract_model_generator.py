from abc import ABCMeta, abstractmethod

__author__ = "VLE"
__copyright__ = "Copyright 2017, OCTO Technology"
__version__ = "1.0"
__email__ = "vlevorato@octo.com"


class KerasFactory:
    """
    Abstract class template for all keras neural nets factories
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def create_model(self, **kwargs):
        pass
