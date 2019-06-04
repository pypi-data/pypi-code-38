from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import object
import logging
from typhoon.allure_step import step
from typhoon.allure_commons.cli_logger import testlogger


def empty_step(msg, force=False):
    with step(msg, force=force):
        pass


class AllureLoggingHandler(logging.Handler):
    def emit(self, record):
        msg = "{} ({}, {})".format(record.getMessage(), record.levelname, record.name)
        empty_step(msg, force=True)


# By default all logging calls become allure steps
logging.getLogger().addHandler(AllureLoggingHandler())


class AllureCatchLogs(object):

    def __init__(self):
        self.rootlogger = logging.getLogger()
        self.root_handlers = None
        self.testlogger = testlogger
        self.cli_logs_formatter = logging.Formatter('%(asctime)s        %(indentation)s %(message)s')

    def __enter__(self):
        """
        Inside a test function:
        - Remove all handlers (incl. pytest) from root logger
        - Add all root logger handlers to testlogger.
        - Then add just AllureHandler to root logger.
        """
        self.root_handlers = list(self.rootlogger.handlers)
        for handler in self.root_handlers:
            if isinstance(handler, AllureLoggingHandler):
                continue
            handler.setFormatter(self.cli_logs_formatter)
            self.rootlogger.removeHandler(handler)
            if handler not in self.testlogger.handlers:
                self.testlogger.addHandler(handler)

    def __exit__(self, exc_type, exc_value, traceback):
        """Undo everything."""
        for handler in self.root_handlers:
            if isinstance(handler, AllureLoggingHandler):
                continue
            handler.setFormatter(None)
            if handler in self.testlogger.handlers:
                self.testlogger.removeHandler(handler)
            if handler not in self.rootlogger.handlers:
                self.rootlogger.addHandler(handler)
