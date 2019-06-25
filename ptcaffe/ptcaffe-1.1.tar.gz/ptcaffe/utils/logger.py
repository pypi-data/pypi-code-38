# encoding: UTF-8
# written by liuyufei, 2018.07.26

from __future__ import print_function

import sys

import logging
import threading
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL, NOTSET
from logging import debug, info, warning, error, critical, exception

__all__ = ['logger', 'debug', 'info', 'warning', 'error', 'critical', 'print', 'exception',
           'set_screen_on', 'set_screen_off', 'set_file', 'getEffectiveLevel',
           'NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'MORE_INFO']

# MORE_INFO means more verbose than INFO but not as verbose as DEBUG
MORE_INFO = (DEBUG + INFO) // 2
__initialized__ = False
manager = None
set_level = None
plain_root = None
logger = sys.modules[__name__]


class ContextController:
    def __init__(self):
        self.level = logging.INFO
        self.screen = sys.__stderr__
        self.filename = None
        self.file_handler = None
        self._plain_screen = None
        self._plain_file = None
        self._fmt_screen = None
        self._fmt_file = None
        self._file_stream = None
        self.lock = threading.Lock()
        self.formatter = logging.Formatter(fmt='%(asctime)s %(message)s',
                                           datefmt='%Y-%m-%d %H:%M:%S')

    @property
    def plain_screen(self):  # type: () -> logging.Handler
        if self._plain_screen is None:
            self._plain_screen = logging.StreamHandler()
            self._plain_screen.setLevel(self.level)
        return self._plain_screen

    @property
    def fmt_screen(self):  # type: () -> logging.Handler
        if self._fmt_screen is None:
            self._fmt_screen = logging.StreamHandler()
            self._fmt_screen.setFormatter(self.formatter)
            self._fmt_screen.setLevel(self.level)
        return self._fmt_screen

    @property
    def file_stream(self):
        if self.filename is None:
            return None
        if self._file_stream is None:
            self._file_stream = open(self.filename, 'a')
        return self._file_stream

    @property
    def plain_file(self):  # type: () -> logging.Handler
        if self.filename is None:
            return None
        if self._plain_file is None and self.filename is not None:
            self._plain_file = logging.FileHandler('DUMMY_LOG_FILE', delay=True)
            self._plain_file.stream = self.file_stream
            self._plain_file.setLevel(self.level)
        return self._plain_file

    @property
    def fmt_file(self):  # type: () -> logging.Handler
        if self.filename is None:
            return None
        if self._fmt_file is None:
            self._fmt_file = logging.FileHandler('dumb_log', delay=True)
            self._fmt_file.stream = self.file_stream
            self._fmt_file.setFormatter(self.formatter)
            self._fmt_file.setLevel(self.level)
        return self._fmt_file

    def handlers(self):
        if self._fmt_file is not None:
            yield self._fmt_file
        if self._fmt_screen is not None:
            yield self._fmt_screen
        if self._plain_file is not None:
            yield self._plain_file
        if self._plain_screen is not None:
            yield self._plain_screen

    def set_level(self, level):
        with self.lock:
            logging._acquireLock()
            logging.root.setLevel(level)
            for handler in self.handlers():
                handler.setLevel(level)
            logging._releaseLock()


def __setup__():
    global manager, __initialized__, set_level
    if not __initialized__:
        logging._acquireLock()
        # add custom level 'MORE_INFO'
        logging.addLevelName(level=MORE_INFO, levelName='MORE_INFO')
        # replace default logger
        manager = ContextController()
        set_level = manager.set_level
        logging.root.handlers = [manager.fmt_screen]
        logging.root.setLevel(logging.INFO)
        logging._releaseLock()
        logging.basicConfig = lambda: None
        __initialized__ = True


def set_screen_off():
    logging._acquireLock()
    logging.root.removeHandler(manager.fmt_screen)
    logging._releaseLock()


def set_screen_on():
    logging._acquireLock()
    logging.root.addHandler(manager.fmt_screen)
    logging._releaseLock()


def set_file(filename):
    with manager.lock:
        logging._acquireLock()
        manager.filename = filename
        logging.root.addHandler(manager.fmt_file)
        logging._releaseLock()


def print(message, *args, **kwargs):
    level = kwargs.get('level', logging.INFO)
    logging._acquireLock()
    for handler in logging.root.handlers:
        handler.acquire()
        handler.formatter = None
    if logging.root.isEnabledFor(level):
        logging.root._log(level, message, args)
    for handler in logging.root.handlers:
        handler.formatter = manager.formatter
        handler.release()
    logging._releaseLock()


def more_info(msg, *args, **kwargs):
    if logging.root.isEnabledFor(MORE_INFO):
        logging.root._log(MORE_INFO, msg, args, **kwargs)


def getEffectiveLevel():
    return logging.root.getEffectiveLevel() or NOTSET

__setup__()

