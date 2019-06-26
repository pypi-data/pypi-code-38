from __future__ import unicode_literals

import json
import os

import sh
from ievv_opensource.utils.ievvbuildstatic import pluginbase
from ievv_opensource.utils.ievvbuildstatic import utils
from ievv_opensource.utils.shellcommandmixin import ShellCommandMixin, ShellCommandError


class JavascriptMerger(object):
    def __init__(self):
        self.javascript_filepaths = []

    def add(self, javascript_filepath):
        self.javascript_filepaths.append(javascript_filepath)

    def __wrap_with_function_wrapper(self, source):
        sourcelines = []
        for line in source.splitlines():
            if line:
                line = '  {}'.format(line)
            sourcelines.append(line)

        sourcelines.insert(0, '(function() {')
        sourcelines.append('}).call(this);')
        return '\n'.join(sourcelines)

    def merge(self, rootdirectory, with_function_wrapper=True):
        output = []
        for javascript_filepath in self.javascript_filepaths:
            filecontent = open(javascript_filepath, 'rb').read().decode('utf-8')
            filecontent = filecontent.replace('\r\n', '\n').replace('\r', '\n')
            output.append('/* {} */'.format(
                            os.path.relpath(javascript_filepath, rootdirectory)))
            output.append(filecontent)
        source = '\n\n'.join(output)
        if with_function_wrapper:
            source = self.__wrap_with_function_wrapper(source=source)
        return source


class Plugin(pluginbase.Plugin, ShellCommandMixin):
    """
    CoffeeScript build plugin --- builds .coffee files into css, and supports watching
    for changes.

    Examples:

        Very simple example where the source file is in
        ``demoapp/staticsources/scripts/coffeescript/app.coffee``::

            IEVVTASKS_BUILDSTATIC_APPS = ievvbuildstatic.config.Apps(
                ievvbuildstatic.config.App(
                    appname='demoapp',
                    version='1.0.0',
                    plugins=[
                        ievvbuildstatic.coffeebuild.Plugin(destinationfile='app.js'),
                    ]
                )
            )

        Lets say we want build a different folder, and exclude all
        ``*.spec.coffee`` files in within the folder::

            IEVVTASKS_BUILDSTATIC_APPS = ievvbuildstatic.config.Apps(
                ievvbuildstatic.config.App(
                    appname='demoapp',
                    version='1.0.0',
                    plugins=[
                        ievvbuildstatic.coffeebuild.Plugin(
                            destinationfile='myapp.js',
                            sourcefolder=os.path.join('scripts', 'coffeescript', 'myapp')
                            sourcefile_exclude_patterns=['^.*\.spec\.coffee$']),
                    ]
                )
            )

        We also support linting, and it is enabled by default. You can disable
        linting with ``lint=False``, and you can override the coffeelint options.
        Lets say we want to change max line length to 120, and make breaking
        it a warning instead of an error::

            ievvbuildstatic.config.App(
                appname='demoapp',
                version='1.0.0',
                plugins=[
                    ievvbuildstatic.coffeebuild.Plugin(
                        destinationfile='app.js',
                        lintconfig={
                            "max_line_length": {
                                'value': 120,
                                'level': "warn",
                                'limitComments': True,
                            }
                        }
                    ),
                ]
            ),

    """

    name = 'coffeebuild'
    default_group = 'js'

    def __init__(self,
                 destinationfile,
                 sourcefile_include_patterns=None,
                 sourcefile_exclude_patterns=None,
                 sourcefolder=os.path.join('scripts', 'coffeescript'),
                 destinationfolder='scripts',
                 extra_watchfolders=None,
                 with_function_wrapper=True,
                 lint=True,
                 lintconfig=None,
                 **kwargs):
        """
        Parameters:
            destinationfile: Path to destination file relative to ``destinationfolder``.
            sourcefile_include_patterns: List of source file regexes. Same format as
                as for :class:`ievv_opensource.utils.ievvbuildstatic.utils.RegexFileList`.
                Defaults to ``['^.*\.coffee$']``.
            sourcefile_exclude_patterns: List of source file regexes. Same format as
                as for :class:`ievv_opensource.utils.ievvbuildstatic.utils.RegexFileList`.
            sourcefolder: The folder where sourcefiles is located relative to
                the source folder of the :class:`~ievv_opensource.utils.ievvbuild.config.App`.
                Defaults to ``scripts/coffeescript/``.
            destinationfolder: The folder where ``destinationfile`` is located relative to
                the destination folder of the :class:`~ievv_opensource.utils.ievvbuild.config.App`.
                Defaults to ``scripts/``.
            extra_watchfolders: List of extra folders to watch for changes.
                Relative to the source folder of the
                :class:`~ievv_opensource.utils.ievvbuild.config.App`.
            with_function_wrapper: Include function wrapper around the resulting
                javascript file.
            **kwargs: Kwargs for :class:`ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin`.
        """
        super(Plugin, self).__init__(**kwargs)
        self.destinationfile = destinationfile
        self.sourcefiles = utils.RegexFileList(
            include_patterns=sourcefile_include_patterns or ['^.*\.coffee$'],
            exclude_patterns=sourcefile_exclude_patterns
        )
        self.destinationfolder = destinationfolder
        self.sourcefolder = sourcefolder
        self.extra_watchfolders = extra_watchfolders or []
        self.with_function_wrapper = with_function_wrapper
        self.lint = lint
        self.lintconfig = lintconfig or {}

    def get_sourcefolder_path(self):
        return self.app.get_source_path(self.sourcefolder)

    def get_destinationfile_path(self):
        return self.app.get_destination_path(self.destinationfolder, self.destinationfile)

    def get_coffee_version(self):
        return None

    def get_coffeelint_version(self):
        return None

    def install(self):
        self.app.get_installer('npm').queue_install(
            'coffee-script', version=self.get_coffee_version())
        if self.lint:
            self.app.get_installer('npm').queue_install(
                'coffeelint', version=self.get_coffeelint_version())

    def get_coffee_executable(self):
        return self.app.get_installer('npm').find_executable('coffee')

    def get_coffeelint_executable(self):
        return self.app.get_installer('npm').find_executable('coffeelint')

    def get_all_sourcefiles(self):
        return self.sourcefiles.get_files_as_list(rootfolder=self.get_sourcefolder_path())

    def lint_coffeescript_file(self, relative_filepath, lintconfig_path):
        executable = self.get_coffeelint_executable()
        sourcefile_path = os.path.join(self.get_sourcefolder_path(), relative_filepath)
        self.get_logger().debug('CoffeeScript linting {!r}'.format(
            relative_filepath))
        try:
            self.run_shell_command(executable,
                                   args=[
                                       '-f', lintconfig_path,
                                       sourcefile_path
                                   ])
        except ShellCommandError:
            self.get_logger().error('CoffeeScript linting of {!r} FAILED!'.format(
                relative_filepath))

    def make_lintconfig_file(self, temporary_directory):
        lintconfig_path = os.path.join(temporary_directory, 'coffeelint.json')
        try:
            coffeelint = sh.Command(self.get_coffeelint_executable())
            default_lintconfig_json = coffeelint('--makeconfig',
                                                 _err=self.log_shell_command_stderr)
        except sh.ErrorReturnCode:
            self.get_logger().error('Failed to create coffeelint config file.')
            raise ShellCommandError()
        else:
            lintconfig = json.loads(str(default_lintconfig_json))
            lintconfig.update(self.lintconfig)
            open(lintconfig_path, 'wb').write(json.dumps(lintconfig, indent=2).encode('utf-8'))
            return lintconfig_path

    def lint_coffeescript_files(self, temporary_directory):
        lintconfig_path = self.make_lintconfig_file(temporary_directory=temporary_directory)
        for relative_filepath in self.get_all_sourcefiles():
            self.lint_coffeescript_file(relative_filepath=relative_filepath,
                                        lintconfig_path=lintconfig_path)

    def compile_coffescript_file(self, js_directory, relative_filepath):
        executable = self.get_coffee_executable()
        sourcefile_path = os.path.join(self.get_sourcefolder_path(), relative_filepath)
        destinationfile_directory = os.path.dirname(
            os.path.join(js_directory, relative_filepath))
        try:
            self.run_shell_command(executable,
                                   args=[
                                       '-b',
                                       '-o', destinationfile_directory,
                                       '-c', sourcefile_path,
                                   ])
        except ShellCommandError:
            self.get_logger().error('CoffeeScript build of {!r} FAILED!'.format(
                relative_filepath))
            raise
        else:
            self.get_logger().debug('CoffeeScript build of {!r} successful :)'.format(
                relative_filepath))

    def build_coffeescript_files(self, js_directory):
        for relative_filepath in self.get_all_sourcefiles():
            self.compile_coffescript_file(
                js_directory=js_directory,
                relative_filepath=relative_filepath)

    def merge_javascript_files(self, js_directory):
        javascript_merger = JavascriptMerger()
        for root, dirs, files in os.walk(js_directory):
            for filename in files:
                filepath = os.path.abspath(os.path.join(root, filename))
                javascript_merger.add(filepath)
        return javascript_merger.merge(rootdirectory=js_directory,
                                       with_function_wrapper=self.with_function_wrapper)

    def build(self, temporary_directory):
        if self.lint:
            self.lint_coffeescript_files(temporary_directory=temporary_directory)
        js_directory = os.path.join(temporary_directory, 'js')
        os.mkdir(js_directory)
        try:
            self.build_coffeescript_files(js_directory=js_directory)
        except ShellCommandError:
            self.get_logger().command_error('CoffeeScript build FAILED!')
        else:
            javascript_source = self.merge_javascript_files(js_directory=js_directory)
            destination_directory = os.path.dirname(self.get_destinationfile_path())
            if not os.path.exists(destination_directory):
                os.makedirs(destination_directory)
            open(self.get_destinationfile_path(), 'wb').write(
                javascript_source.encode('utf-8'))
            self.get_logger().command_success(
                'CoffeeScript build successful :) Output in {}'.format(
                    self.get_destinationfile_path()))

    def run(self):
        self.get_logger().command_start('CoffeeScript building all files in {!r} matching {}'.format(
            self.get_sourcefolder_path(),
            self.sourcefiles.prettyformat_patterns()))
        temporary_directory = self.make_temporary_build_directory()
        self.build(temporary_directory=temporary_directory)

    def get_extra_watchfolder_paths(self):
        return map(self.app.get_source_path, self.extra_watchfolders)

    def get_watch_folders(self):
        """
        We only watch the folder where the coffee sources are located,
        so this returns the absolute path of the ``sourcefolder``.
        """
        folders = [self.app.get_source_path(self.sourcefolder)]
        if self.extra_watchfolders:
            folders.extend(self.get_extra_watchfolder_paths())
        return folders

    def get_watch_regexes(self):
        return ['^.+[.]coffee$']

    def __str__(self):
        return '{}({})'.format(super(Plugin, self).__str__(), self.sourcefolder)
