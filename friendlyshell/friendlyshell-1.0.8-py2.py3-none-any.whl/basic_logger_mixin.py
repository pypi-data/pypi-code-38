"""Mixin for displaying output from a friendly shell"""
import logging
import os
import sys


class BasicLoggerMixin(object):
    """Mixin class, to be combined with a Friendly Shell, to direct log output
    to a default output stream

    The assumption here is that all Friendly Shell derived classes are
    going to use the print(), warning() and error() methods on this class
    to interact with the shell, and those methods in turn will use the
    Python logging API to delegate output to. By default those methods
    should direct their output to stdout, however if a user has s need
    to redriect the output elsewhere - like, when running a shell in
    a non-interactive or headless environment - then they can easily do
    so by simply re-configuring the default logger for the library

    Helpful links relating to logging

    https://docs.python.org/2/library/logging.html#logrecord-attributes
    https://docs.python.org/2/library/logging.html#logging-levels
    """
    def __init__(self, *args, **kwargs):
        super(BasicLoggerMixin, self).__init__(*args, **kwargs)
        self._log = logging.getLogger(__name__)

        # See if our global logger is already configured. If not, then
        # set it up wth a default configuration
        global_logger = logging.getLogger()
        if global_logger.handlers:
            self._log.debug("Handlers for global logger already defined")
            self._log.debug("Skipping custom logging configuration")
            return

        # Capture all log output by default
        global_logger.setLevel(logging.DEBUG)

        # All info messages and above are going to the console
        console_handler = logging.StreamHandler(sys.stdout)
        console_format = logging.Formatter(fmt="%(message)s")
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_format)
        global_logger.addHandler(console_handler)

        # All debug output gets redirected to a log file and marked up
        # with metadata for later debugging purposes
        log_file = os.path.join(os.getcwd(), "friendlyshell.log")
        file_handler = logging.FileHandler(log_file, 'w')
        # fmt = '%(asctime)s %(levelname)s ' \
        #       '(%(name)s.%(funcName)s.%(lineno)d) ' \
        #       '%(message)s'
        fmt = '%(asctime)s %(levelname)s ' \
              '%(message)s'
        file_formatter = logging.Formatter(fmt=fmt)
        file_handler.setFormatter(file_formatter)
        global_logger.addHandler(file_handler)

    def info(self, message, *args, **kwargs):
        """Displays an info message to the default output stream

        :param str message: text to be displayed"""
        self._log.info(message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        """Displays a non-critical warning message to the default output stream

         :param str message: text to be displayed"""
        self._log.warning(message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        """Displays a critical error message to the default output stream

        :param str message: text to be displayed"""
        self._log.error(message, *args, **kwargs)

    def debug(self, message, *args, **kwargs):
        """Displays an internal-use-only debug message to verbose log file

        :param str message: text to be displayed"""
        self._log.debug(message, *args, **kwargs)


if __name__ == "__main__":
    pass
