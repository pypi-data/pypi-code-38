# -*- coding: utf-8 -*-
from .version import version_string
from .lib.CommonLogger import debug, info, warn, error, set_log_level, add_log_cfg
from .cli.router import Router
from .lib.path_helper import PathHelper


class logger:
    '''
    用于暴露给客户用的日志模块
    '''

    @classmethod
    def debug(cls, msg, es=None, frame=3):
        debug(msg, es, frame)

    @classmethod
    def info(cls, msg, es=None, frame=3):
        info(msg, es, frame)

    @classmethod
    def warn(cls, msg, es=None, frame=3):
        warn(msg, es, frame)

    @classmethod
    def error(cls, msg, es=None, frame=3):
        error(msg, es, frame)

    @classmethod
    def set_log_level(cls, log_cfg_name, loglevel):
        set_log_level(log_cfg_name, loglevel)

    @classmethod
    def add_log_cfg(cls, log_cfg):
        add_log_cfg(log_cfg)


__all__ = [
    'logger', '__version__', 'Router', 'PathHelper'
]

disable_unicode_literals_warning = False

__version__ = version_string
