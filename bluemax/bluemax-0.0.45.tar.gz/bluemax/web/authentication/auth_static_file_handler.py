from tornado.web import authenticated, StaticFileHandler
from .authentication import UserMixin


class AuthStaticFileHandler(UserMixin, StaticFileHandler):
    """
    This provide integration between tornado.web.authenticated
    and tornado.web.StaticFileHandler.

    It assumes you have set up the cookie name in the application
    settings and that the request already has the cookie set. In
    other words the user has already authenticated.
    """

    @authenticated
    def get(self, path, include_body=True):
        return StaticFileHandler.get(self, path, include_body)
