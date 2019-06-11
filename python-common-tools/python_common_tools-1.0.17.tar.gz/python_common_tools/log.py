# -*- coding: utf-8 -*-
__author__ = '陈章'
__date__ = '2019-04-24 19:44'

from logzero import logger
import logzero


class ILog:
    @classmethod
    def setup_logger(cls, logfile=None, maxBytes=10_000_000, backupCount=3):
        if logfile:
            logzero.logfile(logfile, maxBytes=maxBytes, backupCount=backupCount, encoding='utf-8')
        return logger


setup_logger = ILog.setup_logger
