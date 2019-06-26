from typing import Type, Union

from tornado.httpclient import HTTPRequest as HTTPClientRequest, HTTPResponse
from tornado.httputil import HTTPServerRequest, HTTPHeaders

from . import ILoggable

from http_server_base.tools import logging_method, ExtendedLogger

class RequestLoggerClient(ILoggable):
    @classmethod
    def _str_or_bytes_to_str(cls, x: Union[str, bytes, None]) -> str:
        if (not x):
            return ''
        elif (isinstance(x, str)):
            return x
        elif (isinstance(x, bytes)):
            return x.decode()
        else:
            raise ValueError(f"Argument must be either str, bytes, or None, not {type(x)}")
    
    @logging_method
    def dump_request(self, request_obj: Union[HTTPServerRequest, HTTPClientRequest], *, request_name: str = '', logger: ExtendedLogger = None, dump_body: bool = False, **kwargs):
        if (logger is None):
            logger = self.logger
        
        _is_server_request = isinstance(request_obj, HTTPServerRequest)
        _url = request_obj.uri if (_is_server_request) else request_obj.url
        logger.info("{0} HTTP request: {1} {2}", request_name, request_obj.method, _url, **kwargs)
        logger.debug("{0} Headers: {1}", request_name, dict(request_obj.headers), **kwargs)
        if (_is_server_request):
            logger.debug("{0} Query args: {1}", request_name, request_obj.query_arguments, **kwargs)
            logger.debug("{0} Body args: {1}", request_name, request_obj.body_arguments, **kwargs)
        else:
            logger.debug("{0} Body: {1}", request_name, request_obj.body, **kwargs)
        
        _body = ''
        if (dump_body):
            try:
                _body = self._str_or_bytes_to_str(request_obj.body)
            except (ValueError, UnicodeDecodeError) as e:
                pass
        
        logger.trace \
        (
            "{0} Dump:\n"
            "{1} {2} HTTP/1.1\n"
            "{3}\n" # This is the double linebreak, because headers do already have the trailing linebreak
            "Body: {4} bytes\n"
            "{5}",
            request_name,
            request_obj.method, _url,
            HTTPHeaders(request_obj.headers),
            len(request_obj.body or ''),
            _body,
            **kwargs,
        )
    @logging_method
    def dump_response(self, response_obj: Union[HTTPResponse], *, request_name: str = '', logger: ExtendedLogger = None, dump_body: bool = False, **kwargs):
        
        request_obj: Union[HTTPClientRequest, HTTPServerRequest] = response_obj.request
        _is_server_request = isinstance(response_obj, HTTPServerRequest)
        _url = request_obj.uri if (_is_server_request) else request_obj.url
        logger.info("{0} HTTP response: {1} {2}", request_name, response_obj.code, response_obj.reason, **kwargs)
        logger.debug("{0} Headers: {1}", request_name, dict(response_obj.headers), **kwargs)
        logger.debug("{0} Body: {1}", request_name, response_obj.body, **kwargs)
        
        _body = ''
        if (dump_body):
            try:
                _body = self._str_or_bytes_to_str(response_obj.body)
            except (ValueError, UnicodeDecodeError) as e:
                pass
        
        logger.trace \
        (
            "{0} Dump:\n"
            "HTTP/1.1 {1} {2}\n"
            "{3}\n" # This is the double linebreak, because headers do already have the trailing linebreak
            "Body: {4} bytes\n"
            "{5}",
            request_name,
            response_obj.code, response_obj.reason,
            HTTPHeaders(response_obj.headers),
            len(response_obj.body or ''),
            _body,
            **kwargs,
        )
