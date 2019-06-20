from typing import List, Callable, Tuple

from tornado.web import RequestHandler

from http_server_base import Logged_RequestHandler
from http_server_base.restapi import CanonicalArgumentListType
from http_server_base.tools import RegExpType

class RestMethod:
    name: str
    path: str
    listen_re: RegExpType
    
    query_arguments: CanonicalArgumentListType
    body_arguments: CanonicalArgumentListType
    path_arguments: CanonicalArgumentListType
    header_arguments: CanonicalArgumentListType
    
    action: Callable
    
    def invoke(self, handler:Logged_RequestHandler):
        pass
