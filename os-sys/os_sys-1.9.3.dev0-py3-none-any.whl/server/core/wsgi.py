import server
from server.core.handlers.wsgi import WSGIHandler


def get_wsgi_application():
    """
    The public interface to Server's WSGI support. Return a WSGI callable.

    Avoids making server.core.handlers.WSGIHandler a public API, in case the
    internal WSGI implementation changes or moves in the future.
    """
    server.setup(set_prefix=False)
    return WSGIHandler()
