#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author: zhangkai
Email: zhangkai@cmcm.com
Last modified: 2018-01-05 11:27:36
'''
import logging

from tornado.log import LogFormatter


class WatchedFileHandler(logging.handlers.WatchedFileHandler):
    '''重写handler，使指定级别的日志只写入指定的文件中'''

    def emit(self, record):
        if record.levelno == self.level:
            super(WatchedFileHandler, self).emit(record)


def Logger(filename=None, name=None, level='INFO', stream=True):
    logger = logging.getLogger(name)
    logger.setLevel(level.upper())
    logger.propagate = False
    logger.handlers = []
    datefmt = '%Y-%m-%d %H:%M:%S'
    fmt = '%(color)s[%(levelname)s %(asctime)s %(module)s:%(lineno)d]%(end_color)s %(message)s'
    if stream:
        hdlr = logging.StreamHandler()
        hdlr.setFormatter(LogFormatter(fmt=fmt, datefmt=datefmt))
        hdlr.setLevel(level)
        logger.addHandler(hdlr)

    if filename:
        hdlr = logging.handlers.WatchedFileHandler(filename=filename, mode='a', encoding='utf-8')
        hdlr.setFormatter(LogFormatter(fmt=fmt, datefmt=datefmt, color=False))
        hdlr.setLevel(level)
        logger.addHandler(hdlr)
    return logger
