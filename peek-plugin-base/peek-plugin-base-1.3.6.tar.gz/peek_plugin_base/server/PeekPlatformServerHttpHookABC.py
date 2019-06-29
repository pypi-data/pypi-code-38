from abc import ABCMeta

from txhttputil.site.BasicResource import BasicResource
from txhttputil.site.FileUnderlayResource import FileUnderlayResource


class PeekPlatformServerHttpHookABC(metaclass=ABCMeta):
    """ Peek Platform Server HTTP Hook

    The methods provided by this class apply to the HTTP service that provides
    resources (vortex, etc) beween the server and the agent, worker and client.

    These resources will not be availible to the web apps.

    """

    def __init__(self):
        self.__rootServerResource = FileUnderlayResource()

    def addServerStaticResourceDir(self, dir: str) -> None:
        """ Add Server Static Resource Directory

        Calling this method sets up directory :code:`dir` to be served by the site.

        :param dir: The file system directory to be served.
        :return: None
        """
        self.__rootServerResource.addFileSystemRoot(dir)

    def addServerResource(self, pluginSubPath: bytes, resource: BasicResource) -> None:
        """ Add Server Resource

        Add a cusotom implementation of a served http resource.

        :param pluginSubPath: The resource path where you want to serve this resource.
        :param resource: The resource to serve.
        :return: None

        """
        pluginSubPath = pluginSubPath.strip(b'/')
        self.__rootServerResource.putChild(pluginSubPath, resource)

    @property
    def rootServerResource(self) -> BasicResource:
        """ Server Root Resource

        This returns the root site resource for this plugin.

        """
        return self.__rootServerResource
