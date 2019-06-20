import os
import subprocess
import sys
import pkg_resources
from .print_or_log import print_update_info, print_update_error, print_update_debug, print_update_forced
import abc
import six


class FailedInstalled(Exception):
    pass


@six.add_metaclass(abc.ABCMeta)
class PackageProvider:
    # used for determination if this is stage or prod
    DEFAULT_PACKAGE_NAME = 'missinglink-sdk'

    def __init__(self, reference_package_name=None):
        self._reference_package_name = reference_package_name or self.DEFAULT_PACKAGE_NAME
        self._keywords = self._get_keywords(self._reference_package_name)

    @classmethod
    def _package_provider_name(cls):
        return cls.__name__.replace('PackageProvider', '').lower()

    def latest_version(self, package, throw_exception=False):
        try:
            version = self._latest_version(package)
            msg = '`%s`: latest %s version %s' if not self.is_staging else '`%s`: latest conda STAGING version %s'
            print_update_info(msg, package, self._package_provider_name(), version)

            return version
        except Exception as e:
            if throw_exception:
                raise

            print_update_error('could not check for new %s version:\n%s', package, e)
            return None

    @classmethod
    def is_conda_env(cls):
        return os.environ.get('CONDA_DEFAULT_ENV') is not None

    @classmethod
    def get_provider(cls, **kwargs):
        if cls.is_conda_env():
            from .conda_util import CondaPackageProvider
            return CondaPackageProvider(**kwargs)

        from .pip_util import PipPackageProvider
        return PipPackageProvider(**kwargs)

    @property
    def is_staging(self):
        return 'test' in self._keywords

    @classmethod
    def _run_command(cls, args, pipe_streams=False):
        args = [str(a) for a in args]
        args_pretty_string = ' '.join(args)

        print_update_info(args_pretty_string)

        pipe_streams = subprocess.PIPE if pipe_streams else None

        return subprocess.Popen(args, stdin=pipe_streams, stdout=pipe_streams, stderr=pipe_streams)

    @staticmethod
    def __log_install_results(rc, require_package, args, std_err, std_output):
        if rc == 0:
            print_update_forced('install requirement: %s', require_package)
            print_update_forced('ran %s (%s)\n%s\n%s', ' '.join(args), rc, std_err, std_output)
            return

        print_update_forced('Failed to install requirement: %s', require_package)
        print_update_forced('Failed to run %s (%s)\n%s\n%s', ' '.join(args), rc, std_err, std_output)

    def _install_package(self, require_package, pipe_streams=True):
        args = self._get_install_args(require_package)

        p = self._run_command(args, pipe_streams=pipe_streams)

        rc, std_output, std_err = self.__communicate_with_install(p)

        if pipe_streams:
            self.__log_install_results(rc, require_package, args, std_err, std_output)

        if rc != 0:
            raise FailedInstalled('Failed to install requirement: %s (%s)' % (require_package, args))

        self.__fixup_namespace_packages()

    def install_package(self, require_package, pipe_streams=True, throw_exception=False):
        try:
            self._install_package(require_package, pipe_streams=pipe_streams)

            return True
        except Exception as ex:
            if throw_exception:
                raise

            print_update_error("install %s failed: %s", require_package, ex)

            return False

    @classmethod
    def _get_keywords_from_env_var(cls):
        return os.environ.get('PIP_KEYWORDS', '')

    @classmethod
    def _get_dist(cls, package_name):
        import pkg_resources

        return pkg_resources.get_distribution(package_name)

    @classmethod
    def get_dist_version(cls, package_name):
        from pkg_resources import DistributionNotFound

        try:
            dist = cls._get_dist(package_name)
        except DistributionNotFound:
            return None

        return dist.version

    @classmethod
    def _get_keywords(cls, package):
        try:
            dist = cls._get_dist(package)
        except pkg_resources.DistributionNotFound:
            return cls._get_keywords_from_env_var()

        parsed_pkg_info = getattr(dist, '_parsed_pkg_info', None)

        if parsed_pkg_info is None:
            return cls._get_keywords_from_env_var()

        print_update_debug('get_keywords for: %s are %s ', package, parsed_pkg_info.get('Keywords'))

        return parsed_pkg_info.get('Keywords', '')

    @classmethod
    def _get_package_location(cls, package):
        try:
            dist = cls._get_dist(package)
        except pkg_resources.DistributionNotFound:
            return ''

        return dist.location

    @classmethod
    def __safe_string_as_string(cls, stream):
        if stream and not isinstance(stream, six.string_types):
            stream = stream.decode('utf-8')

        return stream

    @classmethod
    def __communicate_with_install(cls, p):
        std_err = std_output = None

        try:
            std_output, std_err = p.communicate()
        except Exception as ex:
            six.raise_from(FailedInstalled(str(ex)), ex)

        std_err = cls.__safe_string_as_string(std_err)
        std_output = cls.__safe_string_as_string(std_output)

        return p.returncode, std_output, std_err

    @staticmethod
    def __fixup_namespace_packages():
        for path_item in sys.path:
            __import__('pkg_resources').fixup_namespace_packages(path_item)

    @abc.abstractmethod
    def _latest_version(self, package):
        """
        get the latest version
        :param package:
        :return:
        """

    @abc.abstractmethod
    def _get_install_args(self, require_package):
        """

        :param require_package:
        :param pipe_streams:
        :param throw_exception:
        :return:
        """
