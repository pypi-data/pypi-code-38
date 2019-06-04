# Copyright 2015 Oliver Cope
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#
from __future__ import absolute_import

from collections import defaultdict
from functools import partial
import contextlib
import logging
import sys

from fresco.compat import reraise
from fresco.request import Request
from fresco.response import Response
from fresco.util.http import encode_multipart
from fresco.util.urls import normpath, make_query
from fresco.util.common import fq_path
from fresco.util.wsgi import make_environ

from fresco.exceptions import ResponseException
from fresco.requestcontext import context
from fresco.routing import (GET, ExtensiblePattern, RouteCollection,
                            RouteNotFound, TraversedCollection)
from fresco.options import Options

__all__ = ('FrescoApp', 'urlfor')

logger = logging.getLogger(__name__)


class FrescoApp(RouteCollection):
    """\
    Fresco application class.
    """

    #: The default class to use for URL pattern matching
    pattern_class = ExtensiblePattern

    #: A stdlib logger object, or None
    logger = None

    #: Class to use to instantiate request objects
    request_class = Request

    def __init__(self, *args, **kwargs):

        views = kwargs.pop('views', None)
        path = kwargs.pop('path', None)
        super(FrescoApp, self).__init__(*args, **kwargs)

        if views is not None:
            if path is None:
                path = '/'
            self.include(path, views)

        #: A list of (middleware, args, kwargs) tuples
        self._middleware = []

        #: The WSGI application. This is generated when the first request is
        #: made.
        self._wsgi_app = None

        #: An options dictionary, for arbitrary application variables or
        #: configuration
        self.options = Options()

        #: Functions to be called before the routing has been traversed.
        #: Each function will be passed the request object.
        #: If a function returns a value (other than ``None``)
        #: this will be returned and the normal routing system bypassed.
        self.process_request_handlers = []

        #: Functions to be called after routing, but before any view is invoked
        #: Each function will be passed
        #: ``request, view, view_args, view_kwargs``.
        #: If a function returns a Response instance
        #: this will be returned as the response
        #: instead of calling the scheduled view.
        #: If a function returns any other (non-None) value this will be used
        #: to replace the scheduled view function.
        self.process_view_handlers = []

        #: Functions to be called after a response object has been generated
        #: Each function will be passed ``request, response``.
        #: If a function returns a value (other than ``None``),
        #: this value will be
        #: returned as the response instead of calling the scheduled view.
        self.process_response_handlers = []

        #: Functions to be called if the response has an HTTP error status code
        #: (400 <= x <= 599)
        #: Each function will be passed ``request, response``.
        #: If a function returns a value (other than ``None``),
        #: this value will be
        #: returned as the response instead of calling the scheduled view.
        self.process_http_error_response_handlers = []

        #: Functions to be called if an exception is raised during a view
        #: Each function will be passed ``request, exc_info``.
        #: If a function returns a value (other than ``None``),
        #: this value will be
        #: returned as the response and the error will not be propagated.
        #: If all exception handlers return None then the error will be raised
        self.process_exception_handlers = []

        #: Functions to be called at the end of request processing,
        #: after all content has been output.
        #: Each function will be passed ``request`` and should not
        #: return any value.
        self.process_teardown_handlers = []

    def __call__(self, environ, start_response):
        """\
        Call the app as a WSGI application
        """
        if self._wsgi_app is None:
            self._wsgi_app = self.make_wsgi_app()
            self.__call__ = self._wsgi_app
        return self._wsgi_app(environ, start_response)

    def __str__(self):
        """\
        String representation of the application and its configured routes
        """
        clsname = self.__class__.__name__
        return '<%s %s>' % (
            clsname,
            ('\n' + ' ' * (len(clsname) + 2)).join(str(r)
                                                   for r in self.__routes__))

    def get_response(
            self, routecollection=None, request=None, path=None, method=None,
            currentcontext=context.currentcontext,
            normpath=normpath):

        ctx = currentcontext()
        try:
            routecollection = routecollection or self
            request = request or ctx['request']
            method = method or request.method
            path = path or request.path_info
            error_response = None

            ctx['app'] = self
            environ = request.environ
            environ['fresco.app'] = self

            if path:
                if ('..' in path or '//' in path or '/./' in path):
                    path = normpath(path)
            else:
                path = '/'
        except ResponseException as e:
            return e.response

        response = None
        for f in self.process_request_handlers:
            try:
                r = f(request)
                if r is not None:
                    response = r
            except Exception:
                return self.handle_exception(request,
                                             allow_reraise=False)
        if response:
            return response

        try:
            for traversal in routecollection.get_routes(path, method, request):
                try:
                    route = traversal.route
                    environ['wsgiorg.routing_args'] = (traversal.args,
                                                       traversal.kwargs)
                    view = route.getview(method)
                    ctx['view_self'] = getattr(view, '__self__', None)
                    ctx['route_traversal'] = traversal
                    if self.logger:
                        self.logger.info("matched route: %s %r => %r",
                                         request.method, path, fq_path(view))

                    response = None
                    for f in self.process_view_handlers:
                        try:
                            r = f(request, view, traversal.args,
                                  traversal.kwargs)
                            if r is not None:
                                response = r
                        except Exception:
                            return self.handle_exception(request,
                                                         allow_reraise=False)
                    if response is not None:
                        if isinstance(response, Response):
                            return response
                        else:
                            view = response

                    view = route.getdecoratedview(view)
                    response = view(*traversal.args, **traversal.kwargs)
                    if route.fallthrough_statuses and \
                       response.status_code in route.fallthrough_statuses:
                        continue

                except ResponseException as e:
                    if e.is_final:
                        return e.response
                    error_response = error_response or e.response
                    if route.fallthrough_statuses and \
                       error_response.status_code in route.fallthrough_statuses:
                        continue

                except Exception:
                    return self.handle_exception(request)
                else:
                    return response

        except ResponseException as e:
            if e.is_final:
                return e.response
            error_response = error_response or e.response

        except Exception:
            return self.handle_exception(request)

        # A route was matched, but an error was returned
        if error_response:
            return error_response

        # Is this a head request?
        if method == 'HEAD':
            response = self.get_response(routecollection, request, path, GET)
            if '200' <= response.status < '300':
                return response.replace(content=[], content_length=0)
            return response

        # Is the URL matched by another HTTP method?
        methods = self.get_methods(routecollection, request, path)
        if methods:
            return Response.method_not_allowed(methods)

        # Is the URL just missing a trailing '/'?
        if path[-1] != '/':
            for _ in self.get_methods(routecollection, request, path + '/'):
                return Response.redirect_permanent(path + '/')

        return Response.not_found()

    def view(self, request=None):
        request = request or context.request
        response = self.get_response(request=request)

        for f in self.process_response_handlers:
            try:
                r = f(request, response)
                if r is not None:
                    response = r
            except Exception:
                self.log_exception(request)

        if '400' <= response.status <= '599':
            if self.process_http_error_response_handlers:
                response = self.handle_http_error_response(request, response)

        return response

    def handle_http_error_response(self, request, response):
        """
        Call any process_http_error_response handlers and return the
        (potentially modified) response object.
        """
        for status, f in self.process_http_error_response_handlers:
            try:
                if status is not None and status != response.status_code:
                    continue
                r = f(request, response)
                if r is not None:
                    response = r
            except Exception:
                self.log_exception(request)
        return response

    def get_methods(self, routecollection, request, path):
        """\
        Return the HTTP methods valid in routes to the given path
        """
        methods = set()
        for traversal in routecollection.get_routes(path, None):
            route = traversal.route
            if route.predicate and not route.predicate(request):
                continue
            methods.update(route.methods)
        return methods

    def log_exception(self, request, exc_info=None):
        exc_info = exc_info or sys.exc_info()
        (self.logger or logger).error(
            "Exception in {0} {1}".format(request.method, request.url),
            exc_info=exc_info)

    def handle_exception(self, request, allow_reraise=True):

        exc_info = sys.exc_info()

        have_error_handlers = self.process_exception_handlers or any(
            st in (None, 500)
            for st, fn in self.process_http_error_response_handlers)

        # Backwards compatibility: if no exception or 500 http error
        # handlers have been installed we default to the old behavior
        # of raising the exception and letting the upstream
        # server handle it
        if allow_reraise and not have_error_handlers:
            reraise(exc_info)

        try:
            if not self.process_exception_handlers:
                self.log_exception(request, exc_info)
            response = None
            for exc_type, func in self.process_exception_handlers:
                try:
                    if not issubclass(exc_info[0], exc_type):
                        continue
                    r = func(request, exc_info)
                    if r is not None:
                        response = r
                        break
                except Exception:
                    self.log_exception(request)
            if response is not None:
                if isinstance(response, tuple) and len(response) == 3:
                    reraise(response)
                return response
            else:
                return Response.internal_server_error()
        finally:
            del exc_info

    def add_middleware(self, middleware, *args, **kwargs):
        """\
        Add a WSGI middleware layer

        Note that middleware is applied from the outside in. The first
        middleware added will occupy the innermost layer and be called last in
        each request cycle.
        """
        self.reset_wsgi_app()
        self._middleware.append((middleware, args, kwargs))

    def remove_middleware(self, middleware):
        """
        Remove the given WSGI middleware layer.

        :param middleware: A middleware object. This must be the an object
                           that was previouslly passed to
                           :meth:`add_middleware`.
        """
        self.reset_wsgi_app()
        self._middleware = [m for m in self._middleware
                            if m[0] is not middleware]

    def insert_middleware(self, position, middleware, *args, **kwargs):
        """
        Insert a middleware layer at the given position

        :param position: The index of the element before which to insert.
                         Note that middleware is applied from the outside in,
                         so middleware inserted at position zero will be called
                         last.
        :param middleware: A middleware callable.
        :param args: extra positional args to be passed to the middleware for
                     initialization
        :param kwargs: extra keyword args to be passed to the middleware for
                       initialization
        """
        self.reset_wsgi_app()
        self._middleware.insert(position, (middleware, args, kwargs))

    def make_wsgi_app(self, wsgi_app=None, use_middleware=True):
        """
        Return a WSGI (PEP-3333) compliant application that drives this
        FrescoApp object.

        :param wsgi_app: if given, will be called in place of
                    :meth:~`fresco.core.FrescoApp.view`(request)
                    with :meth:~`fresco.core.FrescoApp.requestcontext`)
        :param use_middleware: if True, the app's middleware stack will be applied
                            to the resulting WSGI app.
        """
        if wsgi_app is None:
            def wsgi_app(environ,
                         start_response,
                         view=self.view,
                         request_class=self.request_class):
                request = request_class(environ)
                return view(request)(environ, start_response)

        if use_middleware:
            for m, m_args, m_kwargs in self._middleware:
                wsgi_app = m(wsgi_app, *m_args, **m_kwargs)

        def fresco_wsgi_app(environ,
                            start_response,
                            frescoapp=self,
                            wsgi_app=wsgi_app,
                            request_class=self.request_class,
                            process_teardown_handlers=self.process_teardown_handlers,
                            call_process_teardown_handlers=self.call_process_teardown_handlers,
                            context_push=context.push,
                            context_pop=context.pop):
            request = request_class(environ)
            context_push(request=request, app=frescoapp)
            iterator = None
            try:
                iterator = wsgi_app(environ, start_response)
                for item in iterator:
                    yield item
            except Exception:
                exc_info = sys.exc_info()
                try:
                    response = frescoapp.handle_exception(request)
                    if '400' <= response.status <= '599':
                        response = frescoapp.handle_http_error_response(
                            request, response)

                    exc_start_response = lambda s, h, exc_info=exc_info: \
                            start_response(s, h, exc_info)
                    for item in response(environ, exc_start_response):
                        yield item
                finally:
                    del exc_info
            finally:
                try:
                    if process_teardown_handlers:
                        call_process_teardown_handlers(request)
                finally:
                    try:
                        close = getattr(iterator, 'close', None)
                        if close is not None:
                            close()
                    finally:
                        context_pop()
        return fresco_wsgi_app

    def reset_wsgi_app(self):
        try:
            del self.__call__
        except AttributeError:
            pass
        self._wsgi_app = None

    def urlfor(self, viewspec, *args, **kwargs):
        """\
        Return the url for the given view name or function spec

        :param viewspec: a view name, a reference in the form
                         ``'package.module.viewfunction'``, or the view
                         callable itself.
        :param _scheme: the URL scheme to use (eg 'https' or 'http').
        :param _netloc: the network location to use (eg 'localhost:8000').
        :param _script_name: the SCRIPT_NAME path component
        :param _query: any query parameters, as a dict or list of
                        ``(key, value)`` tuples.
        :param _fragment: a URL fragment to append.

        All other arguments or keyword args are fed to the ``pathfor`` method
        of the pattern.
        """
        scheme = kwargs.pop('_scheme', None)
        netloc = kwargs.pop('_netloc', None)
        query = kwargs.pop('_query', {})
        script_name = kwargs.pop('_script_name', None)
        fragment = kwargs.pop('_fragment', None)

        ctx = context.currentcontext()
        request = ctx['request']
        traversal = ctx.get('route_traversal')
        if traversal and traversal.collections_traversed:
            collections_traversed = traversal.collections_traversed
        else:
            collections_traversed = [
                TraversedCollection(self, '', None, (), {}, (), {})]

        exc = None
        for ct in collections_traversed[::-1]:
            try:
                path = ct.path + \
                        ct.collection.pathfor(viewspec, request=request,
                                           *args, **kwargs)
            except RouteNotFound as e:
                exc = e
                continue
            return request.make_url(scheme=scheme, netloc=netloc,
                                    SCRIPT_NAME=script_name,
                                    PATH_INFO=path,
                                    parameters='',
                                    query=query, fragment=fragment)
        raise exc or RouteNotFound(viewspec)

    def view_method_not_found(self, valid_methods):
        """
        Return a ``405 Method Not Allowed`` response.

        Called when a view matched the pattern but no HTTP methods matched.
        """
        return Response.method_not_allowed(valid_methods)

    def call_process_teardown_handlers(self, request):
        """
        Called once the request has been completed and the response content
        output.
        """
        for func in self.process_teardown_handlers:
            try:
                func(request)
            except Exception:
                self.log_exception(request)

    def process_request(self, func):
        """
        Register a ``process_request`` hook function
        """
        self.process_request_handlers.append(func)
        return func

    def process_view(self, func):
        """
        Register a ``process_view`` hook function
        """
        self.process_view_handlers.append(func)
        return func

    def process_response(self, func):
        """
        Register a ``process_response`` hook function
        """
        self.process_response_handlers.append(func)
        return func

    def process_exception(self, func, exc_type=Exception):
        """
        Register a ``process_exception`` hook function
        """
        if isinstance(func, type) and issubclass(func, Exception):
            return partial(self.process_exception, exc_type=func)

        self.process_exception_handlers.append((exc_type, func))
        return func

    def process_http_error_response(self, func, status=None):
        """
        Register a ``process_http_error_response`` hook function
        """
        if isinstance(func, int):
            return partial(self.process_http_error_response, status=func)

        self.process_http_error_response_handlers.append((status, func))
        return func

    def process_teardown(self, func):
        """
        Register a ``process_teardown`` hook function
        """
        if self._wsgi_app:
            raise AssertionError("Cannot add hook: "
                                 "application is now receiving requests")
        self.process_teardown_handlers.append(func)

    @contextlib.contextmanager
    def requestcontext(self, url='/', environ=None,
                       wsgi_input=b'', middleware=True, **kwargs):
        """
        Return the global :class:`fresco.requestcontext.RequestContext`
        instance, populated with a new request object modelling default
        WSGI environ values.

        Synopsis::

            >>> app = FrescoApp()
            >>> with app.requestcontext('http://www.example.com/view') as c:
            ...     print c.request.url
            ...
            http://www.example.com/view

        Note that ``url`` must be properly URL encoded.

        :param url: The URL for the request,
                    eg ``/index.html`` or ``/search?q=foo``.
        :param environ: values to pass into the WSGI environ dict
        :param wsgi_input: The input stream to use in the ``wsgi.input``
                           key of the environ dict
        :param middleware: If ``False`` the middleware stack will not be
                           invoked. Disabling the middleware can speed up
                           the execution considerably, but it will no longer
                           give an accurate simulation of a real HTTP request.
        :param kwargs: additional keyword arguments will be passed into the
                       WSGI request environment
        """
        def fake_app(environ, start_response):
            start_response('200 OK', [])
            yield b''

        def fake_start_response(status, headers, exc_info=None):
            return (lambda s: None)

        environ = make_environ(url, environ, wsgi_input, **kwargs)
        app = self.make_wsgi_app(wsgi_app=fake_app, use_middleware=middleware)
        content_iterator = app(environ, fake_start_response)
        next(content_iterator, None)
        yield context
        list(content_iterator)
        getattr(content_iterator, 'close', lambda: None)()

    def requestcontext_with_payload(
            self, url='/', data=None, environ=None, files=None,
            multipart=False, **kwargs):

        if files:
            multipart = True

        if multipart:
            wsgi_input, headers = encode_multipart(data, files)
            kwargs.update(headers)
        elif hasattr(data, 'read'):
            wsgi_input = data.read()
        elif isinstance(data, bytes):
            wsgi_input = data
        else:
            wsgi_input = make_query(data).encode('ascii')

        if 'CONTENT_LENGTH' not in kwargs:
            kwargs['CONTENT_LENGTH'] = str(len(wsgi_input))

        return self.requestcontext(
            url, environ, wsgi_input=wsgi_input, **kwargs)

    def requestcontext_post(self, *args, **kwargs):
        return self.requestcontext_with_payload(
            REQUEST_METHOD='POST', *args, **kwargs)

    def requestcontext_put(self, *args, **kwargs):
        kwargs['REQUEST_METHOD'] = 'PUT'
        return self.requestcontext_with_payload(*args, **kwargs)

    def requestcontext_patch(self, *args, **kwargs):
        kwargs['REQUEST_METHOD'] = 'PATCH'
        return self.requestcontext_with_payload(*args, **kwargs)

    def requestcontext_delete(self, *args, **kwargs):
        kwargs['REQUEST_METHOD'] = 'DELETE'
        return self.requestcontext(*args, **kwargs)


def collect_keys(items):
    """
    [(k1, v1), (k1, v2), (k2, v3)] -> [(k1, [v1, v2]), (k2, [v3])]
    """
    d = defaultdict(list)
    for key, value in items:
        d[key].append(value)
    return d.items()


def urlfor(*args, **kwargs):
    """\
    Convenience wrapper around :meth:`~fresco.core.FrescoApp.urlfor`.
    """
    return context.app.urlfor(*args, **kwargs)
