import os
import shutil

from future.utils import python_2_unicode_compatible

from ievv_opensource.utils.ievvbuildstatic.options_mixin import OptionsMixin
from ievv_opensource.utils.ievvbuildstatic.watcher import WatchdogWatchConfig
from ievv_opensource.utils.logmixin import LogMixin


@python_2_unicode_compatible
class Plugin(LogMixin, OptionsMixin):
    """
    Base class for all plugins in ``ievvbuildstatic``.
    """

    #: The name of the plugin.
    name = None

    #: The default group of the plugin
    #: The default value for the ``group`` kwarg for :meth:`.__init__``.
    default_group = None

    def __init__(self, group=None):
        """

        Args:
            group: The group of the plugin. Defaults to :obj:`~.Plugin.default_group`.
                If this is ``None``, the plugin can not be skipped when building
                an app.

                You can use any value for groups, but these groups are
                convenient because the ``ievv buildstatic`` command has
                command line options that makes it easier to skip them:

                - ``"css"``: Should be used for plugins that build css.
                  Skipped when running ``ievv buildstatic``
                  with ``--skip-css``.
                - ``"js"``: Should be used for plugins that build javascript.
                  Skipped when running ``ievv buildstatic``
                  with ``--skip-js``.
                - ``"jstest"``: Should be used for plugins that run automatic tests for javascript code.
                  Should also be used for tests in languages that compile to javascript
                  such as TypeScript and CoffeeScript.
                  Skipped when running ``ievv buildstatic`` with ``--skip-jstests`` or ``--skip-js``.
                - ``"slow-jstest"``: Should be used instead of ``"jstest"`` for very
                  slow tests.
                  Skipped when running ``ievv buildstatic`` with ``--skip-slow-jstests``,
                  ``--skip-jstests`` or ``--skip-js``.
        """
        self.app = None
        self.group = group or self.default_group
        self._temporary_files_and_directories = set()

    def get_loglevel(self):
        return self.app.apps.loglevel

    def get_command_error_message(self):
        return self.app.apps.command_error_message

    def install(self):
        """
        Install any packages required for this plugin.

        Should use :meth:`ievv_opensource.utils.ievvbuild.config.App.get_installer`.

        Examples:

            Install an npm package::

                def install(self):
                    self.app.get_installer('npm').install(
                        'somepackage')
                    self.app.get_installer('npm').install(
                        'otherpackage', version='~1.0.0')
        """

    def post_install(self):
        """
        Called just like install, but after all apps has finished installing.
        """

    def run(self):
        """
        Run the plugin. Put the code executed by the plugin each time files
        change here.
        """
        pass

    def runwrapper(self):
        try:
            self.run()
        except:
            self.after_run_cleanup()
            raise
        else:
            self.after_run_cleanup()

    def after_run_cleanup(self):
        if not self.app.keep_temporary_files:
            self.clean_temporary_files()

    def watch(self):
        """
        Configure watching for this plugin.

        You normally do not override this method, instead you override
        :meth:`.get_watch_folders` and :meth:`.get_watch_regexes`.

        Returns:
            WatchdogWatchConfig: A :class:`ievv_opensource.utils.ievvbuildstatic.watcher.WatchConfig`
                object if you want to watch for changes in this plugin, or ``None`` if you do not
                want to watch for changes.
        """
        watchfolders = self.get_watch_folders()
        if watchfolders:
            watchregexes = self.get_watch_regexes()
            return WatchdogWatchConfig(
                watchfolders=watchfolders,
                watchregexes=watchregexes,
                plugin=self)
        else:
            return None

    def get_watch_regexes(self):
        """
        Get the regex used when watching for changes to files.

        Defaults to a regex matching any files.
        """
        return [r'^.*$']

    def get_watch_folders(self):
        """
        Get folders to watch for changes when using ``ievv buildstatic --watch``.

        Defaults to an empty list, which means that no watching thread is started
        for the plugin.

        The folder paths must be absolute, so in most cases you should
        use ``self.app.get_source_path()`` (see
        :meth:`ievv_opensource.utils.ievvbuildstatic.config.App#get_source_path`)
        to turn user provided relative folder names into absolute paths.
        """
        return []

    def get_logger_name(self):
        return '{}.{}'.format(self.app.get_logger_name(), self.name)

    def __str__(self):
        return self.get_logger_name()

    def make_temporary_build_directory(self):
        """
        Make a temporary directory that you can use for building something.

        Returns:
            str: The absolute path of the new directory.
        """
        path = self.app.make_temporary_build_directory(self.name)
        self.register_temporary_file_or_directory(path)
        # Register the root temporary directory for the app as a temporary directory
        # - we do not get problems with duplicates - the registry is a set.
        self.register_temporary_file_or_directory(self.app.get_temporary_build_directory_path())
        return path

    def register_temporary_file_or_directory(self, absolute_path):
        """
        Register a temporary file or directory.

        This will automatically be cleaned after run() is finished (even if it crashes)
        if the app uses ``keep_temporary_files=False`` (the default).
        """
        self._temporary_files_and_directories.add(absolute_path)

    def clean_temporary_files(self):
        for absolute_path in self._temporary_files_and_directories:
            if os.path.exists(absolute_path):
                if os.path.isdir(absolute_path):
                    shutil.rmtree(absolute_path)
                else:
                    os.remove(absolute_path)

    def add_deferred_success(self, message):
        self.app.add_deferred_success('[{}] {}'.format(self.name, message))

    def add_deferred_warning(self, message):
        self.app.add_deferred_warning('[{}] {}'.format(self.name, message))
