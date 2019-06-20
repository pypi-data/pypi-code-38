# -*- coding: utf-8 -*-
import os
import site
import sys
import requests
from .pkg_provider import PackageProvider, FailedInstalled
from .print_or_log import print_update_info


class PipPackageProvider(PackageProvider):
    TEST_PYPI_HOST = 'test.pypi.org'
    PROD_PYPI_HOST = 'pypi.org'

    def __init__(self, reference_package_name=None):
        super(PipPackageProvider, self).__init__(reference_package_name)
        host = self.TEST_PYPI_HOST if self.is_staging else self.PROD_PYPI_HOST
        self._pip_server = 'https://{host}/pypi'.format(host=host)

    @classmethod
    def _get_pypi(cls, host):
        return 'https://{host}/simple/'.format(host=host)

    @classmethod
    def _has_write_permissions_to_system_packages(cls):
        site_pkgs = [x for x in cls._getsitepackages() if not x.endswith("site-python")]
        has_access = all([os.access(x, os.W_OK) for x in site_pkgs])
        # this will return true for virtualenv when there are getsitepackages

        if not has_access:
            print_update_info("This user doesn't have access to the system packages")

        return has_access

    def _is_installed_in_user_path(self, package=None):
        package = package or self._reference_package_name
        package_location = self._get_package_location(package)

        return package_location in self._getusersitepackages()

    @classmethod
    def _import_pip(cls):
        import pip
        return pip

    @classmethod
    def _check_pip(cls):
        from .print_or_log import print_update_warning

        try:
            cls._import_pip()
        except ImportError:
            print_update_warning('pip package not found')
            raise FailedInstalled('Missing pip package in python environment')

    def _user_install(self, package=None):
        return (self._is_installed_in_user_path(package=package) and site.ENABLE_USER_SITE) or not self._has_write_permissions_to_system_packages()

    @staticmethod
    def _getpackages(method_name):
        getusersitepackages = getattr(site, method_name, lambda: [])

        values = getusersitepackages() or []

        if not isinstance(values, (list, tuple)):
            values = [values]

        return values

    @classmethod
    def _getusersitepackages(cls):
        return cls._getpackages('getusersitepackages')

    @classmethod
    def _getsitepackages(cls):
        return cls._getpackages('getsitepackages')

    @classmethod
    def _validate_user_path(cls, index_of_path=None, path_insert=None):
        from .print_or_log import print_update_warning

        user_site_packages = cls._getusersitepackages()
        if len(user_site_packages) == 0:
            print_update_warning('getusersitepackages has no user paths')
            return None

        user_site_packages = user_site_packages[0]

        index_of_path = index_of_path or sys.path.index

        try:
            index_of_path(user_site_packages)
        except ValueError:
            path_insert = path_insert or sys.path.insert
            path_insert(0, user_site_packages)
            return True

        return False

    def _get_install_args(self, require_package):
        self._check_pip()

        args = [sys.executable, '-m', 'pip', 'install', '--upgrade']

        if self._user_install():
            self._validate_user_path()

            print_update_info("`%s` will be installed in user mode", require_package)

            args.append('--user')

        if self.is_staging:
            args.extend(['--index-url', self._get_pypi(self.TEST_PYPI_HOST)])
            args.extend(['--extra-index-url', self._get_pypi(self.PROD_PYPI_HOST)])

        args.append(require_package)

        return args

    def _latest_version(self, package):
        url = '{server}/{package}/json'.format(server=self._pip_server, package=package)
        r = requests.get(url)
        r.raise_for_status()

        package_info = r.json()

        return package_info['info']['version']
