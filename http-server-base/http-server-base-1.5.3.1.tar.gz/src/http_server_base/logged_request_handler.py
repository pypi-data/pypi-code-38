import json
import random
import string
import warnings
from io import BytesIO
from json import JSONDecodeError
from typing import Union, Callable, Optional, Tuple, Any, Dict, Collection, List, Type
from types import TracebackType
from urllib.parse import urlparse

from tornado.httpclient import HTTPRequest as HTTPClientRequest, HTTPResponse, AsyncHTTPClient
from tornado.httputil import HTTPServerRequest, HTTPHeaders
from tornado.web import RequestHandler, HTTPError
from logging import getLogger, Logger

from . import ILogged_RequestHandler, IResponder
from . import BasicResponder, SubrequestClient
from http_server_base.tools import ExtendedLogger, RequestLogger
from http_server_base.tools import ConfigLoader
from http_server_base.tools import server_request_to_client_request
from http_server_base.tools import ServerError

# noinspection PyAttributeOutsideInit
class Logged_RequestHandler(ILogged_RequestHandler, SubrequestClient):
    """
    Logged_RequestHandler class
    This is a template to the handler classes.
    """
    
    # Could override
    responder_class: Type[IResponder]
    request_id_possible_query_names: List[str] = [ 'requuid', 'requ_id', 'request-id', 'requestId', 'request_id' ]
    request_id_possible_header_names: List[str] = [ SubrequestClient.request_id_header_name, 'RequestId' ]
    
    _ARG_DEFAULT = object()
    def get_body_or_query_argument(self, name, default=_ARG_DEFAULT, strip=True):
        all_args = self.request.body_arguments.copy()
        all_args.update(self.request.query_arguments)
        # noinspection PyTypeChecker
        return self._get_argument(name=name, default=default, source=all_args, strip=strip)
    
    def get_body_or_query_arguments(self, name, strip=True):
        all_args = self.request.body_arguments.copy()
        all_args.update(self.request.query_arguments)
        return self._get_arguments(name=name, source=all_args, strip=strip)
    
    # noinspection SpellCheckingInspection
    @property
    def requ_id(self) -> str:
        warnings.warn("The 'requ_id' field is going to be deprecated, use 'request_id' instead.", DeprecationWarning, 2)
        return self.request_id
    
    # noinspection SpellCheckingInspection
    # noinspection PyDeprecation
    @requ_id.setter
    def requ_id(self, value):
        warnings.warn("The 'requ_id' field is going to be deprecated, use 'request_id' instead.", DeprecationWarning, 2)
        self.request_id = value
    
    #region Initialization
    def initialize(self, **kwargs):
        """
        Initializes the Logged_RequestHandler
        
        Initializes the logging.
        Logs the incoming request to the DEBUG level.
        Sets an request id.
        """
        if (getattr(self, 'logger_name', None) is None):
            self.logger_name = type(self).__name__
        
        # noinspection PyArgumentList
        super().initialize(**kwargs)
        
        _logger:ExtendedLogger = getLogger(self.logger_name)
        self.logger:ExtendedLogger = RequestLogger(self, _logger)
        
        request_obj = self.request
        self.request_id = self.generate_request_id(search_in_query=True, search_in_headers=True)
    
    def prepare(self):
        super().prepare()
        self.dump_request(self.request, request_name="Incoming", prefix='req', dump_body=ConfigLoader.get_from_config('HTTP/dumpRequestBody', default=False))
    #endregion
    #region Responders
    def set_default_headers(self):
        del self._headers["Content-Type"]
    
    def get_error_response(self, *args, **kwargs) -> HTTPResponse:
        if (hasattr(self, 'responder_class')):
            responder = self.responder_class
        elif (hasattr(self.application, 'responder_class')):
            responder = self.application.responder_class
        else:
            raise AttributeError("Must have responder generate response!")
        
        return responder.get_error_response(self, *args, **kwargs)
    
    def resp_error(self, code=500, reason=None, message=None, *args, **kwargs):
        if (hasattr(self, 'responder_class')):
            responder = self.responder_class
        elif (hasattr(self.application, 'responder_class')):
            responder = self.application.responder_class
        else:
            self.send_error(code, reason=reason)
            return
        
        responder.resp_error(self, code=code, reason=reason, message=message, *args, **kwargs)
    
    def resp(self, code=200, reason=None, message=None, *args, **kwargs):
        BasicResponder.resp_success(handler=self, code=code, reason=reason, message=message, *args, **kwargs)
    
    def get_success_response(self, *args, **kwargs) -> HTTPResponse:
        if (hasattr(self, 'responder_class')):
            responder = self.responder_class
        elif (hasattr(self.application, 'responder_class')):
            responder = self.application.responder_class
        else:
            raise AttributeError("Must have responder generate response!")
        
        return responder.get_success_response(self, *args, **kwargs)
    
    def resp_success(self, code=200, reason=None, message=None, result=None, *args, **kwargs):
        if (hasattr(self, 'responder_class')):
            responder = self.responder_class
        elif (hasattr(self.application, 'responder_class')):
            responder = self.application.responder_class
        else:
            self.set_status(code, reason=reason)
            return
        
        responder.resp_success(self, code=code, reason=reason, message=message, result=result, *args, **kwargs)
    #endregion
    #region Proxying
    def generate_proxy_request(self, handler):
        """
        Generate the new instance of the HTTPClientRequest.
        :param handler:
        :return:
        """
        warnings.warn("The 'generate_proxy_request' method has redundant arguments, "
            "use 'generate_proxy_HTTPRequest' instead. It is going to be changed in v1.0", DeprecationWarning, 2)
        handler.generate_proxy_HTTPRequest()
    
    def generate_proxy_HTTPRequest(self, **kwargs) -> HTTPClientRequest:
        request_obj:HTTPServerRequest = self.request
        
        protocol = kwargs.pop('protocol', request_obj.protocol)
        server = kwargs.pop('host', kwargs.pop('server', request_obj.host))
        uri = kwargs.pop('uri', request_obj.uri)
        new_url = kwargs.pop('url', f"{protocol}://{server}{uri}")
        
        _headers = HTTPHeaders(kwargs.pop('headers', request_obj.headers))
        _headers['Connection'] = 'keep-alive'
        _headers.pop('Host', None)
        _method = kwargs.pop('method', request_obj.method).upper()
        _body = kwargs.pop('body', request_obj.body)
        _headers.pop('Transfer-Encoding', None)
        if (_body):
            _headers['Content-Length'] = str(len(_body))
        else:
            _headers.pop('Content-Length', None)
        _allow_nonstandard_methods = kwargs.pop('allow_nonstandard_methods', True)
        
        _proxy_request = HTTPClientRequest(url=new_url, method=_method, body=_body, headers=_headers, allow_nonstandard_methods=_allow_nonstandard_methods, **kwargs)
        return _proxy_request
    
    async def proxy_request_async_2(self, *, generate_request_func: Optional[Callable[[RequestHandler], HTTPClientRequest]] = None, fetch_args: Dict[str, Any] = None, **kwargs):
        """
        Proxies current request.
        """
        
        if (fetch_args is None):
            fetch_args = dict()
        if (not 'raise_error' in fetch_args):
            fetch_args['raise_error'] = False
        if (not 'add_request_id' in fetch_args):
            fetch_args['add_request_id'] = False
        
        if (generate_request_func is None):
            generate_request_func = type(self).generate_proxy_HTTPRequest
        
        _proxy_request = generate_request_func(self, **kwargs)
        
        self.dump_request(_proxy_request, request_name='Proxy Request', prefix='proxy')
        self.logger.debug("Fetching proxy request", prefix='proxy')
        resp = await self.fetch(_proxy_request, **fetch_args)
        self.__proxied(resp)
    
    def proxy_request_async(self, *, generate_request_func: Optional[Callable[['Logged_RequestHandler'], HTTPClientRequest]]=None, **kwargs):
        """
        Proxies current request.
        """
        
        warnings.warn(DeprecationWarning, "'proxy_request_async' method is going to be deprecated as it is not compatible with the Tornado>=6.0")
        
        from tornado import version_info
        if (version_info >= (6, 0)):
            raise DeprecationWarning("'proxy_request_async' is not compatible with Tornado>=6.0")
        
        if (generate_request_func is None):
            generate_request_func = type(self).generate_proxy_HTTPRequest
        
        _client = self.async_http_client
        _proxy_request = generate_request_func(self, **kwargs)
        
        self.dump_request(_proxy_request, request_name='Proxy Request', prefix='proxy')
        self.logger.debug("Fetching proxy request", prefix='proxy')
        _client.fetch(_proxy_request, callback=self.__proxied, raise_error=False)
        return
    
    def __proxied(self, response: HTTPResponse):
        _code = response.code
        self.logger.trace("Proxying response:\nHTTP/1.1 {0} {1}\n{2}\nBody: {3} bytes", response.code, response.reason, response.headers, len(response.body or ''))
        if (_code == 599):
            self.logger.error(f"{type(response.error).__name__}: {response.error}", prefix='resp')
            if (isinstance(response.error, (ConnectionRefusedError, TimeoutError))):
                _new_code = 503
                _host = urlparse(response.request.url).netloc
                _message = f"{response.error.strerror}: {_host}"
            else:
                _new_code = 500
                _message = f"Internal error during proxying the request: {response.error}"
            _reason = None
            self.logger.error(f"{_message}. Changing request code from {_code} to {_new_code}", prefix='resp')
            self.resp_error(_new_code, reason=_reason, message=_message)
            return
        
        self.set_response(response, clear=False)
        self.finish()
        return
    #endregion
    
    def set_response(self, response: HTTPResponse, *, clear: bool = True):
        if (clear):
            self.clear()
        
        self.set_status(response.code)
        for _header_name, _header_value in response.headers.items(): # type: str, str
            if (not (_header_name.lower().startswith(('access-control-', 'transfer-') or _header_name.lower() in ('host', 'date', 'connection')))):
                self.set_header(_header_name, _header_value)
        self.set_header('Content-Length', len(response.body or ''))
        self.set_header('Connection', 'close')
        self.clear_header('Transfer-Encoding')
        if (response.body):
            self.logger.debug(f"Content {response.body[:500]}", prefix='resp')
            self.write(response.body)
        else:
            self.write(b'')
    
    #region Finisher overrides
    # Overriding original finish to exclude 204/304 no body verification
    def finish(self, chunk=None):
        """Finishes this response, ending the HTTP request."""
        if (self._finished):
            raise RuntimeError("finish() called twice")
        
        if (chunk is not None):
            self.write(chunk)
        
        # Automatically support ETags and add the Content-Length header if
        # we have not flushed any content yet.
        if (not self._headers_written):
            if (self._status_code == 200 and
                self.request.method in ("GET", "HEAD") and
                    "Etag" not in self._headers):
                self.set_etag_header()
                if (self.check_etag_header()):
                    self._write_buffer = []
                    self.set_status(304)
            # if (self._status_code in (204, 304)):
            #     assert not self._write_buffer, "Cannot send body with %s" % self._status_code
            #     self._clear_headers_for_304()
            content_length = sum(len(part) for part in self._write_buffer)
            self.set_header("Content-Length", content_length)
        
        if hasattr(self.request, "connection"):
            # Now that the request is finished, clear the callback we
            # set on the HTTPConnection (which would otherwise prevent the
            # garbage collection of the RequestHandler when there
            # are keepalive connections)
            self.request.connection.set_close_callback(None)
        
        self.flush(include_footers=True)
        self.request.connection.finish()
        self._log()
        self._finished = True
        self.on_finish()
        self._break_cycles()
    def write_error(self, *args, exc_info: Tuple = None, **kwargs):
        if (exc_info):
            exception_type, exception, traceback = exc_info
            if (issubclass(exception_type, ServerError)):
                self.resp_error(**exception.resp_error_params)
                return
        
        return super().write_error(*args, exc_info=exc_info, **kwargs)
    #endregion
    
    def generate_request_id(self, *, search_in_query: bool = False, search_in_headers: bool = False) -> str:
        if (search_in_query):
            for _query_param_name in self.request_id_possible_query_names:
                _from_query = self.get_query_argument(_query_param_name, None)
                if (_from_query):
                    return _from_query
        
        if (search_in_headers):
            for _header_param_name in self.request_id_possible_header_names:
                _from_headers = self.request.headers.get(_header_param_name, None)
                if (_from_headers):
                    return _from_headers
        
        return super().generate_request_id()
    
    def _default_error_matcher__create_response(self, error: Exception, **kwargs) -> HTTPResponse:
        response = self.get_error_response(error=f'{type(error).__name__}', **kwargs)
        return response
    def server_request_to_client_request(self, request: HTTPServerRequest = None) -> HTTPClientRequest:
        if (request is None):
            request = self.request
        
        return server_request_to_client_request(request)
