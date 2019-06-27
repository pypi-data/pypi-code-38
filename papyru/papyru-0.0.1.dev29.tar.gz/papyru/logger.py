import logging
import traceback
from os import path

_logger = logging.getLogger(__name__)


_log_state_indent = 0


def _increase_indent():
    global _log_state_indent
    _log_state_indent += 1


def _decrease_indent():
    global _log_state_indent
    _log_state_indent = max(_log_state_indent - 1, 0)


def _indent_string():
    return '   ' * _log_state_indent


def log_item(message):
    _logger.info('%s⚫ %s' % (_indent_string(), message))


def log_info(message):
    _logger.info('%s- %s' % (_indent_string(), message))


def log_ok(message):
    _logger.info('%s✓ %s' % (_indent_string(), message))


def log_fail(message):
    _logger.error('%s✗ %s' % (_indent_string(), message))


def log_warn(message):
    _logger.warning('%s⚠ %s' % (_indent_string(), message))


def log_trace(exception):
    trace = traceback.TracebackException.from_exception(exception)

    for frame in trace.stack:
        _logger.error('%s↪ %s l.%s | %s' % (_indent_string(),
                                            path.basename(frame.filename),
                                            frame.lineno,
                                            frame.line))

    _logger.error('%s↪ %s: %s' % (_indent_string(),
                                  type(exception).__name__,
                                  exception))


class LogSequence:
    def __init__(self, description):
        log_item(description)

    def __enter__(self):
        _increase_indent()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type is None:
            _logger.info('%s☀ succeeded' % _indent_string())
        else:
            _logger.info('%s☇ failed' % _indent_string())
            _increase_indent()
            log_trace(exc_value)
            _decrease_indent()

        _decrease_indent()

        if _log_state_indent == 0:
            _logger.info('')

    def ok(self, message):
        log_ok(message)

    def fail(self, message):
        log_fail(message)

    def warn(self, message):
        log_warn(message)

    def info(self, message):
        log_info(message)
