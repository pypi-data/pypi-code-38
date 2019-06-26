import json

from .abstract_npm_installer import AbstractNpmInstaller
from ievv_opensource.utils.shellcommandmixin import ShellCommandError


class NpmInstallerError(Exception):
    pass


class PackageJsonDoesNotExist(NpmInstallerError):
    pass


class YarnInstaller(AbstractNpmInstaller):
    """
    Yarn installer.
    """
    name = 'yarninstall'
    optionprefix = 'yarn'

    def yarn_json_output_handler(self, outputdict):
        ignored_messagetypes = {
            'progressTick',
            'step',
        }
        ignored_messages = {
            'Saved 0 new dependencies.',
            'Saved lockfile.',
        }
        if isinstance(outputdict, dict):
            messagetype = outputdict.get('type')
            data = outputdict.get('data', {})
            if isinstance(data, dict):
                message = data.get('message')
            elif isinstance(data, str):
                message = data
            else:
                message = None
        else:
            message = str(outputdict)
            messagetype = 'unknown'
        if message and messagetype and message not in ignored_messages:
            if messagetype == 'error':
                super(YarnInstaller, self).log_shell_command_stderr(line=message)
            elif messagetype not in ignored_messagetypes:
                super(YarnInstaller, self).log_shell_command_stdout(line=message)

    def log_shell_command_stdout(self, line):
        try:
            outputdict = json.loads(line)
        except ValueError:
            super(YarnInstaller, self).log_shell_command_stdout(line=line)
        else:
            self.yarn_json_output_handler(outputdict=outputdict)

    def _run_yarn(self, args):
        self.run_shell_command('yarn',
                               args=args,
                               _cwd=self.app.get_source_path())

    def log_shell_command_stderr(self, line):
        try:
            outputdict = json.loads(line)
        except ValueError:
            super(YarnInstaller, self).log_shell_command_stdout(line=line)
        else:
            self.yarn_json_output_handler(outputdict=outputdict)

    def install_packages_from_packagejson(self):
        try:
            self._run_yarn(args=['--json'])
        except ShellCommandError:
            self.get_logger().command_error('yarn FAILED!')
            self.add_deferred_warning('Installing packages from package.json failed')
            raise SystemExit()

    def install_npm_package(self, package, properties):
        package_spec = package
        if properties['version']:
            package_spec = '{package}@{version}'.format(
                package=package, version=properties['version'])
        args = ['add', '--json', package_spec]
        if properties['installtype'] is not None:
            args.append('--{}'.format(properties['installtype']))
        try:
            self._run_yarn(args=args)
        except ShellCommandError:
            self.get_logger().command_error(
                'yarn add {package} (properties: {properties!r}) FAILED!'.format(
                    package=package, properties=properties))
            raise SystemExit()

    def uninstall_npm_package(self, package):
        try:
            self._run_yarn(args=['remove', package])
        except ShellCommandError:
            message = 'yarn remove {package} FAILED!'.format(
                    package=package)
            self.get_logger().command_error(message)

    def run_packagejson_script(self, script, args=None):
        args = args or []
        args = ['run', script] + args
        self._run_yarn(args=args)

    def link_package(self, packagename):
        self._run_yarn(args=['link', packagename])

    def unlink_package(self, packagename):
        self._run_yarn(args=['unlink', packagename])

    def install(self):
        self.get_logger().command_start(
            'Installing npm packages for {}'.format(self.app.get_source_path()))
        if self.get_option('clean_node_modules', False):
            self.remove_node_modules_directory()
        self.handle_linked_packages()
        if not self.packagejson_exists():
            self.create_packagejson()
        self.install_packages_from_packagejson()
        self.install_queued_packages()
        self.get_logger().command_success('Install npm packages succeeded :)')
        self.add_deferred_success('Install npm packages succeeded :)')
