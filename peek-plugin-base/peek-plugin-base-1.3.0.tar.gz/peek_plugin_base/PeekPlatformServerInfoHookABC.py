from abc import ABCMeta, abstractmethod


class PeekPlatformServerInfoHookABC(metaclass=ABCMeta):
    """ Peek Platform Server Info Hook

    This ABC provides information for plugins that want to connect to their own code
    running on the server service, via the inter peek service HTTP.

    """

    @property
    @abstractmethod
    def peekServerHttpPort(self) -> int:
        """ Peek Server HTTP Port

        :return: The TCP Port of the Peek Servers HTTP Service (not the admin webapp site)
        """

    @property
    @abstractmethod
    def peekServerHost(self) -> str:
        """ Peek Server Host

        :return: The IP address of the server where the peek server service is running.

        """
