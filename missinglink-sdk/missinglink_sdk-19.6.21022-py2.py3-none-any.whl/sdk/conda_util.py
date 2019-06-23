import logging
import os
import requests
from .pkg_provider import PackageProvider

conda_timeout_seconds = 3.0

logger = logging.getLogger('missinglink')


class CondaPackageProvider(PackageProvider):
    def __init__(self, reference_package_name=None):
        super(CondaPackageProvider, self).__init__(reference_package_name)
        self._channel = self._get_conda_channel()

    def _latest_version(self, package):
        url = 'https://api.anaconda.org/package/{channel}/{package}'.format(channel=self._channel, package=package)
        r = requests.get(url, timeout=conda_timeout_seconds)
        r.raise_for_status()

        package_info = r.json()
        versions = package_info['versions']

        return max(versions, key=lambda v: tuple(int(t) for t in v.split('.')))

    @staticmethod
    def _get_conda_channel_by_staging(staging):
        return 'missinglink.ai' if not staging else 'missinglink-test'

    def _get_conda_channel(self):
        return self._get_conda_channel_by_staging(self.is_staging)

    def _get_install_args(self, require_package, pipe_streams=True):
        env_name = os.environ.get('CONDA_DEFAULT_ENV')
        conda_exe = os.environ.get('CONDA_EXE', 'conda')
        args = [conda_exe, 'install', '-n', env_name, '-c', self._channel, '--update-deps', '-y', require_package]

        return args


# Old method that ml is using

def is_conda_env():
    return CondaPackageProvider.is_conda_env()


def get_conda_channel(staging):
    return CondaPackageProvider._get_conda_channel_by_staging(staging)


def get_latest_conda_version(package, staging, throw_exception=False):
    return CondaPackageProvider(package).latest_version(package, throw_exception=throw_exception)
