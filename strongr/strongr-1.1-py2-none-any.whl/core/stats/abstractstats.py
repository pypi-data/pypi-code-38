from abc import ABCMeta, abstractmethod

class AbstractStats():
    __metaclass__ = ABCMeta

    @abstractmethod
    def incr(self, namespace, amount, rate=None):
        pass

    @abstractmethod
    def decr(self, namespace, amount, rate=None):
        pass

    @abstractmethod
    def timing(self, namespace, timems):
        pass

    @abstractmethod
    def time(self, namespace):
        """
        Should return a context manager
        :param namespace:
        :return:
        """
        pass

    @abstractmethod
    def gauge(self, namespace, amount, rate=False, delta=False):
        pass

    @abstractmethod
    def set(self, namespace, arr):
        pass
