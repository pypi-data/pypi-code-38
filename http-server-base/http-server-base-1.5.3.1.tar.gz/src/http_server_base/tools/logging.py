import logging, logging.config
import traceback
from functools import wraps

from io import StringIO
from logging import getLoggerClass, addLevelName, setLoggerClass, NOTSET
import os
import json
from typing import Any, Dict, Tuple, Type, Optional, Union

from tornado.httpclient import HTTPRequest as HTTPClientRequest
from tornado.httputil import HTTPServerRequest
from tornado.web import RequestHandler

def setup_logging \
(
    default_path='configs/logging.json',
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
    """
    Setup logging configuration
    """
    
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

LOGGING_WRAPPER_NAME = '__logging_method_wrapper'
def logging_method(func):
    @wraps(func)
    def __logging_method_wrapper(*args, **kwargs):
        func(*args, **kwargs)

    __logging_method_wrapper.__name__ = LOGGING_WRAPPER_NAME
    return __logging_method_wrapper

TRACE_LEVEL_NUM = 5
DEVELOP_LEVEL_NUM = 60

_logger_class: Type[logging.Logger] = getLoggerClass()
class ExtendedLogger(_logger_class):
    def __init__(self, name, level=NOTSET):
        super().__init__(name, level)
        
        addLevelName(TRACE_LEVEL_NUM, "TRACE")
        addLevelName(DEVELOP_LEVEL_NUM, "DEVELOP")
    
    def findCaller(self, stack_info=False):
        """
        Find the stack frame of the caller so that we can note the source
        file name, line number and function name.
        """
        
        _frame_object = logging.currentframe()
        #On some versions of IronPython, currentframe() returns None if
        #IronPython isn't run with -X:Frames.
        if (_frame_object is not None):
            _frame_object = _frame_object.f_back
        
        rv = ("(unknown file)", 0, "(unknown function)", None)
        while hasattr(_frame_object, 'f_code'):
            _code_object = _frame_object.f_code
            filename = os.path.normcase(_code_object.co_filename)
            
            _next = _frame_object.f_back
            # noinspection PyProtectedMember
            if (filename == logging._srcfile):
                _frame_object = _next
                continue
            
            if (_next and hasattr(_next, 'f_code')):
                _parent_code = _next.f_code
                if (_parent_code.co_name == LOGGING_WRAPPER_NAME):
                    _frame_object = _next.f_back
                    continue
            
            _stack_info = None
            if (stack_info):
                _str_io = StringIO()
                _str_io.write('Stack (most recent call last):\n')
                traceback.print_stack(_frame_object, file=_str_io)
                _stack_info = _str_io.getvalue()
                if (_stack_info[-1] == '\n'):
                    _stack_info = _stack_info[:-1]
                _str_io.close()
            
            rv = (_code_object.co_filename, _frame_object.f_lineno, _code_object.co_name, _stack_info)
            break
        return rv
    
    @logging_method
    def trace(self, message, *args, **kwargs):
        self.log(TRACE_LEVEL_NUM, message, *args, **kwargs)
    
    @logging_method
    def develop(self, message, *args, **kwargs):
        self.log(DEVELOP_LEVEL_NUM, message, *args, **kwargs)

setLoggerClass(ExtendedLogger)

class BraceString(str):
    kwargs: Dict[str, Any] = {}
    def __mod__(self, other):
        return self.format(*other, **self.kwargs)
    def __str__(self):
        return self

class StyleAdapter(logging.LoggerAdapter):
    
    default_style: str
    def __init__(self, logger: logging.Logger, extra=None, *, style='%'):
        super(StyleAdapter, self).__init__(logger, extra)
        self.default_style = style
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        if (kwargs.pop('style', self.default_style) == "{"):
            msg = BraceString(msg)
            msg.kwargs = kwargs
        return msg, kwargs

class RequestLogger(StyleAdapter, ExtendedLogger):
    handler: Optional[RequestHandler]
    def __init__(self, request_handler: Union[RequestHandler, HTTPClientRequest, HTTPServerRequest, None], logger: logging.Logger = None, extra=None):
        self.handler = request_handler
        super().__init__(logger, extra, style='{')
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        prefix = kwargs.pop('prefix', 'req')
        request_id = kwargs.pop('request_id', self.handler and getattr(self.handler, 'request_id', '-'))
        
        msg = f"{prefix}({request_id}): {msg}"
        return super().process(msg, kwargs)
