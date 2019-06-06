from pathlib import Path

from abc import ABCMeta, abstractmethod


class PeekPlatformFileStorageHookABC(metaclass=ABCMeta):
    """ Peek Platform File Storage Hook

    This ABC provides methods allowing plugins to use the file system.

    Though there is nothing in place to prevent the plugins doing what ever they like,
    they should play nice and get their allocated path from here.

    """

    @property
    @abstractmethod
    def fileStorageDirectory(self) -> Path:
        """ File Storage Directory

        This method returns a Path object providing access to the managed
        file storage location where the plugin can persistently store any files it
        wants to.

        See https://docs.python.org/3/library/pathlib.html#basic-use

        :returns: The plugins managed storage Path object.
        """
