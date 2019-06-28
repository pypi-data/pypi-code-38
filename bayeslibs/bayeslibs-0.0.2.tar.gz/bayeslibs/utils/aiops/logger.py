"""
@project:medical_robot_backend
@language:python3
@create:2019/4/26
@author:qianyang@aibayes.com
@description:none
"""
import logging
import inspect
import os
from logging.handlers import RotatingFileHandler
from .setting import LOG_DICT


class Logger:
    def __init__(self):
        pass
    
    @staticmethod
    def __create_logger(module):
        if module not in LOG_DICT:
            module = 'default'
        log_name = LOG_DICT[module]['log_name']
        msg_fmt = '[%(levelname)s][%(asctime)s]%(message)s'
        date_fmt = '%Y-%m-%d %H:%M:%S'
        formatter = logging.Formatter(fmt=msg_fmt, datefmt=date_fmt)
        _rt_handler = RotatingFileHandler(log_name, maxBytes=20 * 1024 * 1024, backupCount=5)
        _rt_handler.setFormatter(formatter)
        logger_ = logging.getLogger(module)
        if len(logger_.handlers) < 1:
            logger_.addHandler(_rt_handler)
        logger_.setLevel(LOG_DICT[module]['log_level'])
        return logger_

    @staticmethod
    def __log_message(file_path, line_no, author, message):
        return '[{0}][line:{1}][{2}]{3}'.format(file_path, line_no, author, message)

    @staticmethod
    def __log_writer(logger_, level, msg):
        if level is 'critical':
            logger_.critical(msg)
        elif level is 'error':
            logger_.error(msg)
        elif level is 'warning':
            logger_.warning(msg)
        elif level is 'info':
            logger_.info(msg)
        else:
            logger_.debug(msg)

    @staticmethod
    def __module_path(call_stack):
        file_path = os.path.basename(call_stack)
        dir_path = os.path.basename(os.path.dirname(call_stack))
        dir_dir_path = os.path.basename(os.path.dirname(os.path.dirname(call_stack)))
        if dir_path and dir_path is not file_path:
            file_path = '/{}/{}'.format(dir_path, file_path)
        if dir_dir_path and dir_dir_path is not dir_path:
            file_path = '.../{}{}'.format(dir_dir_path, file_path)
        return file_path
    
    @staticmethod
    def __log_msg(module='default'):
        try:
            logger_ = Logger.__create_logger(module)
        except KeyError:
            logger_ = Logger.__create_logger('other')
            logger_.error('ModuleInputError!')
        return logger_

    @staticmethod
    def debug(message, author='bayes', module='default'):
        logger_ = Logger.__log_msg(module)
        call_stack = inspect.stack()[1]
        file_path = Logger.__module_path(call_stack[1])
        line_no = call_stack[2]
        msg = Logger.__log_message(file_path, line_no, author, message)
        logger_.debug(msg)
        
    @staticmethod
    def info(message, author='bayes', module='default'):
        logger_ = Logger.__log_msg(module)
        call_stack = inspect.stack()[1]
        file_path = Logger.__module_path(call_stack[1])
        line_no = call_stack[2]
        msg = Logger.__log_message(file_path, line_no, author, message)
        logger_.info(msg)

    @staticmethod
    def warning(message, author='bayes', module='default'):
        logger_ = Logger.__log_msg(module)
        call_stack = inspect.stack()[1]
        file_path = Logger.__module_path(call_stack[1])
        line_no = call_stack[2]
        msg = Logger.__log_message(file_path, line_no, author, message)
        logger_.warning(msg)

    @staticmethod
    def error(message, author='bayes', module='default'):
        logger_ = Logger.__log_msg(module)
        call_stack = inspect.stack()[1]
        file_path = Logger.__module_path(call_stack[1])
        line_no = call_stack[2]
        msg = Logger.__log_message(file_path, line_no, author, message)
        logger_.error(msg)

    @staticmethod
    def critical(message, author='bayes', module='default'):
        logger_ = Logger.__log_msg(module)
        call_stack = inspect.stack()[1]
        file_path = Logger.__module_path(call_stack[1])
        line_no = call_stack[2]
        msg = Logger.__log_message(file_path, line_no, author, message)
        logger_.critical(msg)
