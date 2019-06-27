# -*- coding: utf-8 -*-

"""package benutils
author    Benoit Dubois
copyright FEMTO ENGINEERING, 2019
license   GPL v3.0+
brief     Data logging facilities class.
details   Sub class logging.Formatter class to use as data logging mecanism:
          - standard logging syntax
          - allow use of rotating file mechanism of logging package
          - add header to log file
"""

from logging import Formatter
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


# =============================================================================
class RotatingFileHandlerWithHeader(RotatingFileHandler):
    """Use it when you need to add an header at log file creation,
    i.e. all the files get the header.
    Strongly inspired by:
    https://stackoverflow.com/questions/27840094/write-a-header-at-every-logfile-that-is-created-with-a-time-rotating-logger
    """

    def __init__(self, logfile, mode, maxBytes, backupCount, header=""):
        super().__init__(logfile, mode, maxBytes, backupCount)
        self._header = header
        self._log = None

    def doRollover(self):
        super().doRollover()
        if self._log is not None and self._header != "":
            self._log.info(self._header)

    def setHeader(self, header):
        self._header = header

    def configureHeaderWriter(self, header, log):
        self._header = header
        self._log = log


# =============================================================================
class TimedRotatingFileHandlerWithHeader(TimedRotatingFileHandler):
    """Use it when you need to add an header at log file creation,
    i.e. all the files get the header.
    Strongly inspired by:
    https://stackoverflow.com/questions/27840094/write-a-header-at-every-logfile-that-is-created-with-a-time-rotating-logger
    """

    def __init__(self, logfile, when, interval, header=""):
        super().__init__(logfile, when, interval)
        self._header = header
        self._log = None
        # Override the normal format method
        self.format = self.firstLineFormat

    def doRollover(self):
        super().doRollover()
        if self._log is not None and self._header != "":
            self._log.info(self._header)

    def setHeader(self, header):
        self._header = header

    def configureHeaderWriter(self, header, log):
        self._header = header
        self._log = log

    def firstLineFormat(self, record):
        # First time in, switch back to the normal format function
        self.format = super().format
        retval = self.format(record)
        if self._header != "":
            retval = self._header + "\n" + retval
        return retval


# =============================================================================
class FormatterWithHeader(Formatter):
    """Use it when you need to add a unique header, i.e. in case of rotated log,
    only the first file get the header.
    Strongly inspired by:
    https://stackoverflow.com/questions/33468174/write-header-to-a-python-log-file-but-only-if-a-record-gets-written
    """

    def __init__(self, fmt=None, datefmt=None, style='%', header=""):
        super().__init__(fmt, datefmt, style)
        self._header = header
        # Override the normal format method
        self.format = self.firstLineFormat

    def setHeader(self, header):
        self._header = header

    def firstLineFormat(self, record):
        # First time in, switch back to the normal format function
        self.format = super().format
        retval = self.format(record)
        if self._header != "":
            retval = self._header + "\n" + retval
        return retval


# =============================================================================
def test_RotatingFileHandlerWithHeader(logfile):
    # create rotating log handler
    logHandler = RotatingFileHandlerWithHeader(logfile, maxBytes=20,
                                               backupCount=3)
    form = '%(message)s'
    logFormatter = logging.Formatter(form)
    logHandler.setFormatter(logFormatter)
    # create logger
    logger = logging.getLogger('RotatingLoggerWithLogger')
    logHandler.configureHeaderWriter('# HEADER', logger)
    logger.addHandler(logHandler)
    logger.setLevel(logging.INFO)
    return logger


# =============================================================================
def test_TimedRotatingFileHandlerWithHeader(logfile):
    # create time-rotating log handler
    logHandler = TimedRotatingFileHandlerWithHeader(logfile, when='s',
                                                    interval=5)
    form = '%(message)s'
    logFormatter = logging.Formatter(form)
    logHandler.setFormatter(logFormatter)
    # create logger
    logger = logging.getLogger('TimedRotatingLoggerWithLogger')
    logHandler.configureHeaderWriter('# HEADER', logger)
    logger.addHandler(logHandler)
    logger.setLevel(logging.INFO)
    return logger


# =============================================================================
def test_FormatterWithHeader(logfile):
    logger = logging.getLogger("FormatterWithHeader")
    logger.setLevel(logging.INFO)
    formatter = FormatterWithHeader(header="# HEADER")
    logHandler = TimedRotatingFileHandler(logfile, when='s',
                                          interval=5)
    logHandler.setLevel(logging.INFO)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    return logger


# =============================================================================
if __name__ == "__main__":
    import time
    import logging

    # logger = test_RotatingFileHandlerWithHeader('rlog.log')
    logger = test_TimedRotatingFileHandlerWithHeader('trlog.log')
    # logger = test_FormatterWithHeader('flog.log')

    logger.info("This line will kick out a header first.")
    while True:
        logger.info("These lines will *not* kick out a header.")
        time.sleep(1)
