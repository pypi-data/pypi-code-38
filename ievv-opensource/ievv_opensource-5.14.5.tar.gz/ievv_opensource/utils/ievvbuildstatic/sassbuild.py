from __future__ import unicode_literals
import os

from ievv_opensource.utils.ievvbuildstatic import cssbuildbaseplugin
from ievv_opensource.utils.ievvbuildstatic import filepath
from ievv_opensource.utils.ievvbuildstatic import utils
from ievv_opensource.utils.shellcommandmixin import ShellCommandError


class Plugin(cssbuildbaseplugin.AbstractPlugin):
    """
    SASS build plugin --- builds .scss files into css, and supports watching
    for changes.

    By default, we assume ``sassc`` is available on PATH, but you can
    override the path to the sassc executable by setting the
    ``IEVVTASKS_BUILDSTATIC_SASSC_EXECUTABLE`` environment variable.

    Examples:

        Very simple example where the source file is in
        ``demoapp/staticsources/styles/theme.scss``::

            IEVVTASKS_BUILDSTATIC_APPS = ievvbuildstatic.config.Apps(
                ievvbuildstatic.config.App(
                    appname='demoapp',
                    version='1.0.0',
                    plugins=[
                        ievvbuildstatic.sassbuild.Plugin(sourcefile='theme.scss'),
                    ]
                )
            )

        A more complex example that builds a django-cradmin theme
        where sources are split in multiple directories, and
        the bower install directory is on the scss path
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
                        ievvbuildstatic.sassbuild.Plugin(
                            sourcefolder='styles/cradmin_theme_demoapp',
                            sourcefile='theme.scss',
                            other_sourcefolders=[
                                'styles/cradmin_base',
                                'styles/cradmin_theme_default',
                            ],
                            sass_include_paths=[
                                'bower_components',
                            ]
                        )
                    ]
                )
            )
    """

    name = 'sassbuild'

    def __init__(self, sourcefile, sourcefolder='styles',
                 destinationfolder=None,
                 other_sourcefolders=None,
                 sass_include_paths=None,
                 sass_variables=None,
                 **kwargs):
        """
        Parameters:
            sourcefile: Main source file (the one including all other scss files)
                relative to ``sourcefolder``.
            sourcefolder: The folder where ``sourcefile`` is located relative to
                the source folder of the :class:`~ievv_opensource.utils.ievvbuild.config.App`.
                You can specify a folder in another app using
                a :class:`ievv_opensource.utils.ievvbuildstatic.filepath.SourcePath` object,
                but this is normally not recommended.
            sass_include_paths: Less include paths as a list. Paths are relative
                to the source folder of the :class:`~ievv_opensource.utils.ievvbuild.config.App`.
                You can specify folders in other apps using
                :class:`ievv_opensource.utils.ievvbuildstatic.filepath.SourcePath` objects
            **kwargs: Kwargs for :class:`ievv_opensource.utils.ievvbuildstatic.cssbuildbaseplugin.AbstractPlugin`.
        """
        self.sourcefolder = sourcefolder
        if isinstance(sourcefolder, filepath.FilePathInterface) and destinationfolder is None:
            raise ValueError('destinationfolder must be specifed when sourcefolder is not a string.')
        self.destinationfolder = destinationfolder or sourcefolder

        self.other_sourcefolders = other_sourcefolders or []
        self.sass_include_paths = sass_include_paths or []
        self.sourcefile = sourcefile
        self.sass_variables = sass_variables or {}
        super(Plugin, self).__init__(**kwargs)

    def install(self):
        super(Plugin, self).install()
        self.app.get_installer('npm').queue_install(
            'postcss-scss')

    def get_sourcefolder_path(self):
        return self.app.get_source_path(self.sourcefolder)

    def get_sourcefile_path(self):
        return self.app.get_source_path(self.sourcefolder, self.sourcefile)

    def get_destinationfile_path(self):
        return self.app.get_destination_path(
            self.destinationfolder, self.sourcefile, new_extension='.css')

    def get_other_sourcefolders_paths(self):
        return map(self.app.get_source_path, self.other_sourcefolders)

    def get_sass_include_paths(self, temporary_directory):
        sass_include_paths = list(map(self.app.get_source_path, self.sass_include_paths))
        sass_include_paths.append(self.get_importable_sass_directory(temporary_directory))
        return sass_include_paths

    def format_sass_include_paths(self, temporary_directory):
        if self.sass_include_paths:
            return ':'.join(self.get_sass_include_paths(temporary_directory))
        else:
            return ''

    def get_sassc_executable(self):
        return os.environ.get('IEVVTASKS_BUILDSTATIC_SASSC_EXECUTABLE', 'sassc')

    def get_sass_kwargs(self, temporary_directory):
        kwargs = {}
        sass_include_paths = self.format_sass_include_paths(temporary_directory=temporary_directory)
        if sass_include_paths:
            kwargs['load_path'] = sass_include_paths
        # style = 'nested'
        # if self.app.apps.is_in_production_mode():
        #     style = 'compressed'
        # kwargs['style'] = style
        return kwargs

    def get_importable_sass_directory(self, temporary_directory):
        importable_sass_directory_path = os.path.join(temporary_directory, 'automatically_on_sass_path')
        if not os.path.exists(importable_sass_directory_path):
            os.makedirs(importable_sass_directory_path)
        return importable_sass_directory_path

    def make_importable_sass_file(self, temporary_directory, sass_file_name, sass_code):
        directory_path = os.path.join(self.get_importable_sass_directory(temporary_directory),
                                      'autogenerated_partials')
        if not os.path.exists(directory_path):
            os.mkdir(directory_path)
        sass_file_path = os.path.join(directory_path, sass_file_name)
        with open(sass_file_path, 'wb') as f:
            f.write(sass_code.encode('utf-8'))

    def make_importable_variables_file_content(self):
        contentlist = []
        for variablename, value in self.sass_variables.items():
            contentlist.append('${}: {};'.format(variablename, value))
        header = '// Autogenerated by "ievv buildstatic". Do not edit this file.'
        return '{}\n\n{}'.format(header, '\n'.join(contentlist))

    def make_importable_variables_file(self, temporary_directory):
        self.make_importable_sass_file(temporary_directory=temporary_directory,
                                       sass_file_name='_variables.scss',
                                       sass_code=self.make_importable_variables_file_content())

    def preprocess_styles(self, temporary_directory):
        super(Plugin, self).preprocess_styles(temporary_directory)
        self.make_importable_variables_file(temporary_directory=temporary_directory)

    def build_css(self, temporary_directory):
        self.get_logger().command_start('Building {source} into {destination}.'.format(
            source=self.get_sourcefile_path(),
            destination=self.get_destinationfile_path()))

        destinationdirectory = os.path.dirname(self.get_destinationfile_path())
        if not os.path.exists(destinationdirectory):
            os.makedirs(destinationdirectory)

        executable = self.get_sassc_executable()
        try:
            self.run_shell_command(executable,
                                   args=[
                                       self.get_sourcefile_path(),
                                       self.get_destinationfile_path()
                                   ],
                                   kwargs=self.get_sass_kwargs(temporary_directory=temporary_directory))
        except ShellCommandError:
            self.get_logger().command_error('SASS build FAILED!')
            self.add_deferred_warning('SASS build FAILED!')
            raise cssbuildbaseplugin.CssBuildException()
        else:
            self.get_logger().command_success('SASS build successful :)')
            self.add_deferred_success('SASS build successful :)')

    def get_watch_folders(self):
        """
        We only watch the folder where the scss sources are located,
        so this returns the absolute path of the ``sourcefolder``.
        """
        folders = [self.app.get_source_path(self.sourcefolder)]
        if self.other_sourcefolders:
            folders.extend(self.get_other_sourcefolders_paths())
        return folders

    def get_watch_regexes(self):
        return ['^.+\.scss$']

    def __str__(self):
        return '{}({})'.format(super(Plugin, self).__str__(),
                               os.path.join(self.sourcefolder, self.sourcefile))

    def get_all_source_file_paths(self):
        regexfilelist = utils.RegexFileList(include_patterns=self.get_watch_regexes())
        source_file_paths = []
        sourcefolders = [self.get_sourcefolder_path()]
        sourcefolders.extend(self.get_other_sourcefolders_paths())
        for folder in sourcefolders:
            source_file_paths.extend(
                os.path.join(folder, relative_path)
                for relative_path in regexfilelist.get_files_as_list(folder))
        return source_file_paths
