# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Telemetry logger helper class"""
import logging

try:
    from azureml.telemetry import get_telemetry_log_handler
    from azureml.telemetry.activity import log_activity as _log_activity, ActivityType
    from azureml.telemetry.logging_handler import AppInsightsLoggingHandler
    telemetryImported = True
    DEFAULT_ACTIVITY_TYPE = ActivityType.INTERNALCALL
except ImportError:
    telemetryImported = False
    DEFAULT_ACTIVITY_TYPE = "InternalCall"


class _NullContextManager(object):
    """A class for null context manager"""
    def __init__(self, dummy_resource=None):
        self.dummy_resource = dummy_resource

    def __enter__(self):
        return self.dummy_resource

    def __exit__(self, *args):
        pass


class _TelemetryLogger:
    """A class for telemetry logger"""
    def __init__(self, *args, **kwargs):
        """constructor"""
        super(_TelemetryLogger, self).__init__(*args, **kwargs)

    @staticmethod
    def get_telemetry_logger(name, verbosity=logging.DEBUG):
        """
        gets just the telemetry logger if opted in
        :param name: name of the logger
        :type name: str
        :param verbosity: verbosity
        :type verbosity: int
        :return: logger
        :rtype: logging.Logger
        """
        logger = logging.getLogger(__name__).getChild(name)
        logger.propagate = False
        logger.setLevel(verbosity)

        if telemetryImported:
            if not _TelemetryLogger._found_handler(logger, AppInsightsLoggingHandler):
                logger.addHandler(get_telemetry_log_handler())

        return logger

    @staticmethod
    def log_activity(logger, activity_name, activity_type=DEFAULT_ACTIVITY_TYPE, custom_dimensions=None):
        """
        the wrapper of log_activity from azureml-telemetry
        :param logger: the logger object
        :type logger: logging.Logger
        :param activity_name: the name of the activity which should be unique per the wrapped logical code block
        :type activity_name: str
        :param activity_type: the type of the activty
        :type activity_type: str
        :param custom_dimensions: custom properties of the activity
        :type custom_dimensions: dict
        """
        if telemetryImported:
            return _log_activity(logger, activity_name, activity_type, custom_dimensions)
        else:
            return _NullContextManager(dummy_resource=logger)

    @staticmethod
    def _found_handler(logger, handle_name):
        """
        checks logger for the given handler and returns the found status
        :param logger: Logger
        :param handle_name: handler name
        :return: boolean: True if found else False
        """
        for log_handler in logger.handlers:
            if isinstance(log_handler, handle_name):
                return True

        return False
