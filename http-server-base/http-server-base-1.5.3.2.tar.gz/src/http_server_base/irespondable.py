from typing import Type

from tornado.httpclient import HTTPRequest as HTTPClientRequest, HTTPResponse, AsyncHTTPClient
from tornado.httputil import HTTPServerRequest, HTTPHeaders

class IRespondable:
    
    # Should not override
    responder_class: Type
    request_id = None
    request: HTTPServerRequest
    
    def get_error_response(self, code=500, reason=None, message=None, *args, **kwargs) -> HTTPResponse:
        pass
    def resp_error(self, code=500, reason=None, message=None, *args, **kwargs):
        pass
    def resp(self, code=200, reason=None, message=None, *args, **kwargs):
        pass
    def get_success_response(self, code=200, reason=None, message=None, result=None, *args, **kwargs) -> HTTPResponse:
        pass
    def resp_success(self, code=200, reason=None, message=None, result=None, *args, **kwargs):
        pass
    
    def server_request_to_client_request(self, request: HTTPServerRequest = None) -> HTTPClientRequest:
        pass
    def set_response(self, response: HTTPResponse, *, clear: bool = True):
        pass    
