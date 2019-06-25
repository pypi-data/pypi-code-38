# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""A log factory module that provides methods to log telemetric data for the Dataset SDK."""

import logging
import logging.handlers
import uuid
import os
from tempfile import gettempdir
from contextlib import contextmanager
from datetime import datetime
from functools import wraps
COMPONENT_NAME = 'azureml.dataset'
session_id = str(uuid.uuid4())
instrumentation_key = ''
version = None
default_custom_dimensions = {'app_name': 'dataset'}

try:
    from azureml.telemetry import get_telemetry_log_handler, INSTRUMENTATION_KEY, get_diagnostics_collection_info
    from azureml.telemetry.activity import log_activity as _log_activity, ActivityType
    from azureml.telemetry.logging_handler import AppInsightsLoggingHandler
    from azureml._base_sdk_common import _ClientSessionId
    session_id = _ClientSessionId
    current_folder = os.path.dirname(os.path.realpath(__file__))
    telemetry_config_path = os.path.join(current_folder, '_telemetry.json')

    telemetry_enabled, verbosity = get_diagnostics_collection_info(
        component_name=COMPONENT_NAME,
        path=telemetry_config_path)
    instrumentation_key = INSTRUMENTATION_KEY if telemetry_enabled else ''
    DEFAULT_ACTIVITY_TYPE = ActivityType.INTERNALCALL
except Exception:
    telemetry_enabled = False
    DEFAULT_ACTIVITY_TYPE = "InternalCall"


class _LoggerFactory:

    @staticmethod
    def get_logger(name, verbosity=logging.DEBUG):
        logger = logging.getLogger(__name__).getChild(name)
        logger.propagate = False
        logger.setLevel(verbosity)
        if telemetry_enabled:
            try:
                global version
                if version is None:
                    from ... import dataprep
                    version = dataprep.__version__
            except Exception:
                version = 'DEV'
            if not _LoggerFactory._found_handler(logger, AppInsightsLoggingHandler):
                logger.addHandler(get_telemetry_log_handler(component_name=COMPONENT_NAME, path=telemetry_config_path))
        else:
            os.makedirs(os.path.join(gettempdir(), 'azureml-logs', 'dataset'), exist_ok=True)
            local_log_path = os.path.join(gettempdir(), 'azureml-logs', 'dataset', 'sdk.log')
            logger.addHandler(logging.handlers.RotatingFileHandler(local_log_path, 'a', 2048000, 1))

        return logger

    @staticmethod
    def track_activity(logger, activity_name, activity_type=DEFAULT_ACTIVITY_TYPE, input_custom_dimensions=None):
        if input_custom_dimensions is not None:
            custom_dimensions = default_custom_dimensions.copy()
            custom_dimensions.update(input_custom_dimensions)
        else:
            custom_dimensions = default_custom_dimensions
        custom_dimensions.update({'source': COMPONENT_NAME, 'version': version})
        if telemetry_enabled:
            return _log_activity(logger, activity_name, activity_type, custom_dimensions)
        else:
            return _log_local_only(logger, activity_name, activity_type, custom_dimensions)

    @staticmethod
    def _found_handler(logger, handler_type):
        for log_handler in logger.handlers:
            if isinstance(log_handler, handler_type):
                return True

        return False


def track(get_logger, custom_dimensions=None):
    def monitor(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger()
            with _LoggerFactory.track_activity(logger, func.__name__, DEFAULT_ACTIVITY_TYPE, custom_dimensions):
                return func(*args, **kwargs)

        return wrapper

    return monitor


@contextmanager
def _log_local_only(logger, activity_name, activity_type, custom_dimensions):
    activity_info = dict(activity_id=str(uuid.uuid4()), activity_name=activity_name, activity_type=activity_type)
    custom_dimensions = custom_dimensions or {}
    activity_info.update(custom_dimensions)

    start_time = datetime.utcnow()
    completion_status = "Success"

    message = "ActivityStarted, {}".format(activity_name)
    logger.info(message)
    exception = None

    try:
        yield logger
    except Exception as e:
        exception = e
        completion_status = "Failure"
        raise
    finally:
        end_time = datetime.utcnow()
        duration_ms = round((end_time - start_time).total_seconds() * 1000, 2)

        custom_dimensions["completionStatus"] = completion_status
        custom_dimensions["durationMs"] = duration_ms
        message = "{} | ActivityCompleted: Activity={}, HowEnded={}, Duration={} [ms], Info = {}".format(
            start_time, activity_name, completion_status, duration_ms, repr(activity_info))
        if exception:
            message += ", Exception={}; {}".format(type(exception).__name__, str(exception))
            logger.error(message)
        else:
            logger.info(message)
