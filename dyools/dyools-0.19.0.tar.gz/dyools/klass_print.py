from __future__ import (absolute_import, division, print_function, unicode_literals)

import pprint
from enum import Enum

from .klass_logger import Logger


class STATE(Enum):
    INFO = 'INFO'
    ERROR = 'ERROR'
    WARNING = 'WARNING'
    SUCCESS = 'SUCCESS'
    DEBUG = 'DEBUG'


class Print(object):

    @classmethod
    def __show(cls, data, header=False, footer=False, total=None, state=False, exit=False):
        if header:
            Logger.title(header, exit=exit)
        if state == STATE.ERROR:
            Logger.error(data, exit=exit)
        elif state == STATE.WARNING:
            Logger.warning(data, exit=exit)
        elif state == STATE.SUCCESS:
            Logger.success(data, exit=exit)
        elif state == STATE.INFO:
            Logger.info(data, exit=exit)
        elif state == STATE.DEBUG:
            Logger.debug(data, exit=exit)
        if footer:
            Logger.title(footer, exit=exit)
        if total is not None:
            Logger.title('Total: {} item(s)'.format(total), exit=exit)

    @classmethod
    def info(cls, data, header=False, footer=False, total=None, exit=False):
        cls.__show(data, header, footer, total, STATE.INFO, exit=exit)

    @classmethod
    def success(cls, data, header=False, footer=False, total=None, exit=False):
        cls.__show(data, header, footer, total, STATE.SUCCESS, exit=exit)

    @classmethod
    def error(cls, data, header=False, footer=False, total=None, exit=True):
        cls.__show(data, header, footer, total, STATE.ERROR, exit=exit)

    @classmethod
    def warning(cls, data, header=False, footer=False, total=None, exit=False):
        cls.__show(data, header, footer, total, STATE.WARNING, exit=exit)

    @classmethod
    def debug(cls, data, header=False, footer=False, total=None, exit=False):
        cls.__show(data, header, footer, total, STATE.DEBUG, exit=exit)

    @classmethod
    def abort(cls, data=False, header=False, footer=False, total=None, exit=True):
        if not data:
            data = 'Aborted !'
        cls.__show(data, header, footer, total, STATE.ERROR, exit=exit)


P = pprint.pformat
