from abc import ABCMeta, abstractmethod

class AbstractKeyValueStore:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get(self, key):
        pass

    @abstractmethod
    def set(self, key, value):
        pass

    @abstractmethod
    def getAll(self):
        pass

    @abstractmethod
    def rem(self, key):
        pass

    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def append(self, key, value):
        pass

    @abstractmethod
    def exists(self, key):
        pass
