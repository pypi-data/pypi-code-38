# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Telemetry logger helper class"""
import logging
import sys

try:
    from azureml.telemetry import get_telemetry_log_handler
    from azureml.telemetry.activity import log_activity as _log_activity, ActivityType
    from azureml.telemetry.logging_handler import AppInsightsLoggingHandler

    telemetry_imported = True
    DEFAULT_ACTIVITY_TYPE = ActivityType.INTERNALCALL
except ImportError:
    telemetry_imported = False
    DEFAULT_ACTIVITY_TYPE = "InternalCall"

from ._telemetry_logger_context_formatter import _TelemetryLoggerContextFormatter
from ._telemetry_logger_context_filter import _TelemetryLoggerContextFilter
from azureml._base_sdk_common import __version__

# Follow the same pattern from azureml-telemetry
# The instrumentation key is needed in code to send instrumentation to service level monitoring
# This key is used for writing instrumentation only, so there is no log leaking, but cannot prevent spoofing logs
INSTRUMENTATION_KEY = '436f6faa-027f-4eb0-b08a-af3ce696ba01'
INSTRUMENTATION_KEY_TEST = 'b79fa9a1-005c-4168-854a-8e7a78897bb8'
TELEMETRY_COMPONENT_NAME = "azureml.contrib.datadrift"


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

    @staticmethod
    def get_telemetry_logger(name, component_name=TELEMETRY_COMPONENT_NAME, stream_handler_verbosity=logging.WARNING):
        """
        gets the telemetry logger
        :param name: name of the logger
        :type name: str
        :param component_name: telemetry component name
        :type component_name: str
        :param stream_handler_verbosity: verbosity for stream handler
        :type stream_handler_verbosity: int
        :return: logger
        :rtype: logging.Logger
        """
        logger = logging.getLogger(__name__).getChild(name)
        logger.propagate = False
        logger.setLevel(logging.DEBUG)

        if telemetry_imported:
            if not _TelemetryLogger._found_handler(logger, AppInsightsLoggingHandler):
                logger.addHandler(get_telemetry_log_handler(instrumentation_key=INSTRUMENTATION_KEY,
                                                            component_name=component_name))

        if not _TelemetryLogger._found_handler(logger, logging.StreamHandler):
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setFormatter(_TelemetryLoggerContextFormatter())
            stream_handler.setLevel(stream_handler_verbosity)
            logger.addHandler(stream_handler)

        context = {'sdk_version': __version__, 'telemetry_component_name': component_name}
        logger.addFilter(_TelemetryLoggerContextFilter(context))

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
        if telemetry_imported:
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
