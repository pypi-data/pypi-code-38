from collections import OrderedDict

from ievv_opensource.utils.shellcommandmixin import ShellCommandError
from .abstract_npm_installer import AbstractNpmInstaller


class NpmInstallerError(Exception):
    pass


class PackageJsonDoesNotExist(NpmInstallerError):
    pass


class NpmInstaller(AbstractNpmInstaller):
    """
    NPM installer.
    """
    name = 'npminstall'
    optionprefix = 'npm'

    def _run_npm(self, args):
        self.run_shell_command('npm',
                               args=args,
                               _cwd=self.app.get_source_path())

    def __init__(self, *args, **kwargs):
        super(NpmInstaller, self).__init__(*args, **kwargs)
        self.queued_packages = OrderedDict()

    def log_shell_command_stderr(self, line):
        if 'npm WARN package.json' in line:
            return
        super(NpmInstaller, self).log_shell_command_stderr(line)

    def install_packages_from_packagejson(self):
        try:
            self.run_shell_command('npm',
                                   args=['install'],
                                   _cwd=self.app.get_source_path())
        except ShellCommandError:
            self.get_logger().command_error('npm install FAILED!')
            raise SystemExit()

    def install_npm_package(self, package, properties):
        package_spec = package
        if properties['version']:
            package_spec = '{package}@{version}'.format(
                package=package, version=properties['version'])
        args = ['install', package_spec]
        if properties['installtype'] is None:
            args.append('--save')
        else:
            args.append('--save-{}'.format(properties['installtype']))
        try:
            self.run_shell_command('npm',
                                   args=args,
                                   _cwd=self.app.get_source_path())
        except ShellCommandError:
            self.get_logger().command_error(
                'npm install {package} (properties: {properties!r}) FAILED!'.format(
                    package=package, properties=properties))
            raise SystemExit()

    def run_packagejson_script(self, script, args=None):
        args = args or []
        self.run_shell_command('npm',
                               args=['run', script] + args,
                               _cwd=self.app.get_source_path())

    def link_package(self, packagename):
        self._run_npm(args=['link', packagename])

    def unlink_package(self, packagename):
        self._run_npm(args=['unlink', packagename])

    def install(self):
        self.get_logger().command_start(
            'Installing npm packages for {}'.format(self.app.get_source_path()))
        if self.get_option('clean_node_modules', False):
            self.remove_node_modules_directory()
        if not self.packagejson_exists():
            self.create_packagejson()
        self.install_packages_from_packagejson()
        self.install_queued_packages()
        self.handle_linked_packages()
        self.get_logger().command_success('Install npm packages succeeded :)')
        self.add_deferred_success('Install npm packages succeeded :)')
