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

import sys
import inspect
from operator import attrgetter
from functools import wraps, partial
from itertools import cycle
import warnings

from fresco import GET, POST, PUT, Response
from fresco.exceptions import BadRequest

_marker = object()


def onerror(exceptions, handler):
    """\
    Return a decorator that can replace or update the return value of the
    function if an exception is raised
    """

    try:
        if isinstance(exceptions, Exception):
            exceptions = (exceptions,)
    except TypeError:
        pass

    def decorator(func):
        @wraps(func)
        def decorated(*fargs, **fkwargs):
            try:
                return func(*fargs, **fkwargs)
            except exceptions:
                exc_info = sys.exc_info()
                return handler(exc_info, *fargs, **fkwargs)
        return decorated
    return decorator


def json_response(data=_marker,
                  indent=None,
                  separators=(',', ':'),
                  content_type='application/json',
                  **kwargs):
    """
    JSON encode the function's result and return a response object with the
    content-type ``application/json``.

    May also be used as a regular function to directly create a JSON encoded
    response, however it's preferrable to use
    :meth:`~fresco.response.Response.json` for this.

    :param data: The data to json encode.
                 If left unspecified, ``json_response``
                 will act as a function decorator.
    :param indent: The indent level. Defaults to ``None`` (no pretty printing)
    :param separators: Defaults to ``(',', ':')`` for the most compact JSON
                       representation
    :param kwargs: Other keyword arguments are passed to ``json.dumps``. These
                   may be used to change encoding paramters, for example
                   overriding the default ``JSONEncoder`` class.


    """
    # Called as a decorator or decorator factory
    if data is _marker or callable(data):
        def json_response_decorator(func):
            @wraps(func)
            def json_response_decorated(*fa, **fkw):
                return Response.json(
                    func(*fa, **fkw), indent, separators, **kwargs)
            return json_response_decorated

        # Called as a decorator factory (``@json_response()``)
        if data is _marker:
            return json_response_decorator

        # Called as a decorator (ie no parens: ``@json_response``)
        return json_response_decorator(data)

    # Called as a regular function (or via ``Route(...).filter``)
    else:
        if isinstance(data, Response):
            return data

        return Response.json(data,
                            indent=indent,
                            separators=separators,
                            content_type=content_type,
                            **kwargs)


def extract_requestargs(requesttype, **argspec):
    """
    Decorator mapping request querystring/post data to function arguments.

    """
    warnings.warn("extract_requestargs is deprecated. "
                  "Please see fresco.routeargs for alternatives",
                  DeprecationWarning, stacklevel=2)
    request_attr = {
        GET: attrgetter('query'),
        POST: attrgetter('form'),
        PUT: attrgetter('form'),
    }[requesttype]

    strict_checking = argspec.pop('_strict', False)
    exception = argspec.pop('_raise_on_error', BadRequest)

    def decorator(func):
        """
        Decorate function ``func``.
        """

        f_args, f_varargs, f_varkw, f_defaults = inspect.getargspec(func)

        # Produce a mapping {argname: default}
        if f_defaults is None:
            f_defaults = []
        defaults = dict(zip(f_args[-len(f_defaults):], f_defaults))

        def decorated(*args, **kwargs):
            """
            Call ``func`` with arguments extracted from ``request``.
            """

            from fresco.core import context
            request = context.request
            given_arguments = dict(
                zip(f_args[:len(args)], args)
            )
            given_arguments.update(kwargs)
            newargs = given_arguments.copy()

            for name, type_fn in argspec.items():
                try:
                    try:
                        value = given_arguments[name]
                    except KeyError:
                        if isinstance(type_fn, list):
                            value = request_attr(request).getlist(name)
                        else:
                            value = request_attr(request)[name]

                    try:
                        if isinstance(type_fn, list):
                            value = [cast(v)
                                     for cast, v in zip(cycle(type_fn), value)]
                        else:
                            value = type_fn(value)
                    except ValueError as e:
                        if name in defaults and not strict_checking:
                            value = defaults[name]
                        else:
                            raise exception(
                                "Could not convert parameter %r to "
                                " requested type (%s)" % (name, e.args[0])
                            )

                except KeyError:
                    try:
                        value = defaults[name]
                    except KeyError:
                        raise exception(name)
                newargs[name] = value

            return func(**newargs)
        return wraps(func)(decorated)
    return decorator

extract_getargs = partial(extract_requestargs, GET)
extract_postargs = partial(extract_requestargs, POST)
extract_getargs.__doc__ = """\
        Extract function arguments from request parameters. See extract_getargs
        for details.
        """
extract_getargs.__doc__ = """\
    Extract function arguments from request parameters

    Synopsis::

        >>> from flea import Agent
        >>> from fresco import FrescoApp, GET
        >>>
        >>> app = FrescoApp()
        >>> @app.route('/', GET)
        ... @extract_getargs(GET, id=int)
        ... def my_app(id):
        ...     return Response(['Got id %d' % (id,)])
        ...
        >>> print Agent(app).get('/?id=2')
        200 OK\r
        Content-Type: text/html; charset=UTF-8\r
        \r
        Got id 2

    If specified arguments are not present in the request (and no default value
    is given in the function signature), or a ValueError is thrown during type
    conversion an appropriate error will be raised::

        >>> Agent(app.wsgi_app).get('/') #doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        BadStatusError: GET '/' returned HTTP status '400 Bad Request'
        >>> Agent(app.wsgi_app).get('/?id=ratatouille') #doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        BadStatusError: GET '/' returned HTTP status '400 Bad Request'

    You can change the error raised, for example if you want a 404 page to be
    returned::

        >>> from fresco.exceptions import NotFound
        >>>
        >>> app = FrescoApp()
        >>> @app.route('/', GET)
        ... @extract_getargs(actions=[unicode])
        ... def my_app(id):
        ...     return Response(['Got id %d' % (id,)])
        ...
        >>> Agent(app).get('/')
        Traceback (most recent call last):
            ...
        BadStatusError: GET '/' returned HTTP status '404 Not Found'

    A default argument value in the handler function will protect against
    this::

        >>> app = FrescoApp()
        >>> @app.route('/', GET)
        ... @extract_getargs(actions=[unicode])
        ... def my_app(id=1):
        ...     return Response(['Got id %d' % (id,)])
        ...
        >>> print Agent(app).get('/')
        200 OK\r
        Content-Type: text/html; charset=UTF-8\r
        \r
        Got id 1

    Sometimes it is necessary to map multiple request values to a single
    argument, for example in a form where two or more input fields have the
    same name. To do this, put the type-casting function into a list when
    calling ``with_request_args``::

        >>> app = FrescoApp()
        >>> @app.route('/', GET)
        ... @extract_getargs(actions=[unicode])
        ... def my_app(actions):
        ...     return Response([
        ...         ', '.join(actions)
        ...     ])
        ...
        >>> print Agent(app).get(
        ...     '/?actions=up;actions=up;actions=and+away%21')
        200 OK\r
        Content-Type: text/html; charset=UTF-8\r
        \r
        up, up, and away!

"""
