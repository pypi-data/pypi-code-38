import os


class Pathfinder:
    """Constructs relative and absolute paths based on the QSA
    configuration.
    """

    def __init__(self, workdir):
        self.workdir = workdir

    def abspath(self, path):
        """Converts a path relative to the QSA working directory to an
        absolute path.
        """
        return os.path.join(self.workdir,
            os.path.normpath(path))

    def exists(self, path):
        """Return a boolean indicating if the filepath in the QSA
        managed project exists.
        """
        path = os.path.normpath(path)
        return os.path.exists(os.path.join(self.workdir, path))
