# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains class for specifying logging detail level."""
import logging


class NewLoggingLevel(object):
    """A class for setting up logging levels."""

    def __init__(self, logger_name, level=logging.WARNING):
        """Class NewLoggingLevel constructor.

        :param logger_name:
        :type logger_name: str
        :param level:
        :type level: int
        """
        self.logger_name = logger_name
        self.logger = logging.getLogger(logger_name)
        self.old_level = self.logger.level
        self.new_level = level

    def __enter__(self):
        """Enter context manager.

        :return: logger
        :rtype: RootLogger
        """
        self.logger.setLevel(self.new_level)
        return self.logger

    def __exit__(self, et, ev, tb):
        """Exit context manager.

        :param et: Exception type
        :type et:
        :param ev: Exception value
        :type ev:
        :param tb: Traceback
        :type tb:
        """
        self.logger.setLevel(self.old_level)
