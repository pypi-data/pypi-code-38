import os

from compose_flow.settings import APP_ENVIRONMENTS_ROOT

from .base_backend import BaseBackend


class LocalBackend(BaseBackend):
    """
    Manages local file storage
    """
    def __init__(self, *args, root: str = None, **kwargs):
        """
        Constructor

        Args:
            root: the base directory where to look for local environment files
        """
        super().__init__(*args, **kwargs)

        self.root = root or APP_ENVIRONMENTS_ROOT

    def ls(self):
        if not os.path.exists(self.root):
            return []

        return os.listdir(self.root)

    def get_path(self, name: str) -> str:
        return os.path.join(self.root, name)

    def read(self, name: str) -> str:
        """
        Reads in the environment file
        """
        path = self.get_path(name)
        if not os.path.exists(path):
            return ''

        with open(path, 'r') as fh:
            return fh.read()

    def rm(self, name: str) -> None:
        """
        Removes an environment file
        """
        path = self.get_path(name)
        if os.path.exists(path):
            os.remove(path)

    def write(self, name: str, path: str) -> None:
        # create the directory if it does not exist
        if not os.path.exists(self.root):
            os.makedirs(self.root)

        with open(path, 'r') as fh:
            buf = fh.read()

        with open(self.get_path(name), 'w') as fh:
            fh.write(buf)
