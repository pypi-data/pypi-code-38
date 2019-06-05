from abc import ABCMeta, abstractmethod

class AbstractScaleIn(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def scalein(self, command):
        pass
