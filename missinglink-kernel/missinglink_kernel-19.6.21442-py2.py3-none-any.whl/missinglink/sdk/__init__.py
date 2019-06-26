# -*- coding: utf-8 -*-
import logging
import os.path
import sys

from .pkg_provider import PackageProvider
from .pip_util import PipPackageProvider
from .conda_util import CondaPackageProvider


loaded = False
__version__ = PackageProvider.get_dist_version('missinglink-sdk')

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
    print_update_info('self update is disabled MISSINGLINKAI_DISABLE_SELF_UPDATE=%s', os.environ.get('MISSINGLINKAI_DISABLE_SELF_UPDATE'))


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
_my_pkg_provider = PackageProvider.get_provider()


# noinspection PyBroadException
def update_sdk(latest_version, pipe_streams, throw_exception):
    require_package = 'missinglink-sdk==%s' % latest_version

    return _my_pkg_provider.install_package(require_package, pipe_streams=pipe_streams, throw_exception=throw_exception)


def self_update(pipe_streams=False, throw_exception=False):
    from .print_or_log import print_update_info, print_update_warning

    global __version__

    version = _my_pkg_provider.get_dist_version('missinglink-sdk')

    if version is None:
        __version__ = 'Please install this project with setup.py'
        print_update_info("can't find current installed version (working with dev?)")
        return

    latest_version = _my_pkg_provider.latest_version('missinglink-sdk', throw_exception=throw_exception)

    if latest_version is None:
        print_update_warning("Failed to get latest version `missinglink-sdk`")
        return

    if str(version) == latest_version:
        print_update_info("working with latest `missinglink-sdk` version %s=%s", str(version), latest_version)
        return True

    return update_sdk(latest_version, pipe_streams=pipe_streams, throw_exception=throw_exception)


catch_logs()
self_update_if_not_disabled(throw_exception=os.environ.get('_ML_SELF_UPDATE_THROW') == '1')
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
