import os

from django.apps import apps


class FilePathInterface(object):
    """
    Base interface for file path objects.

    We provide subclasses if this interface with different use cases:

    - :class:`.SourcePath`: Use this to specify a source file or folder
        in the sources directory of a :class:`ievv_opensource.utils.ievvbuildstatic.config.App`.
    - :class:`.DestinationPath`: Use this to specify a destination file or folder
        in the sources directory of a :class:`ievv_opensource.utils.ievvbuildstatic.config.App`.
    - :class:`.AbsoluteFilePath`: Use this to specify a file or folder that is
        not organized using the ievvbuildstatic directory layout.
    """
    @property
    def abspath(self):
        """
        Property that returns the absolute path to the file (or directory).

        Must be overridden in subclasses.
        """
        raise NotImplementedError()


class AbsoluteFilePath(FilePathInterface):
    """
    Absolute file path.

    Works just like :func:`os.path.join`, and we just
    assume that you provide a path that is absolute.
    """
    def __init__(self, *path):
        """

        Args:
            *path: One or more strings that make up an absolute path
                when joined with ``os.path.join(*path)``.

        Returns:

        """
        self._path = path

    @property
    def abspath(self):
        return os.path.join(*self._path)


class AbstractDjangoAppPath(FilePathInterface):
    """
    Abstract base class for file paths within a Django app.
    """
    def get_approot_path(self, appname):
        appconfig = apps.get_app_config(appname)
        return appconfig.path

    def get_approot_relative_path(self, appname, *path):
        return os.path.join(self.get_approot_path(appname=appname), *path)

    @property
    def abspath(self):
        raise NotImplementedError()


class SourcePath(AbstractDjangoAppPath):
    """
    A path to a file or directory within the source directory of
    a :class:`ievv_opensource.utils.ievvbuildstatic.config.App`.

    Assumes that the sourcefolder of the App is ``"staticsources"`` (the default).
    """
    def __init__(self, appname, *path):
        """
        Args:
            appname: The name of the Django app.
            *path: The path relative to the source directory of the
                :class:`ievv_opensource.utils.ievvbuildstatic.config.App`
                identified by ``appname``. Same format as :func:`os.path.join`.
        """
        self.appname = appname
        self.path = path

    @property
    def abspath(self):
        return self.get_approot_relative_path(self.appname, 'staticsources', self.appname, *self.path)


class DestinationPath(AbstractDjangoAppPath):
    """
    A path to a file or directory within the destination directory of
    a :class:`ievv_opensource.utils.ievvbuildstatic.config.App`.

    Assumes that the destinationfolder of the App is ``"static"`` (the default).
    """
    def __init__(self, appname, version, *path):
        """
        Args:
            appname: The name of the Django app.
            version: The version of the app.
            *path: The path relative to the destination directory of the
                :class:`ievv_opensource.utils.ievvbuildstatic.config.App`
                identified by ``appname``. Same format as :func:`os.path.join`.
        """
        self.appname = appname
        self.version = version
        self.path = path

    @property
    def abspath(self):
        return self.get_approot_relative_path(self.appname, 'static', self.appname, self.version, *self.path)


class AppPath(AbstractDjangoAppPath):
    """
    A path to a file or directory within the root directory of
    a :class:`ievv_opensource.utils.ievvbuildstatic.config.App`.
    """
    def __init__(self, appname, *path):
        """
        Args:
            appname: The name of the Django app.
            *path: The path relative to the root directory of the
                :class:`ievv_opensource.utils.ievvbuildstatic.config.App`
                identified by ``appname``. Same format as :func:`os.path.join`.
        """
        self.appname = appname
        self.path = path

    @property
    def abspath(self):
        return self.get_approot_relative_path(self.appname, *self.path)
