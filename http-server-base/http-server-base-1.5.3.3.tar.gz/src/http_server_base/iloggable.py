from typing import Type, Union
from types import TracebackType

from http_server_base.tools import ExtendedLogger, logging_method
from tornado.httpclient import HTTPError

class ILoggable():
    logger_name: str
    logger: ExtendedLogger = None
    logger_class: Type[ExtendedLogger] = None

    #region Logging
    @logging_method
    def log_exception(self, error_type, error, trace: TracebackType):
        _at = ""
        if (trace):
            from traceback import extract_tb
            frame = extract_tb(trace)[0]
            _at =f" at {frame.filename}:{frame.lineno}"
        msg = f"{error_type}{_at}: {error}"
        if (isinstance(error, HTTPError)):
            self.logger.error(msg)
        else:
            self.logger.exception(f"Uncaught exception {msg}", exc_info=(error_type, error, trace))
    #endregion
