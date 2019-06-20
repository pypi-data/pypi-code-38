from tornado.web import RequestHandler

from . import IRespondable, ILoggable

class ILogged_RequestHandler(RequestHandler, IRespondable, ILoggable):
    
    def get_body_or_query_argument(self, name, default=None, strip=True):
        pass
    def get_body_or_query_arguments(self, name, strip=True):
        pass
