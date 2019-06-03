import logging as log

import statsd


class Base:
    """Base class for other "minty" classes

    This base class provides lazy-loaded "self.logger" and "self.statsd"
    properties.
    """

    __slots__ = ["_logger", "_statsd"]

    @property
    def logger(self):
        """Return this object's logger instance, create one if necessary

        :return: A logger object for this instance
        :rtype: logging.Logger
        """
        try:
            self._logger
        except AttributeError:
            self._logger = log.getLogger(self.__class__.__name__)

        return self._logger

    @property
    def statsd(self):
        """Return this object's statsd instance, create one if necessary

        :return: A statsd object for this instance
        :rtype: statsd.Client
        """
        try:
            self._statsd
        except AttributeError:
            class_name = self.__class__.__name__
            if class_name.startswith("_"):
                class_name = class_name[1:]
            self._statsd = statsd.Client(class_name)

        return self._statsd
