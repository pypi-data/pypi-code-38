import os

from ievv_opensource.utils.ievvbuildstatic import pluginbase
from ievv_opensource.utils.shellcommandmixin import ShellCommandMixin, ShellCommandError


class Plugin(pluginbase.Plugin, ShellCommandMixin):
    """
    LESS build plugin --- builds .less files into css, and supports watching
    for changes.

    Examples:

        Very simple example where the source file is in
        ``demoapp/staticsources/styles/theme.less``::

            IEVVTASKS_BUILDSTATIC_APPS = ievvbuildstatic.config.Apps(
                ievvbuildstatic.config.App(
                    appname='demoapp',
                    version='1.0.0',
                    plugins=[
                        ievvbuildstatic.lessbuild.Plugin(sourcefile='theme.less'),
                    ]
                )
            )

        A more complex example that builds a django-cradmin theme
        where sources are split in multiple directories, and
        the bower install directory is on the less path
        (the example also uses :class:`ievv_opensource.utils.ievvbuildstatic.bowerinstall.Plugin`)::

            IEVVTASKS_BUILDSTATIC_APPS = ievvbuildstatic.config.Apps(
                ievvbuildstatic.config.App(
                    appname='demoapp',
                    version='1.0.0',
                    plugins=[
                        ievvbuildstatic.bowerinstall.Plugin(
                            packages={
                                'bootstrap': '~3.1.1'
                            }
                        ),
                        ievvbuildstatic.lessbuild.Plugin(
                            sourcefolder='styles/cradmin_theme_demoapp',
                            sourcefile='theme.less',
                            other_sourcefolders=[
                                'styles/cradmin_base',
                                'styles/cradmin_theme_default',
                            ],
                            less_include_paths=[
                                'bower_components',
                            ]
                        )
                    ]
                )
            )
    """

    name = 'lessbuild'
    default_group = 'css'

    def __init__(self, sourcefile, sourcefolder='styles',
                 other_sourcefolders=None,
                 less_include_paths=None,
                 **kwargs):
        """
        Parameters:
            sourcefile: Main source file (the one including all other less files)
                relative to ``sourcefolder``.
            sourcefolder: The folder where ``sourcefile`` is located relative to
                the source folder of the :class:`~ievv_opensource.utils.ievvbuild.config.App`.
            less_include_paths: Less include paths as a list. Paths are relative
                to the source folder of the :class:`~ievv_opensource.utils.ievvbuild.config.App`.
            **kwargs: Kwargs for :class:`ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin`.
        """
        super(Plugin, self).__init__(**kwargs)
        self.sourcefolder = sourcefolder
        self.other_sourcefolders = other_sourcefolders
        self.less_include_paths = less_include_paths
        self.sourcefile = os.path.join(sourcefolder, sourcefile)

    def get_sourcefile_path(self):
        return self.app.get_source_path(self.sourcefile)

    def get_destinationfile_path(self):
        return self.app.get_destination_path(
            self.sourcefile, new_extension='.css')

    def get_other_sourcefolders_paths(self):
        return map(self.app.get_source_path, self.other_sourcefolders)

    def format_less_include_paths(self):
        if self.less_include_paths:
            return ':'.join(map(self.app.get_source_path, self.less_include_paths))
        else:
            return ''

    def get_less_version(self):
        return None

    def install(self):
        self.app.get_installer('npm').queue_install(
            'less', version=self.get_less_version())

    def run(self):
        self.get_logger().command_start('Building {}.'.format(self.get_sourcefile_path()))
        executable = self.app.get_installer('npm').find_executable('lessc')
        kwargs = {}
        less_include_paths = self.format_less_include_paths()
        if less_include_paths:
            kwargs['include_path'] = less_include_paths
            self.get_logger().info('Using --include-path={}'.format(less_include_paths))
        try:
            self.run_shell_command(executable,
                                   args=[
                                       self.get_sourcefile_path(),
                                       self.get_destinationfile_path()
                                   ],
                                   kwargs=kwargs)
        except ShellCommandError:
            self.get_logger().command_error('LESS build FAILED!')
        else:
            self.get_logger().command_success('LESS build successful :)')

    def get_watch_folders(self):
        """
        We only watch the folder where the less sources are located,
        so this returns the absolute path of the ``sourcefolder``.
        """
        folders = [self.app.get_source_path(self.sourcefolder)]
        if self.other_sourcefolders:
            folders.extend(self.get_other_sourcefolders_paths())
        return folders

    def get_watch_regexes(self):
        return ['^.+[.]less$']

    def __str__(self):
        return '{}({})'.format(super(Plugin, self).__str__(), self.sourcefile)
