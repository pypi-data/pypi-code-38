import logging
from contextlib import contextmanager


class LogCaptureHandler(logging.Handler):
    """
    Log handler that captures all messages that it handles and exposes them as a list in `log_sequence` attribute.
    """

    def __init__(self):
        self.log_sequence = list()
        super(LogCaptureHandler, self).__init__()

    def emit(self, record):
        self.log_sequence.append(record)


class GlobFilter(logging.Filter):
    def __init__(self, glob_expression):
        self.__glob_sequence = glob_expression.split('.')
        super(GlobFilter, self).__init__()

    def filter(self, record):
        expected_seq = record.name.split('.')
        if len(expected_seq) == len(self.__glob_sequence):
            for expected, actual in zip(expected_seq, self.__glob_sequence):
                if actual != '*' and actual != expected:
                    return False
            return True
        else:
            return False


@contextmanager
def capture_log(logger_name_glob, log_level=logging.INFO):
    """
    Context manager that captures the logs of all loggers that satisfy `logger_name_glob`
    with associated severity greater or equal than `log_level`.

    Parameters
    ----------
    logger_name_glob : str
        Glob expression that specified the loggers should be captured.
    log_level : int, optional
        Minimum severity level to be captured, included. Default is logging.INFO.

    Returns
    -------
    LogCaptureHandler
        Handler that exposes the `log_sequence` attribute, which consists of a list of captured messages.

    Examples
    --------
    >>> logger = logging.getLogger('package.module.method')
    >>> with capture_log('package.module.*', log_level=logging.WARNING) as captured_logs:
    ...     logger.info("This info message won't be captured")
    ...     logger.warning("This warning message will be captured")
    ...     logger.critical("This critical message will be also captured")
    ...     print([record.msg for record in captured_logs.log_sequence])
    ['This warning message will be captured', 'This critical message will be also captured']
    """
    # Set up the handler, filter and log level
    root_logger = logging.getLogger()

    handler = LogCaptureHandler()
    handler.addFilter(GlobFilter(logger_name_glob))
    root_logger.addHandler(handler)

    default_level = root_logger.level
    root_logger.setLevel(log_level)

    yield handler

    # Clean up the handler and restore original log level
    root_logger.setLevel(default_level)
    root_logger.removeHandler(handler)
