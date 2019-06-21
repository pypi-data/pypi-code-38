import logging


class BaseBackend(object):
    def __init__(self, *args, **kwargs):
        pass

    @property
    def logger(self):
        return logging.getLogger(f'{__name__}.{self.__class__.__name__}')

    def ls(self):
        """List the available environments"""
        raise NotImplementedError()

    def read(self, name: str):
        """Read a specific environment"""
        raise NotImplementedError()

    def rm(self, name: str):
        """
        Removes an environment from the backend

        Args:
            name: name of the environment to remove
        """
        raise NotImplementedError()

    def write(self, name: str, path: str):
        """
        Writes the environment to the backend

        Args:
            name: the environment name
            path: the path to the config on disk
        """
        raise NotImplementedError()
