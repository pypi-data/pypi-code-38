import json
import logging
import os
import shutil
import time
from collections import OrderedDict

from django.apps import apps
from ievv_opensource.utils.ievvbuildstatic import filepath
from ievv_opensource.utils.ievvbuildstatic.installers.yarn import YarnInstaller
from ievv_opensource.utils.ievvbuildstatic.watcher import WatchConfigPool
from ievv_opensource.utils.logmixin import LogMixin, Logger

from . import docbuilders


class App(LogMixin):
    """
    Configures how ``ievv buildstatic`` should build the static files for a Django app.
    """
    def __init__(self, appname, version, plugins,
                 sourcefolder='staticsources',
                 destinationfolder='static',
                 keep_temporary_files=False,
                 installers_config=None,
                 docbuilder_classes=None,
                 default_skipgroups=None,
                 default_includegroups=None):
        """
        Parameters:
            appname: Django app label (I.E.: ``myproject.myapp``).
            plugins: Zero or more :class:`ievv_opensource.utils.ievvbuild.pluginbase.Plugin`
                objects.
            sourcefolder: The folder relative to the app root folder where
                static sources (I.E.: less, coffescript, ... sources) are located.
                Defaults to ``staticsources``.
        """
        self.apps = None
        self.version = version
        self.appname = appname
        self.sourcefolder = sourcefolder
        self.destinationfolder = destinationfolder
        self.installers = {}
        self.plugins = []
        self.docbuilder_classes = docbuilder_classes or self.get_default_docbuilder_classes()
        self.keep_temporary_files = keep_temporary_files
        self.default_skipgroups = default_skipgroups or []
        self.default_includegroups = default_includegroups or []
        self.installers_config = self._make_installers_config(
            installers_config_overrides=installers_config)
        for plugin in plugins:
            self.add_plugin(plugin)

    def _make_installers_config(self, installers_config_overrides):
        installers_config = {
            'npm': {
                'installer_class': YarnInstaller
            },
        }
        installers_config_overrides = installers_config_overrides or {}
        for alias, config in installers_config_overrides.items():
            overrides = installers_config_overrides.get(alias, {})
            if alias not in installers_config:
                installers_config[alias] = {}
            installers_config[alias].update(overrides)
        return installers_config

    def get_options_classes(self):
        options_classes = []
        for installer_config in self.installers_config.values():
            options_classes.append(installer_config['installer_class'])
        for plugin in self.plugins:
            options_classes.append(plugin.__class__)
        return options_classes

    def add_plugin(self, plugin):
        """
        Add a :class:`ievv_opensource.utils.ievvbuildstatic.lessbuild.Plugin`.
        """
        plugin.app = self
        self.plugins.append(plugin)

    def iterplugins(self, skipgroups=None, includegroups=None):
        skipgroups = skipgroups or self.default_skipgroups
        includegroups = includegroups or self.default_includegroups
        skipgroups = {group for group in skipgroups if group not in includegroups}
        for plugin in self.plugins:
            if includegroups and plugin.group not in includegroups:
                continue
            if plugin.group and plugin.group in skipgroups:
                continue
            yield plugin

    def run(self, skipgroups=None, includegroups=None):
        """
        Run :meth:`ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin.run`
        for all plugins within the app.
        """
        for plugin in self.iterplugins(skipgroups=skipgroups, includegroups=includegroups):
            plugin.runwrapper()

    def _make_json_appconfig_dict(self):
        return {
            'appname': self.appname,
            'version': self.version,
            'sourcefolder': self.get_source_path(),
            'destinationfolder': self.get_destination_path(),
            'keep_temporary_files': self.keep_temporary_files,
            'is_in_production_mode': self.apps.is_in_production_mode()
        }

    def _get_json_appconfig_path(self):
        return self.get_source_path('ievv_buildstatic.appconfig.json')

    def _save_json_appconfig(self, appconfig_dict):
        config_path = self._get_json_appconfig_path()
        self.get_logger().debug('Creating {config_path}'.format(config_path=config_path))
        open(config_path, 'w').write(
            json.dumps(appconfig_dict, indent=2, sort_keys=True)
        )

    def add_pluginconfig_to_json_config(self, plugin_name, config_dict):
        appconfig_dict = json.loads(open(self._get_json_appconfig_path(), 'r').read())
        appconfig_dict[plugin_name] = config_dict
        self._save_json_appconfig(appconfig_dict=appconfig_dict)

    def install(self, skipgroups=None, includegroups=None):
        """
        Run :meth:`ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin.install`
        for all plugins within the app.
        """
        self._save_json_appconfig(appconfig_dict=self._make_json_appconfig_dict())
        for alias in self.installers_config.keys():
            installer = self.get_installer(alias=alias)
            installer.initialize()
        for plugin in self.iterplugins(skipgroups=skipgroups, includegroups=includegroups):
            plugin.install()
        for installer in self.installers.values():
            installer.install()
        for plugin in self.iterplugins(skipgroups=skipgroups, includegroups=includegroups):
            plugin.post_install()

    def get_app_config(self):
        """
        Get the AppConfig for the Django app.
        """
        if not hasattr(self, '_app_config'):
            self._app_config = apps.get_app_config(self.appname)
        return self._app_config

    def get_appfolder(self):
        """
        Get the absolute path to the Django app root folder.
        """
        return self.get_app_config().path

    def get_app_path(self, apprelative_path):
        """
        Returns the path to the directory joined with the
        given ``apprelative_path``.
        """
        return os.path.join(self.get_appfolder(), apprelative_path)

    def _relative_or_absolute_path_to_absolute_path(self, relative_path_root, pathlist):
        if len(pathlist) == 1 and isinstance(pathlist[0], filepath.FilePathInterface):
            return pathlist[0].abspath
        else:
            if pathlist:
                return os.path.join(relative_path_root, *pathlist)
            else:
                return relative_path_root

    def get_source_path(self, *path):
        """
        Returns the absolute path to a folder within the source
        folder of this app or another app.

        Examples:

            Get the source path for a coffeescript file::

                self.get_source_path('mylib', 'app.coffee')

            Getting the path of a source file within another app using
            a :class:`ievv_opensource.utils.ievvbuildstatic.filepath.SourcePath`
            object (a subclass of :class:`ievv_opensource.utils.ievvbuildstatic.filepath.FilePathInterface`)
            as the path::

                self.get_source_path(
                    ievvbuildstatic.filepath.SourcePath('myotherapp', 'scripts', 'typescript', 'app.ts'))


        Args:
            *path: Zero or more strings to specify a path relative to the source folder of this app -
                same format as :func:`os.path.join`.
                A single :class:`ievv_opensource.utils.ievvbuildstatic.filepath.FilePathInterface`
                object to specify an absolute path.
        """
        sourcefolder = os.path.join(self.get_app_path(self.sourcefolder), self.appname)
        return self._relative_or_absolute_path_to_absolute_path(relative_path_root=sourcefolder,
                                                                pathlist=path)

    def make_source_relative_path(self, *path):
        return os.path.relpath(self.get_source_path(*path), start=self.get_source_path())

    def get_destination_path(self, *path, **kwargs):
        """
        Returns the absolute path to a folder within the destination
        folder of this app or another app.

        Examples:

            Get the destination path for a coffeescript file - extension
            is changed from ``.coffee`` to ``.js``::

                self.get_destination_path('mylib', 'app.coffee', new_extension='.js')

            Getting the path of a destination file within another app using
            a :class:`ievv_opensource.utils.ievvbuildstatic.filepath.SourcePath`
            object (a subclass of :class:`ievv_opensource.utils.ievvbuildstatic.filepath.FilePathInterface`)
            as the path::

                self.get_destination_path(
                    ievvbuildstatic.filepath.DestinationPath(
                        'myotherapp', '1.1.0', 'scripts', 'typescript', 'app.ts'),
                    new_extension='.js')

        Args:
            path: Path relative to the source folder.
                Same format as ``os.path.join()``.
                A single :class:`ievv_opensource.utils.ievvbuildstatic.filepath.FilePathInterface`
                object to specify an absolute path.
            new_extension: A new extension to give the destination path.
                See example below.

        """
        new_extension = kwargs.get('new_extension', None)
        destinationfolder = os.path.join(
            self.get_app_path(self.destinationfolder), self.appname, self.version)
        absolute_path = self._relative_or_absolute_path_to_absolute_path(relative_path_root=destinationfolder,
                                                                         pathlist=path)
        if new_extension is not None:
            path, extension = os.path.splitext(absolute_path)
            absolute_path = '{}{}'.format(path, new_extension)
        return absolute_path

    def watch(self, skipgroups=None, includegroups=None):
        """
        Start a watcher thread for each plugin.
        """
        watchconfigs = []
        for plugin in self.iterplugins(skipgroups=skipgroups, includegroups=includegroups):
            watchconfig = plugin.watch()
            if watchconfig:
                watchconfigs.append(watchconfig)
        return watchconfigs

    def iterinstallers(self):
        return self.installers.values()

    def get_installer(self, alias):
        """
        Get an instance of the installer configured with the provided ``alias``.

        Parameters:
            alias: A subclass of
                .
        Returns:
            ievv_opensource.utils.ievvbuildstatic.installers.base.AbstractInstaller: An instance
                of the requested installer.
        """
        installer_class = self.installers_config[alias]['installer_class']
        if installer_class.name not in self.installers:
            installer = installer_class(app=self)
            self.installers[installer_class.name] = installer
        return self.installers[installer_class.name]

    def get_logger_name(self):
        return '{}.{}'.format(self.apps.get_logger_name(), self.appname)

    def get_loglevel(self):
        return self.apps.loglevel

    def get_temporary_build_directory_path(self, *path):
        return self.get_source_path('ievvbuildstatic_temporary_build_directory', *path)

    def make_temporary_build_directory(self, name):
        """
        Make a temporary directory that you can use for building something.

        Returns:
            str: The absolute path of the new directory.
        """
        self._delete_temporary_build_directory(name)
        temporary_directory_path = self.get_temporary_build_directory_path(name)
        os.makedirs(temporary_directory_path)
        return temporary_directory_path

    def _delete_temporary_build_directory(self, name):
        """
        Delete a temporary directory created with :meth:`.make_temporary_build_directory`.
        """
        temporary_directory_path = self.get_temporary_build_directory_path(name)
        if os.path.exists(temporary_directory_path):
            shutil.rmtree(temporary_directory_path)
        base_temporary_directory = self.get_temporary_build_directory_path()
        if os.path.exists(base_temporary_directory) and len(os.listdir(base_temporary_directory)) == 0:
            shutil.rmtree(base_temporary_directory)

    def get_default_docbuilder_classes(self):
        return [
            docbuilders.npm_docbuilder.NpmDocBuilder
        ]

    def get_docbuilder(self):
        for docbuilder_class in self.docbuilder_classes:
            docbuilder = docbuilder_class(app=self)
            if docbuilder.is_available():
                return docbuilder
        return None

    def build_docs(self, output_directory):
        docbuilder = self.get_docbuilder()
        if docbuilder:
            docbuilder.build_docs(output_directory=os.path.join(output_directory, self.appname))
        else:
            self.get_logger().debug(
                'No docbuilders found for {appname}. Tried the following docbuilders: {docbuilders}'.format(
                    appname=self.appname,
                    docbuilders=', '.join(
                        docbuilder_class.name
                        for docbuilder_class in self.docbuilder_classes)
                ))

    def add_deferred_success(self, message):
        self.apps.add_deferred_success('[{}] {}'.format(self.appname, message))

    def add_deferred_warning(self, message):
        self.apps.add_deferred_warning('[{}] {}'.format(self.appname, message))


class Apps(LogMixin):
    """
    Basically a list around :class:`.App` objects.
    """
    MODE_DEVELOP = 'develop'
    MODE_PRODUCTION = 'production'

    def __init__(self, *apps, **kwargs):
        """
        Parameters:
            apps: :class:`.App` objects to add initially. Uses :meth:`.add_app` to add the apps.
        """
        self.apps = OrderedDict()
        self.loglevel = Logger.DEBUG
        self.command_error_message = None
        self.help_header = kwargs.pop('help_header', None)
        self.mode = self.MODE_DEVELOP
        self._warnings = []
        self._successes = []
        self.options = {}
        for app in apps:
            self.add_app(app)

    def get_loglevel(self):
        return self.loglevel

    def get_command_error_message(self):
        return self.command_error_message

    def add_app(self, app):
        """
        Add an :class:`.App`.
        """
        app.apps = self
        self.apps[app.appname] = app

    def get_app(self, appname):
        """
        Get app by appname.
        """
        return self.apps[appname]

    def install(self, appnames=None, skipgroups=None, includegroups=None):
        """
        Run :meth:`ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin.install`
        for all plugins within all :class:`apps <.App>`.
        """
        for app in self.iterapps(appnames=appnames):
            app.install(skipgroups=skipgroups, includegroups=includegroups)

    def log_help_header(self):
        if self.help_header:
            self.get_logger().infobox(self.help_header)

    def validate_appnames(self, appnames):
        for appname in appnames:
            if appname not in self.apps:
                raise ValueError('Invalid appname: {}'.format(appname))

    def iterapps(self, appnames=None):
        """
        Get an interator over the apps.
        """
        for app in self.apps.values():
            include = not appnames or app.appname in appnames
            if include:
                yield app

    def run(self, appnames=None, skipgroups=None, includegroups=None):
        """
        Run :meth:`ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin.run`
        for all plugins within all :class:`apps <.App>`.
        """
        for app in self.iterapps(appnames=appnames):
            app.run(skipgroups=skipgroups, includegroups=includegroups)
        self.log_deferred_messages()

    def watch(self, appnames=None, skipgroups=None, includegroups=None):
        """
        Start watcher threads for all folders that at least one
        :class:`plugin <ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin>`
        within any of the :class:`apps <.App>` has configured to be watched for changes.

        Blocks until ``CTRL-c`` is pressed.
        """
        watchconfigpool = WatchConfigPool()
        for app in self.iterapps(appnames=appnames):
            watchconfigpool.extend(app.watch(skipgroups=skipgroups, includegroups=includegroups))
        all_observers = watchconfigpool.watch()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            for observer in all_observers:
                observer.stop()

        for observer in all_observers:
            observer.join()

    def build_docs(self, output_directory, appnames=None):
        for app in self.iterapps(appnames=appnames):
            app.build_docs(output_directory=output_directory)

    def get_logger_name(self):
        return 'ievvbuildstatic'

    def __configure_shlogger(self, loglevel, handler):
        shlogger = logging.getLogger('sh.command')
        shlogger.setLevel(loglevel)
        shlogger.addHandler(handler)
        shlogger.propagate = False

    def configure_logging(self, loglevel=None, shlibrary_loglevel=logging.WARNING,
                          command_error_message=None):
        handler = logging.StreamHandler()
        self.__configure_shlogger(loglevel=shlibrary_loglevel,
                                  handler=handler)
        self.loglevel = loglevel
        self.command_error_message = command_error_message

    def set_development_mode(self):
        self.mode = self.MODE_DEVELOP

    def set_production_mode(self):
        self.mode = self.MODE_PRODUCTION

    def is_in_production_mode(self):
        return self.mode == self.MODE_PRODUCTION

    def add_deferred_warning(self, message):
        self._warnings.append(message)

    def add_deferred_success(self, message):
        self._successes.append(message)

    def log_deferred_messages(self):
        if self._successes:
            self.get_logger().success('Success messages:')
            for message in set(self._successes):
                self.get_logger().success('- {}'.format(message))
        if self._warnings:
            self.get_logger().warning('Warnings:')
            for message in set(self._warnings):
                self.get_logger().warning('- {}'.format(message))
        self._successes = []
        self._warnings = []

    def add_cli_arguments(self, parser):
        options_classes = set()
        for app in self.iterapps():
            options_classes.update(app.get_options_classes())
        for option_class in options_classes:
            option_class.add_cli_arguments(parser=parser)

    def set_options(self, options):
        self.options = options
