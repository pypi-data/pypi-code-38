from __future__ import (absolute_import, division, print_function, unicode_literals)
import abc


class Connector(object, metaclass=abc.ABCMeta):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if isinstance(k, str) and not k.startswith('_'):
                setattr(self, k, v)
        self.context = kwargs

    @abc.abstractmethod
    def get(self):
        pass
