"""
Project-level logging module

"""
import os
import sys
import inspect
import logging
import logging.handlers
from pathlib import Path
from xlines.statics import local_config
from xlines._version import __version__


syslog = logging.getLogger(__version__)
syslog.setLevel(logging.DEBUG)


def mode_assignment(arg):
    """
    Translates arg to enforce proper assignment
    """
    arg = arg.upper()
    stream_args = ('STREAM', 'CONSOLE', 'STDOUT')
    try:
        if arg in stream_args:
            return 'STREAM'
        else:
            return arg
    except Exception:
        return None


def logging_prep(mode):
    """
    Summary:
        prerequisites for log file generation
    Return:
        Success | Failure, TYPE: bool
    """
    try:
        if mode == 'FILE':

            log_path = local_config['LOGGING']['LOG_PATH']
            # path: path to log dir
            path, log_dirname = os.path.split(log_path)

            if not os.path.exists(path):
                os.makedirs(path)

            if not os.path.exists(log_path):
                Path(log_path).touch(mode=0o644, exist_ok=True)

    except OSError as e:
        syslog.exception(f'{inspect.stack()[0][3]}: Failure while seeding log file path: {e}')
        return False
    return True


def getLogger(*args, **kwargs):
    """
    Summary:
        custom format logger

    Args:
        mode (str):  The Logger module supprts the following log modes:

            - log to console / stdout. Log_mode = 'stream'
            - log to file
            - log to system logger (syslog)

    Returns:
        logger object | TYPE: logging
    """

    log_mode = local_config['LOGGING']['LOG_MODE']

    # log format - file
    file_format = '%(asctime)s - %(pathname)s - %(name)s - [%(levelname)s]: %(message)s'

    # log format - stream
    stream_format = '%(pathname)s - %(name)s - [%(levelname)s]: %(message)s'

    # log format - syslog
    syslog_format = '- %(pathname)s - %(name)s - [%(levelname)s]: %(message)s'
    # set facility for syslog:
    if local_config['LOGGING']['SYSLOG_FILE']:
        syslog_facility = 'local7'
    else:
        syslog_facility = 'user'

    # all formats
    asctime_format = "%Y-%m-%d %H:%M:%S"

    # objects
    logger = logging.getLogger(*args, **kwargs)
    logger.propagate = False

    try:
        if not logger.handlers:
            # branch on output format, default to stream
            if mode_assignment(log_mode) == 'FILE':

                # file handler
                if logging_prep(mode_assignment(log_mode)):

                    f_handler = logging.FileHandler(local_config['LOGGING']['LOG_PATH'])
                    f_formatter = logging.Formatter(file_format, asctime_format)
                    f_handler.setFormatter(f_formatter)
                    logger.addHandler(f_handler)
                    logger.setLevel(logging.DEBUG)

                else:
                    syslog.warning(f'{inspect.stack()[0][3]}: Log preparation fail - exit')
                    sys.exit(1)

            elif mode_assignment(log_mode) == 'STREAM':
                # stream handlers
                s_handler = logging.StreamHandler()
                s_formatter = logging.Formatter(stream_format)
                s_handler.setFormatter(s_formatter)
                logger.addHandler(s_handler)
                logger.setLevel(logging.DEBUG)

            elif mode_assignment(log_mode) == 'SYSLOG':
                sys_handler = logging.handlers.SysLogHandler(address='/dev/log', facility=syslog_facility)
                sys_formatter = logging.Formatter(syslog_format)
                sys_handler.setFormatter(sys_formatter)
                logger.addHandler(sys_handler)
                logger.setLevel(logging.DEBUG)

            else:
                syslog.warning(
                    '%s: [WARN]: log_mode value of (%s) unrecognized - not supported' %
                    (inspect.stack()[0][3], str(log_mode))
                    )
                ex = Exception(
                    '%s: Unsupported mode indicated by log_mode value: %s' %
                    (inspect.stack()[0][3], str(log_mode))
                    )
                raise ex
    except OSError as e:
        raise e
    return logger
