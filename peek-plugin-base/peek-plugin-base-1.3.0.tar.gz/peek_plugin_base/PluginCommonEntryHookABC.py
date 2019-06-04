from abc import ABCMeta, abstractmethod

from jsoncfg.value_mappers import require_string
from peek_plugin_base.PluginPackageFileConfig import PluginPackageFileConfig


class PluginCommonEntryHookABC(metaclass=ABCMeta):
    def __init__(self, pluginName:str, pluginRootDir:str):
        self._pluginName = pluginName
        self._pluginRootDir = pluginRootDir
        self._packageCfg = PluginPackageFileConfig(pluginRootDir)

    @property
    def name(self) -> str:
        """ Plugin Name

        :return: The name of this plugin
        """
        return self._pluginName

    @property
    def rootDir(self) -> str:
        """ Plugin Root Dir

        :return: The absolute directory where the Plugin package is located.
        """
        return self._pluginRootDir

    @property
    def packageCfg(self) -> PluginPackageFileConfig:
        """ Package Config

        :return: A reference to the plugin_package.json loader object (see json-cfg)
        """
        return self._packageCfg

    @abstractmethod
    def load(self) -> None:
        """ Load

        This will be called when the plugin is loaded, just after the db is migrated.
        Place any custom initialiastion steps here.

        """

    @abstractmethod
    def start(self) -> None:
        """ Start

        This method is called by the platform when the plugin should start
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """ Stop

        This method is called by the platform to tell the peek app to shutdown and stop
        everything it's doing
        """
        pass

    @abstractmethod
    def unload(self) -> None:
        """Unload

        This method is called after stop is called, to unload any last resources
        before the PLUGIN is unlinked from the platform
        """
        pass

    @property
    def title(self) -> str:
        """ Peek App Title
        :return the title of this plugin
        """
        return self._packageCfg.config.plugin.title(require_string)
