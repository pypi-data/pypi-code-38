from .engine import get_current_engine
from datetime import datetime
from pathlib import Path
from . import setting
import logging

logger = None
log_list = []
_is_client = False


def _get_logger():
    global logger
    if not logger:
        handlers = [logging.StreamHandler()]
        if setting.log_path:
            if not Path(setting.log_path).exists():
                raise ValueError('setting.log_path not exist.')
            handlers.append(
                logging.FileHandler(f'{setting.log_path}/{datetime.now().strftime("%Y-%m-%d %H-%M-%S")}.log'))
        logging.basicConfig(level=logging.CRITICAL, handlers=handlers, format='%(message)s')
        logger = logging.getLogger()
    return logger


def _get_engine_name():
    try:
        return get_current_engine().name
    except RuntimeError:
        return ''


def _logging(msg):
    _get_logger().critical(msg)


def _log(level, msg, name):
    if level in setting.log_filter:
        msg = f'[{datetime.now()}] {name if name else _get_engine_name()}({level.upper()}): {msg}'
        _logging(msg)
        if _is_client: log_list.append(msg)


def info(msg, name=None):
    _log('info', msg, name)


def debug(msg, name=None):
    _log('debug', msg, name)


def result(msg, name=None):
    _log('result', msg, name)


def warning(msg, name=None):
    _log('warning', msg, name)


def error(msg, name=None):
    _log('error', msg, name)


def system(msg, name=None):
    _log('system', msg, name)
