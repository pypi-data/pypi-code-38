from abc import ABCMeta, abstractmethod

from peek_plugin_livedb.server.LiveDBReadApiABC import LiveDBReadApiABC
from peek_plugin_livedb.server.LiveDBWriteApiABC import LiveDBWriteApiABC


class LiveDBApiABC(metaclass=ABCMeta):
    @property
    @abstractmethod
    def writeApi(self) -> LiveDBWriteApiABC:
        """ LiveDB Write API

        This API is for all the methods that make changes to the LiveDB

        :return: A reference to the LiveDBWriteApiABC instance

        """

    @property
    @abstractmethod
    def readApi(self) -> LiveDBReadApiABC:
        """ LiveDB Read API

        This API is for all the methods to read changes from the LiveDB

        :return: A reference to the LiveDBReadApiABC instance

        """
