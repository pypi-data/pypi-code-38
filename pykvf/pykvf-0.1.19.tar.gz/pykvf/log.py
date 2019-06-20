#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

@author: banixc

@contact: banixc@gmail.com

@time: 2017/9/30 14:57

@desc: log工具
    通过名字获得唯一的log
    console_logger直接打印在控制台中
"""
import logging
import logging.handlers

try:
    import cloghandler
except ImportError:
    cloghandler = None

logger_set = set()

default_message_fmt = '[%(asctime)s.%(msecs)01d][%(process)d][%(filename)s:%(lineno)s][%(levelname)s][%(message)s]'
default_date_fmt = '%Y-%m-%d %H:%M:%S'
default_log_level = logging.DEBUG

CONSOLE_LOG_NAME = 'std_in_out_err'
LOG_SIZE = 1024 * 1024 * 100  # 100M


def init_log(log_path, name='__default', filemode='a', message_fmt=default_message_fmt, date_fmt=default_date_fmt,
             level=logging.DEBUG):
    if name in logger_set:
        return logging.getLogger(name)

    try:
        if cloghandler:
            handler = cloghandler.ConcurrentRotatingFileHandler(log_path, filemode, 1024 * 1024 * 100, 10)
        else:
            handler = logging.handlers.RotatingFileHandler(log_path, filemode, 1024 * 1024 * 100, 10)
    except IOError as e:
        console_logger.error(repr(e))
        return exit(1)

    formatter = logging.Formatter(message_fmt, date_fmt)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger_set.add(name)

    return logger


def get_log(name='__default'):
    if name in logger_set:
        return logging.getLogger(name)
    else:
        return None


def get_console_logger(level=logging.DEBUG):
    logger_name = 'std_in_out_err'
    if logger_name in logger_set:
        return logging.getLogger(logger_name)

    handler = logging.StreamHandler()
    formatter = logging.Formatter(default_message_fmt, default_date_fmt)
    handler.setFormatter(formatter)

    log = logging.getLogger(logger_name)
    log.setLevel(level)
    log.addHandler(handler)

    logger_set.add(logger_name)
    return log


console_logger = get_console_logger()
