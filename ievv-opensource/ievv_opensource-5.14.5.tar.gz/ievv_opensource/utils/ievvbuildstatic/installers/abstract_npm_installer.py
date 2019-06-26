import json
import os
from collections import OrderedDict

import shutil

from ievv_opensource.utils.ievvbuildstatic.installers.base import AbstractInstaller
from ievv_opensource.utils.shellcommandmixin import ShellCommandMixin


class NpmInstallerError(Exception):
    pass


class PackageJsonDoesNotExist(NpmInstallerError):
    pass


class AbstractNpmInstaller(AbstractInstaller, ShellCommandMixin):
    """
    Abstract npm installer.

    Base class for npm and yarn installers.
    """
    @classmethod
    def add_cli_arguments(cls, parser):
        parser.add_argument('--{}-clean-node-modules'.format(cls.optionprefix),
                            dest='clean_node_modules',
                            action='store_true', required=False, default=False,
                            help='Remove node_modules before installing node packages.')
        parser.add_argument('--{}-link'.format(cls.optionprefix),
                            dest='npmlink',
                            action='append',
                            metavar='PACKAGENAME',
                            required=False,
                            help='Link specified javascript package. Can be repeated multiple times.')

    def __init__(self, *args, **kwargs):
        super(AbstractNpmInstaller, self).__init__(*args, **kwargs)
        self.queued_packages = OrderedDict()

    def __validate_installtype(self, installtype):
        installtypes = (None, "dev", "optional")
        if installtype not in installtypes:
            raise ValueError(
                'Invalid installtype {installtype!r}. Must be '
                'one of {installtypes}'.format(
                    installtype=installtype,
                    installtypes=', '.join(installtypes)
                ))

    def queue_install(self, package, version=None, installtype=None):
        """
        Installs the given npm package in the build
        directory for the app.

        Does nothing if the package is already installed.

        Parameters:
            package: The package name.
            version: The package version.
            installtype: Determines where the package ends up in
                package.json. Can be one of:

                - ``None`` (the default): Ends up in dependencies.
                - ``"dev"``: Ends up in devDependencies.
                - ``"optional"`` (the default): Ends up in optionalDependencies.
        """
        self.__validate_installtype(installtype=installtype)
        self.get_logger().debug('Queued install of {} (version={}) for {}.'.format(
            package, version, self.app.appname))
        queue = True
        if package in self.queued_packages:
            queued_version = self.queued_packages[package]
            if version is None:
                queue = False
            elif queued_version is None:
                queue = True
            else:
                self.get_logger().warning(
                    'Multiple explicit versions of the same NPM package {package} '
                    'specified for {appname}: {version!r} and {queued_version!r}. '
                    'Using {version!r}.'.format(
                        package=package,
                        version=version,
                        queued_version=queued_version,
                        appname=self.app.appname))
                queue = True
        if queue:
            self.queued_packages[package] = {
                'version': version,
                'installtype': installtype
            }

    def get_packagejson_path(self):
        return self.app.get_source_path('package.json')

    def packagejson_exists(self):
        return os.path.exists(self.get_packagejson_path())

    # def packagejson_created_by_ievv_buildstatic(self):
    #     return 'ievv_buildstatic' in self.get_packagejson_dict()

    def __get_packagejson_dict(self):
        package_json_string = open(self.get_packagejson_path()).read()
        package_json_dict = json.loads(package_json_string)
        return package_json_dict

    def get_packagejson_dict(self):
        """
        Get ``package.json`` as a dict.

        This is cached, so calling it many times only requires
        one read from the disk.
        """
        if not hasattr(self, '_packagejson_dict'):
            self._packagejson_dict = self.__get_packagejson_dict()
        return self._packagejson_dict

    def save_packagejson_dict(self):
        """
        Save the dict returned by :meth:`.get_packagejson_dict`
        to ``package.json``.

        You must call this if you change the dict returned
        by :meth:`.get_packagejson_dict`.
        """
        open(self.get_packagejson_path(), 'wb').write(
            json.dumps(
                self._packagejson_dict,
                indent=2,
                sort_keys=True
            ).encode('utf-8'))

    def create_packagejson(self):
        """
        Create initial ``package.json``.
        """
        package_json_dict = {
            'name': self.app.appname,
            'private': True,
            'ievv_buildstatic': {},
            # We do not care about the version. We are not building a distributable package.
            'version': '0.0.1',
        }
        self._packagejson_dict = package_json_dict
        self.save_packagejson_dict()

    def add_npm_script(self, scriptname, script):
        """
        Add a script to the ``"scripts"`` property of ``package.json``.

        Overwrites any existing script named ``scriptname``.

        Args:
            scriptname: The key in the ``"scripts"`` object/dict.
            script: The value in in the ``"scripts"`` object/dict.
        """
        package_json_dict = self.get_packagejson_dict()
        scripts = self.get_packagejson_dict().get('scripts', {})
        scripts[scriptname] = script
        package_json_dict['scripts'] = scripts
        self.save_packagejson_dict()

    def has_npm_script(self, scriptname):
        return scriptname in self.get_packagejson_dict().get('scripts', {})

    def get_packagejson_key_from_installtype(self, installtype):
        if installtype is None:
            return 'dependencies'
        elif installtype == 'dev':
            return 'devDependencies'
        elif installtype == 'optional':
            return 'optionalDependencies'

    def package_is_in_packages_json(self, package, properties):
        package_json_dict = self.get_packagejson_dict()
        key = self.get_packagejson_key_from_installtype(installtype=properties['installtype'])
        packages = package_json_dict.get(key, {})
        return package in packages

    def get_node_modules_directory(self):
        return self.app.get_source_path('node_modules')

    def find_executable(self, executablename):
        """
        Find an executable named ``executablename``.

        Returns the absolute path to the executable.
        """
        executablepath = self.app.get_source_path(
            'node_modules', '.bin', executablename)
        return executablepath

    def get_package_json_dict_for_package(self, package_name):
        package_json_path = self.app.get_source_path(
            'node_modules', package_name, 'package.json')
        package_json_string = open(package_json_path).read()
        package_json_dict = json.loads(package_json_string)
        return package_json_dict

    def get_package_version(self, package_name):
        return self.get_package_json_dict_for_package(package_name)['version']

    def get_installed_package_names(self):
        if not os.path.exists(self.get_packagejson_path()):
            raise PackageJsonDoesNotExist()
        package_json_string = open(self.get_packagejson_path()).read()
        package_json_dict = json.loads(package_json_string)
        package_names = []
        for package_name, version in package_json_dict.get('devDependencies', {}).items():
            package_names.append(package_name)
        return package_names

    def install_queued_packages(self):
        for package, properties in self.queued_packages.items():
            if not self.package_is_in_packages_json(package=package,
                                                    properties=properties):
                self.install_npm_package(package=package, properties=properties)

    def install(self):
        raise NotImplementedError()

    def install_packages_from_packagejson(self):
        raise NotImplementedError()

    def install_npm_package(self, package, properties):
        raise NotImplementedError()

    def uninstall_npm_package(self, packagename):
        raise NotImplementedError()

    def run_packagejson_script(self, script, args=None):
        """
        Run a script in the scripts section of the package.json.

        Args:
            script: The npm script to run.
            args (list): List of arguments.
        """
        raise NotImplementedError()

    def initialize(self):
        if os.path.exists(self.get_packagejson_path()):
            self.install()

    def remove_node_modules_directory(self):
        """
        Remove node_modules directory.
        """
        if os.path.exists(self.get_node_modules_directory()):
            shutil.rmtree(self.get_node_modules_directory())

    def get_linked_packages(self):
        """
        Get all the linked packages in the node_modules directory.
        (packages added with npm link).

        """
        node_modules_directory = self.get_node_modules_directory()
        linked_packages = set()
        if os.path.exists(node_modules_directory):
            for filename in os.listdir(node_modules_directory):
                path = os.path.join(node_modules_directory, filename)
                if os.path.islink(path):
                    linked_packages.add(filename)
        return linked_packages

    def _remove_linked_packages(self, linked_packages):
        for packagename in linked_packages:
            self._unlink_package(packagename=packagename)
            path = os.path.join(self.get_node_modules_directory(), packagename)
            if os.path.exists(path):
                os.remove(path)

    def _link_package(self, packagename):
        self.get_logger().info('Linking package {!r}'.format(packagename))
        self.link_package(packagename=packagename)
        self.add_deferred_success(
            'linked package {}'.format(packagename)
        )

    def link_package(self, packagename):
        raise NotImplementedError()

    def _unlink_package(self, packagename):
        self.get_logger().info('Unlinking package {!r}'.format(packagename))
        self.unlink_package(packagename=packagename)
        self.add_deferred_warning(
            'unlinked package {}'.format(packagename)
        )

    def unlink_package(self, packagename):
        raise NotImplementedError()

    def get_requested_link_packages_from_options(self):
        return self.get_option('npmlink', []) or []

    def handle_linked_packages(self):
        linked_packages = self.get_linked_packages()
        if self.is_in_production_mode() and linked_packages:
            self.get_logger().warning(
                'There are linked packages ({linked_packages!r}) in {node_modules_directory!r}. '
                'Since we are running in production mode, we remove the node_modules directory '
                'to make sure we get a prestine build.'.format(
                    linked_packages=linked_packages,
                    node_modules_directory=self.get_node_modules_directory()
                ))
            self.remove_node_modules_directory()
        else:
            requested_link_packages = set(self.get_requested_link_packages_from_options())
            packages_to_unlink = linked_packages.difference(requested_link_packages)
            packages_to_link = requested_link_packages.difference(linked_packages)
            if packages_to_unlink:
                self.get_logger().warning(
                    'There are linked packages ({linked_packages!r}) in {node_modules_directory!r} '
                    'that has not been specified using command line options. '
                    'Unlinking these packages.'.format(
                        linked_packages=packages_to_unlink,
                        node_modules_directory=self.get_node_modules_directory()
                    ))
                self._remove_linked_packages(
                    linked_packages=packages_to_unlink)
            for packagename in packages_to_link:
                self._link_package(packagename=packagename)
            if linked_packages:
                self.add_deferred_warning('Installing with linked packages: {!r}'.format(linked_packages))
