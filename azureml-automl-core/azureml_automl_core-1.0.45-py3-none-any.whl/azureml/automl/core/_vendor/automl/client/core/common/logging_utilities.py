"""Utility module for logging."""
from typing import Any, Dict, List, Optional, Tuple, Union

import contextlib
import functools
import json
import logging
import logging.handlers as handlers
import os
import sys
import threading
import traceback
import uuid

from datetime import datetime

from .constants import TelemetryConstants, DEFAULT_LOGGING_APP_NAME
from .exceptions import AutoMLException, ErrorTypes, ResourceException
from .types import DataInputType
from .memory_utilities import get_data_memory_size

# import telemetry package if available.
try:
    from azureml.telemetry import get_telemetry_log_handler
    from azureml.telemetry.logging_handler import AppInsightsLoggingHandler

    telemetry_imported = True
except ImportError:
    telemetry_imported = False


file_handlers = {}  # type: Dict[str, logging.Handler]
log_cache_lock = threading.Lock()
file_loggers = {}   # type: Dict[Tuple[str, int], logging.Logger]


def _get_null_logger(name: str = 'null_logger') -> logging.Logger:
    null_logger = logging.getLogger(name)
    null_logger.addHandler(logging.NullHandler())
    null_logger.propagate = False
    return null_logger


NULL_LOGGER = _get_null_logger()


def log_traceback(exception: BaseException,
                  logger: Optional[logging.Logger],
                  override_error_msg: Optional[str] = None,
                  is_critical: Optional[bool] = True) -> None:
    """
    Log exception traces.

    :param exception: The exception to log.
    :param logger: The logger to use.
    :param override_error_msg: The message what to display that will override the current error_msg.
    :param is_critical: If is_critical, the logger will use log.critical, otherwise log.error.
    """
    if logger is None:
        logger = NULL_LOGGER

    # Appropriately classify MemoryErrors that may pop up anywhere in our code
    if isinstance(exception, MemoryError):
        exception = ResourceException.from_exception(
            exception,
            "Unable to allocate enough memory for this operation. Please consider increasing available memory.")

    if isinstance(exception, AutoMLException):
        error_type = exception.error_type
        error_msg = str(exception)
        if override_error_msg is not None:
            error_msg = override_error_msg
    else:
        error_type = ErrorTypes.Unclassified
        error_msg = "Inner Exception raised. Error message is hidden."

    traceback_obj = exception.__traceback__ or sys.exc_info()[2]
    if traceback_obj is not None:
        traceback_msg = ''.join(_CustomStackSummary.format(traceback.extract_tb(traceback_obj)))
    else:
        traceback_msg = 'Not available (exception was not raised but was returned directly)'

    message = [
        'Type: {}'.format(error_type),
        'Class: {}'.format(exception.__class__.__name__),
        'Message: {}'.format(error_msg),
        'Traceback:',
        traceback_msg
    ]
    custom_dimensions = {
        'error_type': error_type,
        'exception_class': exception.__class__.__name__,
        'exception_message': error_msg,
        'exception_traceback': traceback_msg
    }
    if is_critical:
        logger.critical('\n'.join(message), extra={'properties': custom_dimensions})
    else:
        logger.error('\n'.join(message), extra={'properties': custom_dimensions})


def log_data_info(logger: logging.Logger,
                  data_name: str,
                  data: DataInputType,
                  run_id: Optional[str] = None) -> None:
    """
    Log datatype, shape and datasize.

    :param logger: logger object.
    :param data_name: string that represent the name of the data.
    :param data: the real data.
    :param run_id: the run_id of the run
    :return: None
    """
    prefix = "[ParentRunId:{}]".format(run_id) if run_id is not None else ""
    logger.info(
        "{}{} datatype is {}, shape is {}, datasize is {}.".format(
            prefix, data_name, type(data), data.shape, get_data_memory_size(data)
        )
    )


def get_logger(namespace: Optional[str] = None,
               filename: Optional[str] = None,
               verbosity: int = logging.DEBUG,
               extra_handlers: Optional[List[logging.Handler]] = None,
               component_name: Optional[str] = None) -> logging.Logger:
    """
    Create the logger with telemetry hook.

    :param namespace: The namespace for the logger
    :param filename: log file name
    :param verbosity: logging verbosity
    :param extra_handlers: any extra handlers to attach to the logger
    :param component_name: component name
    :return: logger if log file name and namespace are provided otherwise null logger
    :rtype
    """
    if filename is None or namespace is None:
        return NULL_LOGGER

    with log_cache_lock:
        global file_loggers
        global file_handlers

        key = (filename, verbosity)
        if key in file_loggers:
            return file_loggers[key]

        if filename not in file_handlers:
            handler = handlers.RotatingFileHandler(filename, maxBytes=1000000, backupCount=9)
            log_format = '%(asctime)s - %(levelname)s - %(lineno)d : %(message)s'
            formatter = logging.Formatter(log_format)
            handler.setFormatter(formatter)
            file_handlers[filename] = handler

        logger_name = '%s_%s' % (filename, str(verbosity))
        logger = logging.getLogger(namespace).getChild(logger_name)
        logger.addHandler(file_handlers[filename])
        logger.setLevel(verbosity)

        if extra_handlers is not None:
            for h in extra_handlers:
                logger.addHandler(h)

        logger.propagate = False
        file_loggers[key] = logger

        if telemetry_imported:
            if not _found_handler(logger, AppInsightsLoggingHandler):
                logger.addHandler(get_telemetry_log_handler(component_name=component_name))

        return logger


def cleanup_log_map(log_filename: str, verbosity: int = logging.DEBUG) -> None:
    """
    Cleanup log map.

    :param log_filename: log file name
    :param verbosity: log verbosity
    :return:
    """
    with log_cache_lock:
        logger = file_loggers.pop((log_filename, verbosity), None)
        handler = file_handlers.pop(log_filename, None)
        if handler:
            if logger:
                logger.removeHandler(handler)
            handler.close()


def cleanup_all_loggers() -> None:
    """
    Clean up all loggers without using logging.shutdown().

    :return:
    """
    with log_cache_lock:
        global file_loggers
        global file_handlers
        for k in file_loggers:
            logger = file_loggers[k]
            logger.handlers = []
        for k_tuple in file_handlers:
            handler = file_handlers[k_tuple]
            handler.close()
            del handler
        file_loggers = {}
        file_handlers = {}


def function_debug_log_wrapped(f: Any) -> Any:
    """Add logs wrapper around transformer class function."""
    @functools.wraps(f)
    def debug_log_wrapped(self, *args, **kwargs):
        self._logger_wrapper(
            "debug", "[Class:{}][Function:{}] Started.".format(
                self.__class__.__name__, f.__name__
            )
        )
        r = f(self, *args, **kwargs)
        self._logger_wrapper(
            "debug", "[Class:{}][Function:{}] Ended.".format(
                self.__class__.__name__, f.__name__
            )
        )
        return r

    return debug_log_wrapped


BLACKLISTED_LOGGING_KEYS = [
    'path', 'resource_group', 'workspace_name', 'data_script', 'debug_log',
    'time_column_name', 'grain_column_names', 'drop_column_names'
]


def remove_blacklisted_logging_keys_from_dict(dict_obj: Dict[str, Any]) -> None:
    """Recursively remove the key from a dict."""
    keys = [k for k in dict_obj.keys()]
    blacklisted_keys = set(BLACKLISTED_LOGGING_KEYS)
    for k in keys:
        if k in blacklisted_keys:
            del dict_obj[k]
    for v in dict_obj.values():
        if isinstance(v, dict):
            remove_blacklisted_logging_keys_from_dict(v)


def remove_blacklisted_logging_keys_from_json_str(json_str: str) -> str:
    """Recursively remove the key from a json str and return a json str."""
    try:
        dict_obj = json.loads(json_str)
        remove_blacklisted_logging_keys_from_dict(dict_obj)
        return json.dumps(dict_obj)
    except Exception:
        # Delete the whole string since it cannot be parsed properly
        return "***Information Scrubbed For Logging Purposes***"


def log_system_info(logger: logging.Logger, prefix_message: str = '') -> None:
    """
    Log cpu, memory and OS info.

    :param logger: logger object
    :param prefix_message: string that in the prefix in the log
    :return: None
    """
    if prefix_message is None:
        prefix_message = ''

    try:
        import psutil
        logger.info("{}CPU logical cores: {}, CPU cores: {}, virtual memory: {}, swap memory: {}.".format(
            prefix_message,
            psutil.cpu_count(), psutil.cpu_count(logical=False),
            psutil.virtual_memory().total, psutil.swap_memory().total)
        )
    except ImportError:
        logger.warning("psutil not found, skipping logging cpu and memory")

    import platform
    logger.info("{}Platform information: {}.".format(prefix_message, platform.platform()))


def _found_handler(logger: logging.Logger, handle_name: Any) -> bool:
    """
    Check logger with the given handler and return the found status.

    :param logger: Logger
    :param handle_name: handler name
    :return: boolean: True if found else False
    """
    for log_handler in logger.handlers:
        if isinstance(log_handler, handle_name):
            return True

    return False


@contextlib.contextmanager
def log_activity(logger: logging.Logger, activity_name: str = '', activity_type: str = '',
                 custom_dimensions: Dict[str, Any] = {}) -> Any:
    """
    Log the activity status with duration.

    :param logger: logger
    :param activity_name: activity name
    :param activity_type: activity type
    :param custom_dimensions: custom dimensions
    """
    activity_info = dict(activity_id=str(uuid.uuid4()), activity_name=activity_name, activity_type=activity_type) \
        # type: Dict[str, Union[str, float]]

    properties = dict()
    activity_info.update(custom_dimensions)
    properties['properties'] = activity_info

    completion_status = TelemetryConstants.SUCCESS

    start_time = datetime.utcnow()
    logger.info("ActivityStarted: {}".format(activity_name), extra=properties)

    try:
        yield
    except Exception:
        completion_status = TelemetryConstants.FAILURE
        raise
    finally:
        end_time = datetime.utcnow()
        duration_ms = round((end_time - start_time).total_seconds() * 1000, 2)
        activity_info["durationMs"] = duration_ms
        activity_info["completionStatus"] = completion_status

        logger.info("ActivityCompleted: Activity={}, HowEnded={}, Duration={}[ms]".
                    format(activity_name, completion_status, duration_ms), extra=properties)


class LogConfig:
    """
    Class containing the information needed to create a new logger.

    The Python logger is not serializable, so passing this data is sufficient to recreate a logger in a subprocess
    where all arguments must be serializable.
    """

    def __init__(self, log_filename: str, log_verbosity: int, log_namespace: str) -> None:
        """
        Construct a LogConfig object.

        :param log_filename: name of the log file
        :param log_verbosity: the logging verbosity level
        :param log_namespace: the logging namespace
        """
        self._log_filename = log_filename
        self._log_verbosity = log_verbosity
        self._log_namespace = log_namespace
        self._custom_dimensions = {'app_name': DEFAULT_LOGGING_APP_NAME}

    def get_params(self) -> Tuple[str, int, str]:
        """Get the logging params."""
        return self._log_filename, self._log_verbosity, self._log_namespace

    def get_filename(self) -> str:
        """Get the log filename."""
        return self._log_filename

    def get_namespace(self) -> str:
        """Get the log namespace."""
        return self._log_namespace

    def get_verbosity(self) -> int:
        """Get the log verbosity."""
        return self._log_verbosity

    def get_component_name(self) -> str:
        """Get the component name."""
        return TelemetryConstants.COMPONENT_NAME

    def get_custom_dimensions(self) -> Dict[str, Any]:
        """Get the custom dimensions."""
        return self._custom_dimensions

    def set_custom_dimensions(self, custom_dimensions: Dict[str, Any]) -> None:
        """
        Set the custom dimensions according to existing loggers.

        :param custom_dimensions: Custom dimensions to be added to the log.
        """
        self._custom_dimensions.update(custom_dimensions)


class _CustomStackSummary(traceback.StackSummary):
    """Subclass of StackSummary."""

    def format(self):
        """Format the stack ready for printing.

        Returns a list of strings ready for printing.  Each string in the
        resulting list corresponds to a single frame from the stack.
        Each string ends in a newline; the strings may contain internal
        newlines as well, for those items with source text lines.
        """
        result = []
        for frame in self:
            row = ['  File "{}", line {}, in {}\n'.format(
                os.path.basename(frame.filename), frame.lineno, frame.name)]
            if frame.line:
                row.append('    {}\n'.format(frame.line.strip()))
            if frame.locals:
                for name, value in sorted(frame.locals.items()):
                    row.append('    {name} = {value}\n'.format(name=name, value=value))
            result.append(''.join(row))
        return result
