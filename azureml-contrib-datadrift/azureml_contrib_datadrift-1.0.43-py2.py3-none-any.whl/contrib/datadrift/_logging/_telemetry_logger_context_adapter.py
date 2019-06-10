# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""A file for telemetry logger context adapter classes."""

import logging


class _TelemetryLoggerContextAdapter(logging.LoggerAdapter):
    """An adapter for loggers to keep contextual information in logging output."""

    def __init__(self, logger, context):
        """
        Initialize a new instance of the class.

        :param logger:
        :param context:
        """
        self._context = context
        super(_TelemetryLoggerContextAdapter, self).__init__(logger, None)

    @property
    def context(self):
        """Return current context info."""
        return self._context

    @property
    def manager(self):
        return self.logger.manager

    @manager.setter
    def manager(self, value):
        self.logger.manager = value

    @property
    def name(self):
        return self.logger.name

    def process(self, msg, kwargs):
        """
        Process the log message.

        :param msg: The log message.
        :type msg: str
        :param kwargs: The arguments with properties.
        :type kwargs: dict
        """
        if 'extra' not in kwargs:
            kwargs["extra"] = {}

        if self._context:
            if "properties" not in kwargs["extra"]:
                kwargs["extra"]["properties"] = {}
            kwargs["extra"]["properties"].update(self._context)

        return msg, kwargs

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False):
        """
        Low-level log implementation, proxied to allow nested logger adapters.
        """
        return self.logger._log(
            level,
            msg,
            args,
            exc_info=exc_info,
            extra=extra,
            stack_info=stack_info,
        )
