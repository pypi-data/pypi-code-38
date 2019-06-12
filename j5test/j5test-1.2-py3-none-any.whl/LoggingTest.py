# -*- coding: utf-8 -*-

"""Convenience context for catching logs which happen in a certain code block"""
import logging
from j5.Logging import MemoryHandler

class LoggingTest(object):
    def __init__(self):
        self.log = MemoryHandler.MemoryHandler(level=logging.DEBUG)

    def __enter__(self):
        logging.getLogger().addHandler(self.log)
        return self.log

    def __exit__(self, exception_type, exception_value, exception_traceback):
        logging.getLogger().removeHandler(self.log)

