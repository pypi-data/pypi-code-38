import os

from ievv_opensource.utils.ievvbuildstatic import pluginbase
from ievv_opensource.utils.ievvbuildstatic.filepath import AbstractDjangoAppPath
from ievv_opensource.utils.shellcommandmixin import ShellCommandError
from ievv_opensource.utils.shellcommandmixin import ShellCommandMixin


class Plugin(pluginbase.Plugin, ShellCommandMixin):
    """
    Browserify javascript bundler plugin.

    Examples:

        Simple example::

            IEVVTASKS_BUILDSTATIC_APPS = ievvbuildstatic.config.Apps(
                ievvbuildstatic.config.App(
                    appname='demoapp',
                    version='1.0.0',
                    plugins=[
                        ievvbuildstatic.browserify_jsbuild.Plugin(
                            sourcefile='app.js',
                            destinationfile='app.js',
                        ),
                    ]
                )
            )

        Custom source folder example::

            IEVVTASKS_BUILDSTATIC_APPS = ievvbuildstatic.config.Apps(
                ievvbuildstatic.config.App(
                    appname='demoapp',
                    version='1.0.0',
                    plugins=[
                        ievvbuildstatic.browserify_jsbuild.Plugin(
                            sourcefolder=os.path.join('scripts', 'javascript', 'api'),
                            sourcefile='api.js',
                            destinationfile='api.js',
                        ),
                    ]
                )
            )
    """
    name = 'browserify_jsbuild'
    default_group = 'js'

    def __init__(self, sourcefile, destinationfile,
                 sourcefolder=os.path.join('scripts', 'javascript'),
                 destinationfolder=os.path.join('scripts'),
                 extra_watchfolders=None,
                 extra_import_paths=None,
                 sourcemap=True,
                 **kwargs):
        """
        Parameters:
            sourcefile: The source file relative to ``sourcefolder``.
            destinationfile: Path to destination file relative to ``destinationfolder``.
            sourcefolder: The folder where ``sourcefiles`` is located relative to
                the source folder of the :class:`~ievv_opensource.utils.ievvbuild.config.App`.
                Defaults to ``scripts/javascript``.
            destinationfolder: The folder where ``destinationfile`` is located relative to
                the destination folder of the :class:`~ievv_opensource.utils.ievvbuild.config.App`.
                Defaults to ``scripts/``.
            extra_watchfolders: List of extra folders to watch for changes.
                Relative to the source folder of the
                :class:`~ievv_opensource.utils.ievvbuild.config.App`.
            **kwargs: Kwargs for :class:`ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin`.
        """
        super(Plugin, self).__init__(**kwargs)
        self.sourcefile = sourcefile
        self.destinationfile = destinationfile
        self.destinationfolder = destinationfolder
        self.sourcefolder = sourcefolder
        self.extra_watchfolders = extra_watchfolders or []
        self.sourcemap = sourcemap
        self.extra_import_paths = extra_import_paths or []

    def get_sourcefile_path(self):
        return self.app.get_source_path(self.sourcefolder, self.sourcefile)

    def get_destinationfile_path(self):
        return self.app.get_destination_path(self.destinationfolder, self.destinationfile)

    def get_default_import_paths(self):
        return ['node_modules']

    def get_import_paths(self):
        return self.get_default_import_paths() + self.extra_import_paths

    def _get_import_paths_as_strlist(self):
        import_paths = []
        for path in self.get_import_paths():
            if isinstance(path, AbstractDjangoAppPath):
                path = path.abspath
            import_paths.append(path)
        return import_paths

    def install(self):
        """
        Installs the ``browserify`` NPM package.

        The package is installed with no version specified, so you
        probably want to freeze the version using the
        :class:`ievv_opensource.utils.ievvbuildstatic.npminstall.Plugin` plugin.
        """
        self.app.get_installer('npm').queue_install(
            'browserify', installtype='dev')
        if self.app.apps.is_in_production_mode():
            self.app.get_installer('npm').queue_install(
                'uglifyify', installtype='dev')

    def get_browserify_executable(self):
        return self.app.get_installer('npm').find_executable('browserify')

    def get_browserify_extra_args(self):
        """
        Get extra browserify args.

        Override this in subclasses to add transforms and such.
        """
        return []

    def get_browserify_production_args(self):
        return [
            '-t', '[', 'uglifyify', ']',
            '-g', 'uglifyify',
        ]

    def make_browserify_args(self):
        """
        Make browserify args list.

        Adds the following in the listed order:

        - ``-d`` if the ``sourcemap`` kwarg is ``True``.
        - the source file.
        - ``-d <destination file path>``.
        - whatever :meth:`.get_browserify_extra_args` returns.

        Should normally not be extended. Extend :meth:`.get_browserify_extra_args`
        instead.
        """
        args = []
        if self.sourcemap:
            args.append('-d')
        args.extend([
           self.get_sourcefile_path(),
           '-o', self.get_destinationfile_path(),
        ])
        args.extend(self.get_browserify_extra_args())
        if self.app.apps.is_in_production_mode():
            args.extend(self.get_browserify_production_args())
        return args

    def make_browserify_executable_environment(self):
        environment = os.environ.copy()
        environment.update({
            'NODE_PATH': ':'.join(self._get_import_paths_as_strlist())
        })
        return environment

    def post_run(self):
        """
        Called at the start of run(), after the initial command start logmessage,
        but before any other code is executed.

        Does nothing by default, but subclasses can hook in
        configuration code here if they need to generate config
        files, perform validation of file structure, etc.
        """

    def run(self):
        self.get_logger().command_start(
            'Running browserify with {sourcefile} as input and {destinationfile} as output'.format(
                sourcefile=self.get_sourcefile_path(),
                destinationfile=self.get_destinationfile_path()))
        self.post_run()
        executable = self.get_browserify_executable()
        destination_folder = self.app.get_destination_path(self.destinationfolder)
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        try:
            self.run_shell_command(executable, args=self.make_browserify_args(),
                                   _cwd=self.app.get_source_path(),
                                   _env=self.make_browserify_executable_environment())
        except ShellCommandError:
            self.get_logger().command_error('browserify build FAILED!')
        else:
            self.get_logger().command_success('browserify build succeeded :)')

    def get_extra_watchfolder_paths(self):
        return map(self.app.get_source_path, self.extra_watchfolders)

    def get_watch_folders(self):
        """
        We only watch the folder where the javascript is located,
        so this returns the absolute path of the ``sourcefolder``.
        """
        folders = [self.app.get_source_path(self.sourcefolder)]
        if self.extra_watchfolders:
            folders.extend(self.get_extra_watchfolder_paths())
        return folders

    def get_watch_extensions(self):
        """
        Returns a list of the extensions to watch for in watch mode.

        Defaults to ``['js']``.

        Unless you have complex needs, it is probably easier to override
        this than overriding
        :meth:`~ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin.get_watch_regexes`.
        """
        return ['js']

    def get_watch_regexes(self):
        return ['^.+[.]({extensions})'.format(
            extensions='|'.join(self.get_watch_extensions()))]

    def __str__(self):
        return '{}({})'.format(super(Plugin, self).__str__(), self.sourcefolder)
