from abc import ABCMeta, abstractmethod
from typing import Optional


class PeekPlatformCommonHookABC(metaclass=ABCMeta):

    @abstractmethod
    def getOtherPluginApi(self, pluginName:str) -> Optional[object]:
        """ Get Other Plugin Api

        Asks the plugin for it's api object and return it to this plugin.
        The API returned matches the platform service.

        :param pluginName: The name of the plugin to retrieve the API for
        :return: An instance of the other plugins API for this Peek Platform Service.

        """

    @property
    @abstractmethod
    def serviceId(self) -> str:
        """ Service ID

        Return a unique identifier for this service.
        """