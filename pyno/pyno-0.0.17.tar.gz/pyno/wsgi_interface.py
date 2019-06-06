""" This file defines an object that defines methods to ease integration with Flask"""

def bond(l, name):
    'Utility function used to easily bind a name to a function'
    l.__name__ = name
    return l

class WSGIInterface:
    def __call__(self, environ, start_response, **kwargs): # pragma: no cover
        """ When called a TreeNode object will act like a WSGI application.
        This way they can be passed directly as output to Flask apps, and served using the wsgi
        reference implementation easily """
        if hasattr(self, 'kwargs'):
            self.kwargs.update(kwargs)

        start_response('200 OK', [('Content-type', 'text/HTML charset=utf-8')])
        return [str(self).encode('utf-8')]