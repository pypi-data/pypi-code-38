import tornado
from typing import Union

from tornado.web import Application
from tornado.httpclient import HTTPRequest, HTTPResponse

from http_server_base.tools import RequestLogger, ExtendedLogger

class HttpSubrequest(HTTPRequest):
    request_id: str
    parent_request_id: str
    logger: RequestLogger
    
    def __init__(self, url: Union[str, HTTPRequest], *args, request_id: str = None, parent_request_id: str = None, base_logger: ExtendedLogger = None, **kwargs):
        if (isinstance(url, HTTPRequest)):
            self.__dict__ = url.__dict__.copy()
        else:
            super().__init__(url, *args, **kwargs)
        
        self.request_id = request_id
        self.parent_request_id = parent_request_id
        if (base_logger is None):
            base_logger: ExtendedLogger = 'http_server.subrequests'
        
        self.logger = RequestLogger(self, base_logger)

class HttpSubrequestResponse(HTTPResponse):
    request: HttpSubrequest
    
    def __init__(self, *args, **kwargs):
        if (args and isinstance(args[0], HTTPResponse)):
            self.__dict__ = args[0].__dict__.copy()
        else:
            super().__init__(*args, **kwargs)
