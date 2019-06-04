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

from fresco.response import Response

__all__ = 'ResponseException', 'NotFound', 'Unauthorized',\
          'Forbidden', 'BadRequest', 'Redirect', 'RedirectTemporary',\
          'RedirectPermanent'


class ResponseException(Exception):
    """\
    An exception class with an associated :class:`fresco.response.Response`
    instance that will render a suitable error page.
    """
    response = None

    #: If true, the error response will be returned immediately without trying
    #: any other routes.
    is_final = True

    def __init__(self, content=None, **kwargs):
        self.is_final = kwargs.pop('final', True)
        if content:
            kwargs['content'] = content
        if kwargs:
            self.response = self.response.replace(**kwargs)


class NotFound(ResponseException):
    """\
    Raised when a view needs to signal a 404 not found condition.
    """
    response = Response.not_found()

    def __init__(self, content=None, **kwargs):
        """
        ``final`` is false by default, meaning other routes will be offered the
        opportunity to handle the request. Only after other routes have been
        tried will an error response be returned.
        """
        kwargs.setdefault('final', False)
        super(NotFound, self).__init__(content, **kwargs)


class BadRequest(ResponseException):
    """\
    Return a 400 Bad Request response
    """
    response = Response(['Bad request'], status=400)


class Unauthorized(ResponseException):
    """\
    Return a 401 Unauthorized response.

    Use this when you want to flag that the user does not have permission to
    access a resource but may be able to gain access, eg by logging in.
    """
    response = Response(['Unauthorized'], status=401)


class Forbidden(ResponseException):
    """\
    Return a 403 Forbidden response

    Use this when you want to flag that the user does not have permission to
    access a resource and that there is no possiblity to do so (eg they are
    already logged in, but their account does not have the right access
    permissions)
    """
    response = Response(['Forbidden'], status=403)


class RedirectTemporary(ResponseException):
    """\
    Return a 302 Found response. Example:

        raise RedirectTemporary('http://example.org/')
    """
    def __init__(self, *args, **kwargs):
        self.response = Response.redirect(*args, **kwargs)

Redirect = RedirectTemporary


class RedirectPermanent(ResponseException):
    """\
    Return a 301 Moved Permanently response. Example:

        raise RedirectPermanent('http://example.org/')

    """
    def __init__(self, *args, **kwargs):
        self.response = Response.redirect_permanent(*args, **kwargs)


class RequestParseError(BadRequest):
    """\
    An error was encountered while parsing the HTTP request.
    """


class MethodNotAllowed(ResponseException):
    """\
    The URL is valid, but does not respond to the requested method
    """
    def __init__(self, valid_methods, **kwargs):
        self.response = Response.method_not_allowed(valid_methods)
        super(MethodNotAllowed, self).__init__(**kwargs)


class TooManyRequests(ResponseException):
    """
    Indicates that the user has sent too many
    requests in a given amount of time ("rate limiting").

    The response representations SHOULD include details explaining the
    condition, and MAY include a Retry-After header indicating how long
    to wait before making a new request.
    """
    response = Response(['Too many requests'], status=429)


class MissingRouteArg(BadRequest):
    """\
    A request argument was expected but not supplied.
    """
