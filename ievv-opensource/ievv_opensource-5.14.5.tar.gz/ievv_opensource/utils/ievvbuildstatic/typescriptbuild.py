from __future__ import unicode_literals

import json
import os

import sh
from ievv_opensource.utils.ievvbuildstatic import pluginbase
from ievv_opensource.utils.ievvbuildstatic import utils
from ievv_opensource.utils.shellcommandmixin import ShellCommandMixin, ShellCommandError


class Plugin(pluginbase.Plugin, ShellCommandMixin):
    name = 'typescriptbuild'
    default_group = 'js'

    def __init__(self,
                 main_sourcefile="main.ts",
                 destinationfile=None,
                 sourcefile_include_patterns=None,
                 sourcefile_exclude_patterns=None,
                 sourcefolder=os.path.join('scripts', 'typescript'),
                 destinationfolder=os.path.join('scripts'),
                 extra_watchfolders=None,
                 with_function_wrapper=True,
                 lint=True,
                 lintconfig=None,
                 tsc_compiler_options=None,
                 tsc_exclude=None,
                 typings_global_dependencies=None,
                 register_tsconfig_as_temporaryfile=True,
                 **kwargs):
        super(Plugin, self).__init__(**kwargs)
        self.destinationfile = destinationfile
        self.main_sourcefile = main_sourcefile
        self.register_tsconfig_as_temporaryfile = register_tsconfig_as_temporaryfile
        self.sourcefiles = utils.RegexFileList(
            include_patterns=sourcefile_include_patterns or ['^.*\.ts'],
            exclude_patterns=sourcefile_exclude_patterns
        )
        self.destinationfolder = destinationfolder
        self.sourcefolder = sourcefolder
        self.extra_watchfolders = extra_watchfolders or []
        self.with_function_wrapper = with_function_wrapper
        self.lint = lint
        self.lintconfig = lintconfig or {}
        self.tsc_compiler_options = {
            "target": "es5",
            "module": "commonjs",
            "moduleResolution": "node",
            "sourceMap": True,
            "emitDecoratorMetadata": True,
            "experimentalDecorators": True,
            "removeComments": False,
            "noImplicitAny": True,
            "suppressImplicitAnyIndexErrors": True
        }
        if tsc_compiler_options:
            self.tsc_compiler_options.update(tsc_compiler_options)
        if tsc_exclude is None:
            self.tsc_exclude = ['node_modules']
        else:
            self.tsc_exclude = tsc_exclude
        self.typings_global_dependencies = typings_global_dependencies

    def get_sourcefolder_path(self):
        return self.app.get_source_path(self.sourcefolder)

    def get_main_sourcefile_path(self):
        return self.app.get_source_path(self.sourcefolder, self.main_sourcefile)

    def get_destinationfile_path(self):
        if self.destinationfile:
            return self.app.get_destination_path(self.destinationfolder, self.destinationfile)
        else:
            return self.app.get_destination_path(self.destinationfolder, self.main_sourcefile, new_extension='.js')

    def get_typescript_version(self):
        return None

    def get_typings_version(self):
        return None

    def get_tslint_version(self):
        return None

    def get_browserify_version(self):
        return None

    def install(self):
        self.app.get_installer('npm').queue_install(
            'typescript', version=self.get_typescript_version())
        self.app.get_installer('npm').queue_install(
            'typings', version=self.get_typings_version())
        if self.lint:
            self.app.get_installer('npm').queue_install(
                'tslint', version=self.get_tslint_version())
        self.app.get_installer('npm').queue_install(
            'browserify', version=self.get_browserify_version())

    def post_install(self):
        self.setup_typings()

    def get_tsc_executable(self):
        return self.app.get_installer('npm').find_executable('tsc')

    def get_tslint_executable(self):
        return self.app.get_installer('npm').find_executable('tslint')

    def get_typings_executable(self):
        return self.app.get_installer('npm').find_executable('typings')

    def get_all_sourcefiles(self, absolute_paths=False):
        return self.sourcefiles.get_files_as_list(rootfolder=self.get_sourcefolder_path(),
                                                  absolute_paths=absolute_paths)

    def lint_typescript_file(self, relative_filepath, lintconfig_path):
        executable = self.get_tslint_executable()
        sourcefile_path = os.path.join(self.get_sourcefolder_path(), relative_filepath)
        self.get_logger().debug('Typescript linting {!r}'.format(
            relative_filepath))
        try:
            self.run_shell_command(executable,
                                   args=[
                                       '-f', lintconfig_path,
                                       sourcefile_path
                                   ])
        except ShellCommandError:
            self.get_logger().error('Typescript linting of {!r} FAILED!'.format(
                relative_filepath))

    def make_lintconfig_file(self, temporary_directory):
        lintconfig_path = os.path.join(temporary_directory, 'coffeelint.json')
        try:
            coffeelint = sh.Command(self.get_tslint_executable())
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

    def lint_typescript_files(self, temporary_directory):
        # lintconfig_path = self.make_lintconfig_file(temporary_directory=temporary_directory)
        # for relative_filepath in self.get_all_sourcefiles():
        #     self.lint_typescript_file(relative_filepath=relative_filepath,
        #                               lintconfig_path=lintconfig_path)
        pass

    def make_tsconfig_dict(self, output_directory):
        tsc_compiler_options = self.tsc_compiler_options.copy()
        tsc_compiler_options['outDir'] = output_directory
        output = {
            "compilerOptions": tsc_compiler_options,
            "include": self.get_all_sourcefiles(absolute_paths=True),
            "exclude": self.tsc_exclude
        }
        return output

    def make_tsconfig(self, output_directory):
        tsconfig_dict = self.make_tsconfig_dict(output_directory)
        path = self.app.get_source_path("tsconfig.json")
        open(path, 'wb').write(json.dumps(tsconfig_dict, indent=2).encode('utf-8'))
        if self.register_tsconfig_as_temporaryfile:
            self.register_temporary_file_or_directory(path)

    def run_typings_install(self):
        self.get_logger().debug("Running typings install")
        executable = self.get_typings_executable()
        for typings_install_key in self.typings_global_dependencies:
            try:
                self.run_shell_command(executable,
                                       args=['install', typings_install_key, '--save', '--global'],
                                       _cwd=self.app.get_source_path())
            except ShellCommandError:
                self.get_logger().error('typings install failed: {}'.format(typings_install_key))
                raise

    def setup_typings(self):
        if self.typings_global_dependencies is None:
            return
        self.run_typings_install()

    def compile_typescript(self):
        executable = self.get_tsc_executable()
        sourcefolder_path = self.get_sourcefolder_path()

        try:
            self.run_shell_command(executable, _cwd=self.app.get_source_path())
        except ShellCommandError:
            self.get_logger().error('TypeScript build of {!r} FAILED!'.format(sourcefolder_path))
            raise
        else:
            self.get_logger().debug('TypeScript build of {!r} successful :)'.format(sourcefolder_path))

    def get_browserify_executable(self):
        return self.app.get_installer('npm').find_executable('browserify')

    def merge_javascript_files(self, js_directory):
        self.get_logger().command_start(
            'Running browserify with {sourcefile} as input and {destinationfile} as output'.format(
                sourcefile=self.get_main_sourcefile_path(),
                destinationfile=self.get_destinationfile_path()))

        sourcefilepath = os.path.join(js_directory, self.main_sourcefile)
        sourcefilepath = os.path.splitext(sourcefilepath)[0] + '.js'

        destinationfolder = os.path.dirname(self.get_destinationfile_path())
        if not os.path.exists(destinationfolder):
            os.makedirs(destinationfolder)
        executable = self.get_browserify_executable()
        try:
            self.run_shell_command(executable,
                                   args=[
                                       sourcefilepath,
                                       '-o', self.get_destinationfile_path()
                                   ],
                                   _cwd=self.app.get_source_path())
        except ShellCommandError:
            self.get_logger().command_error('browserify build FAILED!')
            raise
        else:
            self.get_logger().command_success('browserify build succeeded :)')

    def build(self, temporary_directory):
        if self.lint:
            self.lint_typescript_files(temporary_directory=temporary_directory)
        js_directory = os.path.join(temporary_directory, 'js')
        os.mkdir(js_directory)
        self.make_tsconfig(js_directory)

        try:
            self.compile_typescript()
        except ShellCommandError:
            self.get_logger().command_error('Typescript build FAILED!')
        else:
            # javascript_source = self.merge_javascript_files(js_directory=js_directory)
            # destination_directory = os.path.dirname(self.get_destinationfile_path())
            # if not os.path.exists(destination_directory):
            #     os.makedirs(destination_directory)
            # open(self.get_destinationfile_path(), 'wb').write(
            #     javascript_source.encode('utf-8'))
            try:
                self.merge_javascript_files(js_directory)
            except ShellCommandError:
                pass
            else:
                self.get_logger().command_success(
                    'TypeScript build successful :) Output in {}'.format(
                        self.get_destinationfile_path()))

    def run(self):
        self.get_logger().command_start('TypeScript building all files in {!r} matching {}'.format(
            self.get_sourcefolder_path(),
            self.sourcefiles.prettyformat_patterns()))
        temporary_directory = self.make_temporary_build_directory()
        self.build(temporary_directory=temporary_directory)


    def get_extra_watchfolder_paths(self):
        return map(self.app.get_source_path, self.extra_watchfolders)

    def get_watch_folders(self):
        """
        We only watch the folder where the typescript sources are located,
        so this returns the absolute path of the ``sourcefolder``.
        """
        folders = [self.app.get_source_path(self.sourcefolder)]
        if self.extra_watchfolders:
            folders.extend(self.get_extra_watchfolder_paths())
        return folders

    def get_watch_regexes(self):
        return ['^.+[.]ts']

    def __str__(self):
        return '{}({})'.format(super(Plugin, self).__str__(), self.sourcefolder)
