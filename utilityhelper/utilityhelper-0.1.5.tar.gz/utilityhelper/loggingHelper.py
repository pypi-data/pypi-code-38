#coding:utf-8
# !/usr/local/python/bin

from __future__ import (print_function, unicode_literals)
from utilityhelper.compatible import *

__author__ = "gongleilei"
__status__ = "Development"

# __all__ = ['set_logger', 'debug', 'info', 'warning', 'error',
#            'critical', 'exception']

import os
import sys
import logging  # @UnusedImport
import logging.handlers

# Color escape string
COLOR_RED = '\033[1;31m'
COLOR_GREEN = '\033[1;32m'
COLOR_YELLOW = '\033[1;33m'
COLOR_BLUE = '\033[1;34m'
COLOR_PURPLE = '\033[1;35m'
COLOR_CYAN = '\033[1;36m'
COLOR_GRAY = '\033[1;37m'
COLOR_WHITE = '\033[1;38m'
COLOR_RESET = '\033[1;0m'

# Define log color
LOG_COLORS = {
    'DEBUG': '%s',
    'INFO': COLOR_GREEN + '%s' + COLOR_RESET,
    'WARNING': COLOR_YELLOW + '%s' + COLOR_RESET,
    'ERROR': COLOR_RED + '%s' + COLOR_RESET,
    'CRITICAL': COLOR_RED + '%s' + COLOR_RESET,
    'EXCEPTION': COLOR_RED + '%s' + COLOR_RESET,
}

# Global logger
g_logger = []

#继承logging模块的日志级别
LEVEL_CRITICAL = logging.CRITICAL
LEVEL_FATAL = logging.FATAL
LEVEL_ERROR = logging.ERROR
LEVEL_WARNING = logging.WARNING
LEVEL_WARN = LEVEL_WARNING
LEVEL_INFO = logging.INFO
LEVEL_DEBUG = logging.DEBUG
LEVEL_NOTSET = logging.NOTSET

HANDLER_TYPE_STREAM = 1
HANDLER_TYPE_FILE   = 2
HANDLER_TYPE_SMTP   = 3
HANDLER_TYPE_WINDOW = 4

class EncodingFormatter(logging.Formatter):

    def __init__(self, fmt, datefmt=None, encoding=None):
        super(EncodingFormatter, self).__init__(fmt, datefmt)
        self.encoding = encoding

    def format(self, record):
        result = logging.Formatter.format(self, record)
        if not PY3:
            if isinstance(result, unicode):
                result = result.encode(self.encoding or 'utf-8')
        return result

class ColoredFormatter(logging.Formatter):
    '''@summary A colorful formatter.
    '''
    def __init__(self, fmt=None, datefmt=None):
        super(ColoredFormatter, self).__init__(fmt, datefmt)

    def format(self, record):
        level_name = record.levelname
        msg = logging.Formatter.format(self, record)
        msg = LOG_COLORS.get(level_name, '%s') % msg
        return msg


class LogManger(object):
    
    @classmethod
    def getLogger(cls, name=None, LowestLevel=logging.WARNING):
        if name is None:
            logger = logging.getLogger()
            if logger not in g_logger:
                logger.setLevel(LowestLevel)
                g_logger.append(logger)
        else:
            logger = logging.getLogger(name)
            if logger not in g_logger:
                logger.setLevel(LowestLevel)
                g_logger.append(logger)
        
        return logger

    @classmethod
    def addHandler(cls, loggers, handlertype, level, fmt, **kwargs):
        if handlertype == HANDLER_TYPE_STREAM:
            LogManger.__add_streamhandler(loggers, level, fmt, **kwargs)
        elif handlertype == HANDLER_TYPE_FILE:
            LogManger.__add_filehandler(loggers, level, fmt, **kwargs)
        elif handlertype == HANDLER_TYPE_SMTP:
            LogManger.__add_mailhandler(loggers, level, fmt, **kwargs)
        elif handlertype == HANDLER_TYPE_WINDOW:
            LogManger.__add_windowhandler(loggers, level, fmt, **kwargs)

    @staticmethod
    def __add_handler(HanderClass, loggers, level, fmt, colorful, **kwargs):
        '''Add a configured handler to the global logger.'''
        global g_logger
        if isinstance(level, str):
            level = getattr(logging, level.upper(), logging.DEBUG)
        handler = HanderClass(**kwargs)
        handler.setLevel(level)
        
        if colorful:
            formatter = ColoredFormatter(fmt)
        else:
            formatter = EncodingFormatter(fmt)
    
        handler.setFormatter(formatter)
        for logger in loggers:
            if g_logger.count(logger) != 0:
                logger.addHandler(handler)
    
        return handler

    @staticmethod
    def __add_streamhandler(loggers, level, fmt):
        '''Add a stream handler to the global logger.'''
        return LogManger.__add_handler(logging.StreamHandler, loggers, level, fmt, False)
    
    @staticmethod
    def __add_filehandler(loggers, level, fmt, filename, mode, backup_count, limit, when):
        '''Add a file handler to the global logger.'''
        kwargs = {}
    
        # If the filename is not set, use the default filename
        if filename is None:
            filename = getattr(sys.modules['__main__'], '__file__', 'log.py')
            filename = os.path.basename(filename.replace('.py', '.log'))
            #path = os.path.abspath(filename)
            #filename = os.path.join('/tmp', filename)
            #filename = os.path.join(path, filename)
        kwargs['filename'] = filename
    
        # Choose the filehandler based on the passed arguments
        if backup_count == 0:  # Use FileHandler
            cls = logging.FileHandler
            kwargs['mode'] = mode
        elif when is None:  # Use RotatingFileHandler
            cls = logging.handlers.RotatingFileHandler
            kwargs['maxBytes'] = limit
            kwargs['backupCount'] = backup_count
            kwargs['mode'] = mode
        else:  # Use TimedRotatingFileHandler
            cls = logging.handlers.TimedRotatingFileHandler
            kwargs['when'] = when
            kwargs['interval'] = limit
            kwargs['backupCount'] = backup_count
    
        return LogManger.__add_handler(cls, loggers, level, fmt, False, **kwargs)

    @staticmethod
    def __add_windowhandler(loggers, level, fmt, window):
        '''Add a window handler to the global logger.'''
        kwargs = {}
        kwargs['stream'] = window
        return LogManger.__add_handler(logging.StreamHandler, loggers, level, fmt, False, **kwargs)

    @staticmethod
    def __add_mailhandler(loggers, level, fmt, 
                        mailhost, fromaddr, toaddrs, subject,
                        credentials=None, secure=None):
        kwargs = {}
        kwargs['mailhost'] = mailhost
        kwargs['fromaddr'] = fromaddr
        kwargs['toaddrs'] = toaddrs
        kwargs['subject'] = subject
        kwargs['credentials'] = credentials
        kwargs['secure'] = secure
        
        return LogManger.__add_handler(logging.handlers.SMTPHandler, loggers, level, fmt, True, **kwargs)

if __name__ == "__main__":
    __fmt = '【%(levelname)s】 - %(asctime)s - %(name)s -%(thread)d -%(threadName)s - %(message)s'
    _g_logger = LogManger.getLogger(None, LEVEL_DEBUG)
    LogManger.addHandler((_g_logger,), HANDLER_TYPE_STREAM, LEVEL_DEBUG, __fmt)
    _g_logger.debug("logdebug={}".format('message'))
