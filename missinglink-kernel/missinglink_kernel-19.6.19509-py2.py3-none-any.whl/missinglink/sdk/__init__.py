# -*- coding: utf-8 -*-
import json
import logging
import os.path
import sys
import requests
import six
from .sdk_version import get_version, get_dist

loaded = False
__version__ = get_version()


logger = logging.getLogger('missinglink')


global_root_logger_sniffer = None


def do_import():
    import missinglink_kernel

    global global_root_logger_sniffer

    global __version__
    __version__ = missinglink_kernel.get_version()

    from missinglink_kernel import \
        KerasCallback, TensorFlowProject, PyTorchProject, PyCaffeCallback, \
        ExperimentStopped, SkLearnProject, VanillaProject, \
        MissingLinkException, set_global_root_logger_sniffer

    set_global_root_logger_sniffer(global_root_logger_sniffer)

    return KerasCallback, TensorFlowProject, PyTorchProject, PyCaffeCallback, SkLearnProject, ExperimentStopped, MissingLinkException, VanillaProject


def self_update_if_not_disabled(throw_exception=False):
    from .print_or_log import print_update_info, print_update_forced, print_update_warning

    if os.environ.get('MISSINGLINKAI_DISABLE_SELF_UPDATE') is None and os.environ.get('ML_DISABLE_SELF_UPDATE') is None:
        return self_update(throw_exception=throw_exception)

    print_update_info('self update is disabled ML_DISABLE_SELF_UPDATE=%s', os.environ.get('ML_DISABLE_SELF_UPDATE'))


# This will store all the logs in memory until the first callback is created and will take control
class GlobalRootLoggerSniffer(logging.Handler):
    MAX_BACKLOGS = 1000

    def __init__(self):
        super(GlobalRootLoggerSniffer, self).__init__(logging.DEBUG)
        self.set_name('ml_global_logs_handler')
        self.root_logger = logging.getLogger()
        self.log_records = []

    def emit(self, record):
        self.log_records.append(record)

        while len(self.log_records) > self.MAX_BACKLOGS:
            self.log_records.pop(0)

    def start_capture_global(self):
        self.root_logger.addHandler(self)  # to catch direct root logging

    def stop_capture_global(self):
        self.root_logger.removeHandler(self)


def _set_logger_debug():
    root_logger = logging.getLogger()
    prev_logger_level = root_logger.level
    if root_logger.level != logging.DEBUG:
        root_logger.setLevel(logging.DEBUG)

        for handler in root_logger.handlers:
            handler.setLevel(prev_logger_level)


def catch_logs():
    if os.environ.get('ML_DISABLE_LOGGING_HOOK') is not None:
        return True

    global global_root_logger_sniffer

    _set_logger_debug()

    global_root_logger_sniffer = GlobalRootLoggerSniffer()
    global_root_logger_sniffer.start_capture_global()


def _is_hook_disabled():
    if os.environ.get('MISSINGLINKAI_DISABLE_EXCEPTION_HOOK') is not None:
        return True

    if os.environ.get('ML_DISABLE_EXCEPTION_HOOK') is not None:
        return True

    return False


def _except_hook(exc_type, value, tb):
    import traceback
    from missinglink.core.exceptions import MissingLinkException as MissingLinkExceptionCore

    if _is_hook_disabled():
        sys.__excepthook__(exc_type, value, tb)
        return

    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, value, tb)
        return

    unhandled_logger = logging.getLogger('unhandled')

    if isinstance(value, MissingLinkExceptionCore):
        unhandled_logger.critical('[%s] %s', exc_type.__name__, value)
    else:
        message = ''.join(traceback.format_exception(exc_type, value, tb))
        unhandled_logger.critical(message)

    sys.__excepthook__(exc_type, value, tb)


def setup_global_exception_handler():
    if _is_hook_disabled():
        return

    import sys

    sys.excepthook = _except_hook


KerasCallback, TensorFlowProject, PyTorchProject, PyCaffeCallback, SkLearnProject, ExperimentStopped, MissingLinkException, VanillaProject = do_import()


class FailedInstalled(Exception):
    pass


def __actual_install(require_package, pipe_streams=True):
    from .conda_util import conda_install, is_conda_env
    from .pip_util import in_venv, get_pip_index_url
    from .print_or_log import print_update_info, print_update_forced, print_update_warning

    package_keywords = get_keywords() or []
    staging = 'test' in package_keywords

    if is_conda_env():
        return conda_install(staging, require_package, pipe_streams=pipe_streams)

    running_under_virtualenv = in_venv()
    should_use_user_path = not running_under_virtualenv
    if should_use_user_path:
        print_update_info('updating %s in user path', require_package)

    return _pip_install(get_pip_index_url(staging), require_package, should_use_user_path, pipe_streams=pipe_streams)


def __safe_string_as_string(stream):
    if stream and not isinstance(stream, six.string_types):
        stream = stream.decode('utf-8')

    return stream


def __communicate_with_install(p):
    std_err = std_output = None

    try:
        std_output, std_err = p.communicate()
    except Exception as ex:
        six.raise_from(FailedInstalled(), ex)

    std_err = __safe_string_as_string(std_err)
    std_output = __safe_string_as_string(std_output)

    return p.returncode, std_output, std_err


def _get_pip_bin_path(pip_command):
    from .pip_util import which

    pip_bin_path = which(pip_command)
    if pip_bin_path is None:
        python_bin_path = sys.executable
        pip_bin_path = os.path.join(os.path.dirname(python_bin_path), 'pip')
        if not os.path.exists(pip_bin_path):
            return None

    return pip_bin_path


def _get_keywords_from_dist():
    from pkg_resources import DistributionNotFound

    try:
        dist = get_dist()
    except DistributionNotFound:
        return None

    parsed_pkg_info = getattr(dist, '_parsed_pkg_info', {})

    return parsed_pkg_info.get('Keywords', [])


def _get_keywords_from_env():
    if 'PIP_KEYWORDS' in os.environ:
        return os.environ['PIP_KEYWORDS']


def get_keywords():
    for method in (_get_keywords_from_env, _get_keywords_from_dist):
        val = method()
        if not val:
            continue

        return val

    return None


def __fixup_namespace_packages():
    for path_item in sys.path:
        __import__('pkg_resources').fixup_namespace_packages(path_item)


def install_package(require_package, pipe_streams=True):
    from .print_or_log import print_update_info, print_update_forced, print_update_warning

    p, args = __actual_install(require_package, pipe_streams=pipe_streams)

    if p is None:
        raise FailedInstalled('Failed to install requirement: %s' % require_package)

    rc, std_output, std_err = __communicate_with_install(p)

    if rc != 0:
        if pipe_streams:
            print_update_forced('Failed to install requirement: %s', require_package)
            print_update_forced('Failed to run %s (%s)\n%s\n%s', ' '.join(args), rc, std_err, std_output)

        raise FailedInstalled('Failed to install requirement: %s' % require_package)

    if pipe_streams:
        print_update_forced('install requirement: %s', require_package)
        print_update_forced('ran %s (%s)\n%s\n%s', ' '.join(args), rc, std_err, std_output)

    __fixup_namespace_packages()


def __run_pip_install(args, pipe_streams):
    from subprocess import Popen, PIPE

    pipe_streams = PIPE if pipe_streams else None
    return Popen(args, stdin=pipe_streams, stdout=pipe_streams, stderr=pipe_streams), args


def _pip_install(pip_index_url, require_packages, user_path, pipe_streams=True):
    from .pip_util import _get_pip_command, _validate_user_path
    from .print_or_log import print_update_info, print_update_forced, print_update_warning

    pip_command = _get_pip_command()

    pip_bin_path = _get_pip_bin_path(pip_command)
    if pip_bin_path is None:
        print_update_warning("pip not found, can't install %s", require_packages)
        return None, None

    if isinstance(require_packages, six.string_types):
        require_packages = [require_packages]

    args = [pip_bin_path, 'install', '--upgrade']
    if user_path:
        _validate_user_path()
        args.extend(['--user'])

    if pip_index_url:
        args.extend(['--extra-index-url', pip_index_url])

    args.extend(require_packages)

    print_update_info('{pip_command} install => {args}'.format(pip_command=pip_command, args=' '.join(args)))

    return __run_pip_install(args, pipe_streams)


# noinspection PyBroadException
def update_sdk(latest_version, throw_exception):
    require_package = 'missinglink-sdk==%s' % latest_version

    try:
        install_package(require_package)
        return True
    except Exception:
        if throw_exception:
            raise

        return False


def get_latest_pip_version(package, staging, throw_exception=False):
    from .pip_util import get_pip_host, pypi_request_timeout_seconds
    from .print_or_log import print_update_info, print_update_forced, print_update_warning

    try:
        pypi_host = get_pip_host(staging)

        url = '{pypi_host}/pypi/{package}/json'.format(pypi_host=pypi_host, package=package)
        r = requests.get(url, timeout=pypi_request_timeout_seconds)

        r.raise_for_status()

        package_info = json.loads(r.text)

        print_update_info('latest pip version %s (staging version: %s))' % (package_info['info']['version'], staging))

        return package_info['info']['version']
    except Exception as e:
        if throw_exception:
            raise

        print_update_info('could not check for new missinglink-sdk version:\n%s', e)
        logger.exception('could not check for new missinglink-sdk version:\n%s', e)
        return None


def __get_latest_version(throw_exception):
    from .conda_util import is_conda_env, get_latest_conda_version

    package_keywords = get_keywords() or []

    staging = 'test' in package_keywords

    if is_conda_env():
        latest_version = get_latest_conda_version('missinglink-sdk', staging, throw_exception=throw_exception)
    else:
        latest_version = get_latest_pip_version('missinglink-sdk', staging, throw_exception=throw_exception)

    return latest_version


def self_update(throw_exception=False):
    from .print_or_log import print_update_info

    global __version__

    version = get_version()

    if version is None:
        __version__ = 'Please install this project with setup.py'
        print_update_info("can't find current installed version (working with dev?)")
        return

    latest_version = __get_latest_version(throw_exception)

    if latest_version is None or str(version) == latest_version:
        print_update_info("working with latest missinglink version %s=%s", str(version), latest_version)
        return

    return update_sdk(latest_version, throw_exception=throw_exception)


catch_logs()
self_update_if_not_disabled()
setup_global_exception_handler()


def debug_missinglink_on():
    logging.basicConfig()
    missinglink_log = logging.getLogger('missinglink')
    missinglink_log.setLevel(logging.DEBUG)
    missinglink_log.propagate = False
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(name)s %(levelname)s %(message)s', '%Y-%m-%d %H:%M:%S')
    ch.setFormatter(formatter)
    missinglink_log.addHandler(ch)
