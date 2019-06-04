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
"""
The :class:`Response` class models the response from your application to a
single request.
"""
from __future__ import absolute_import

from datetime import datetime
from itertools import chain
import re
import json

import fresco
from .cookie import Cookie
from .compat import ustr

__all__ = [
    'STATUS_CONTINUE', 'STATUS_SWITCHING_PROTOCOLS', 'STATUS_PROCESSING',
    'STATUS_OK', 'STATUS_CREATED', 'STATUS_ACCEPTED',
    'STATUS_NON_AUTHORITATIVE_INFORMATION', 'STATUS_NO_CONTENT',
    'STATUS_RESET_CONTENT', 'STATUS_PARTIAL_CONTENT', 'STATUS_MULTI_STATUS',
    'STATUS_ALREADY_REPORTED', 'STATUS_IM_USED', 'STATUS_MULTIPLE_CHOICES',
    'STATUS_MOVED_PERMANENTLY', 'STATUS_FOUND', 'STATUS_SEE_OTHER',
    'STATUS_NOT_MODIFIED', 'STATUS_USE_PROXY', 'STATUS_TEMPORARY_REDIRECT',
    'STATUS_PERMANENT_REDIRECT', 'STATUS_BAD_REQUEST', 'STATUS_UNAUTHORIZED',
    'STATUS_PAYMENT_REQUIRED', 'STATUS_FORBIDDEN', 'STATUS_NOT_FOUND',
    'STATUS_METHOD_NOT_ALLOWED', 'STATUS_NOT_ACCEPTABLE',
    'STATUS_PROXY_AUTHENTICATION_REQUIRED', 'STATUS_REQUEST_TIMEOUT',
    'STATUS_CONFLICT', 'STATUS_GONE', 'STATUS_LENGTH_REQUIRED',
    'STATUS_PRECONDITION_FAILED', 'STATUS_PAYLOAD_TOO_LARGE',
    'STATUS_URI_TOO_LONG', 'STATUS_UNSUPPORTED_MEDIA_TYPE',
    'STATUS_RANGE_NOT_SATISFIABLE', 'STATUS_EXPECTATION_FAILED',
    'STATUS_UNPROCESSABLE_ENTITY', 'STATUS_LOCKED', 'STATUS_FAILED_DEPENDENCY',
    'STATUS_UPGRADE_REQUIRED', 'STATUS_PRECONDITION_REQUIRED',
    'STATUS_TOO_MANY_REQUESTS', 'STATUS_REQUEST_HEADER_FIELDS_TOO_LARGE',
    'STATUS_INTERNAL_SERVER_ERROR', 'STATUS_NOT_IMPLEMENTED',
    'STATUS_BAD_GATEWAY', 'STATUS_SERVICE_UNAVAILABLE',
    'STATUS_GATEWAY_TIMEOUT', 'STATUS_HTTP_VERSION_NOT_SUPPORTED',
    'STATUS_VARIANT_ALSO_NEGOTIATES', 'STATUS_INSUFFICIENT_STORAGE',
    'STATUS_LOOP_DETECTED', 'STATUS_NOT_EXTENDED',
    'STATUS_NETWORK_AUTHENTICATION_REQUIRED',
    'Response'
]


#: HTTP/1.1 status codes as listed in http://www.ietf.org/rfc/rfc2616.txt
HTTP_STATUS_CODES = {100: 'Continue',
                     101: 'Switching Protocols',
                     102: 'Processing',
                     200: 'OK',
                     201: 'Created',
                     202: 'Accepted',
                     203: 'Non-Authoritative Information',
                     204: 'No Content',
                     205: 'Reset Content',
                     206: 'Partial Content',
                     207: 'Multi-Status',
                     208: 'Already Reported',
                     226: 'IM Used',
                     300: 'Multiple Choices',
                     301: 'Moved Permanently',
                     302: 'Found',
                     303: 'See Other',
                     304: 'Not Modified',
                     305: 'Use Proxy',
                     307: 'Temporary Redirect',
                     308: 'Permanent Redirect',
                     400: 'Bad Request',
                     401: 'Unauthorized',
                     402: 'Payment Required',
                     403: 'Forbidden',
                     404: 'Not Found',
                     405: 'Method Not Allowed',
                     406: 'Not Acceptable',
                     407: 'Proxy Authentication Required',
                     408: 'Request Timeout',
                     409: 'Conflict',
                     410: 'Gone',
                     411: 'Length Required',
                     412: 'Precondition Failed',
                     413: 'Payload Too Large',
                     414: 'URI Too Long',
                     415: 'Unsupported Media Type',
                     416: 'Range Not Satisfiable',
                     417: 'Expectation Failed',
                     422: 'Unprocessable Entity',
                     423: 'Locked',
                     424: 'Failed Dependency',
                     426: 'Upgrade Required',
                     428: 'Precondition Required',
                     429: 'Too Many Requests',
                     431: 'Request Header Fields Too Large',
                     500: 'Internal Server Error',
                     501: 'Not Implemented',
                     502: 'Bad Gateway',
                     503: 'Service Unavailable',
                     504: 'Gateway Timeout',
                     505: 'HTTP Version Not Supported',
                     506: 'Variant Also Negotiates',
                     507: 'Insufficient Storage',
                     508: 'Loop Detected',
                     510: 'Not Extended',
                     511: 'Network Authentication Required'}

# Symbolic names for the HTTP status codes
STATUS_CONTINUE = 100
STATUS_SWITCHING_PROTOCOLS = 101
STATUS_PROCESSING = 102
STATUS_OK = 200
STATUS_CREATED = 201
STATUS_ACCEPTED = 202
STATUS_NON_AUTHORITATIVE_INFORMATION = 203
STATUS_NO_CONTENT = 204
STATUS_RESET_CONTENT = 205
STATUS_PARTIAL_CONTENT = 206
STATUS_MULTI_STATUS = 207
STATUS_ALREADY_REPORTED = 208
STATUS_IM_USED = 226
STATUS_MULTIPLE_CHOICES = 300
STATUS_MOVED_PERMANENTLY = 301
STATUS_FOUND = 302
STATUS_SEE_OTHER = 303
STATUS_NOT_MODIFIED = 304
STATUS_USE_PROXY = 305
STATUS_TEMPORARY_REDIRECT = 307
STATUS_PERMANENT_REDIRECT = 308
STATUS_BAD_REQUEST = 400
STATUS_UNAUTHORIZED = 401
STATUS_PAYMENT_REQUIRED = 402
STATUS_FORBIDDEN = 403
STATUS_NOT_FOUND = 404
STATUS_METHOD_NOT_ALLOWED = 405
STATUS_NOT_ACCEPTABLE = 406
STATUS_PROXY_AUTHENTICATION_REQUIRED = 407
STATUS_REQUEST_TIMEOUT = 408
STATUS_CONFLICT = 409
STATUS_GONE = 410
STATUS_LENGTH_REQUIRED = 411
STATUS_PRECONDITION_FAILED = 412
STATUS_PAYLOAD_TOO_LARGE = 413
STATUS_URI_TOO_LONG = 414
STATUS_UNSUPPORTED_MEDIA_TYPE = 415
STATUS_RANGE_NOT_SATISFIABLE = 416
STATUS_EXPECTATION_FAILED = 417
STATUS_UNPROCESSABLE_ENTITY = 422
STATUS_LOCKED = 423
STATUS_FAILED_DEPENDENCY = 424
STATUS_UPGRADE_REQUIRED = 426
STATUS_PRECONDITION_REQUIRED = 428
STATUS_TOO_MANY_REQUESTS = 429
STATUS_REQUEST_HEADER_FIELDS_TOO_LARGE = 431
STATUS_INTERNAL_SERVER_ERROR = 500
STATUS_NOT_IMPLEMENTED = 501
STATUS_BAD_GATEWAY = 502
STATUS_SERVICE_UNAVAILABLE = 503
STATUS_GATEWAY_TIMEOUT = 504
STATUS_HTTP_VERSION_NOT_SUPPORTED = 505
STATUS_VARIANT_ALSO_NEGOTIATES = 506
STATUS_INSUFFICIENT_STORAGE = 507
STATUS_LOOP_DETECTED = 508
STATUS_NOT_EXTENDED = 510
STATUS_NETWORK_AUTHENTICATION_REQUIRED = 511

#: Mapping from python symbolic names to HTTP headers to ensure headers are
#: emitted with correct capitalization
HEADER_NAMES = {
    'accept_ranges': 'Accept-Ranges',
    'age': 'Age',
    'allow': 'Allow',
    'cache_control': 'Cache-Control',
    'connection': 'Connection',
    'content_encoding': 'Content-Encoding',
    'content_language': 'Content-Language',
    'content_length': 'Content-Length',
    'content_location': 'Content-Location',
    'content_md5': 'Content-MD5',
    'content_disposition': 'Content-Disposition',
    'content_range': 'Content-Range',
    'content_type': 'Content-Type',
    'date': 'Date',
    'etag': 'ETag',
    'expires': 'Expires',
    'last_modified': 'Last-Modified',
    'link': 'Link',
    'location': 'Location',
    'p3p': 'P3P',
    'pragma': 'Pragma',
    'proxy_authenticate': 'Proxy-Authenticate',
    'refresh': 'Refresh',
    'retry_after': 'Retry-After',
    'server': 'Server',
    'set_cookie': 'Set-Cookie',
    'strict_transport_security': 'Strict-Transport-Security',
    'trailer': 'Trailer',
    'transfer_encoding': 'Transfer-Encoding',
    'vary': 'Vary',
    'via': 'Via',
    'warning': 'Warning',
    'www_authenticate': 'WWW-Authenticate',
    'x_frame_options': 'X-Frame-Options',
    'x_content_type_options': 'X-Content-Type-Options',
    'x_forwarded_proto': 'X-Forwarded-Proto',
    'front_end_https': 'Front-End-Https',
    'x_powered_by': 'X-Powered-By',
    'x_ua_compatible': 'X-UA-Compatible',
}

default_charset = 'UTF-8'


def encoder(stream, charset):
    r"""\
    Encode a response iterator using the given character set.
    """
    if charset is None:
        charset = default_charset

    for chunk in stream:
        if not isinstance(chunk, bytes):
            yield chunk.encode(charset)
        else:
            yield chunk


def make_header_name(name):
    """\
    Return a formatted header name from a python idenfier.

    Example usage::

        >>> make_header_name('content_type')
        'Content-Type'
    """
    try:
        return HEADER_NAMES[name]
    except KeyError:
        return name.replace('_', '-').title()


def make_headers(header_list, header_dict,
                 make_header_name=make_header_name, chain=chain):
    """
    Return a list of header (name, value) tuples from the combination of
    the header_list and header_dict.

    Synopsis::

        >>> make_headers(
        ...     [('Content-Type', 'text/html')],
        ...     {'content_length' : 54}
        ... )
        [('Content-Type', 'text/html'), ('Content-Length', '54')]

        >>> make_headers(
        ...     [('Content-Type', 'text/html')],
        ...     {'x_foo' : ['a1', 'b2']}
        ... )
        [('Content-Type', 'text/html'), ('X-Foo', 'a1'), ('X-Foo', 'b2')]

    """
    hs = []
    addheader = hs.append
    for h, val in chain(header_list, header_dict.items()):
        if val is None:
            continue
        h = make_header_name(h)
        if isinstance(val, list):
            for item in val:
                addheader((h, str(item)))
        else:
            addheader((h, str(val)))
    return hs


class Response(object):
    """\
    Model an HTTP response
    """

    default_content_type = "text/html; charset=UTF-8"

    def __init__(self, content=None, status=None, headers=None,
                 onclose=None,
                 _nocontent=[],
                 passthrough=False,
                 content_iterator=None,
                 make_headers=make_headers,
                 **kwargs):
        """
        Create a new Response object, modelling the HTTP status, headers and
        content of an HTTP response. Response instances are valid WSGI
        applications.

        :param content: The response content as an iterable object
        :param status: The HTTP status line, eg ``200 OK`` or ``404 Not Found``
        :param headers: A list of HTTP headers
        :param passthrough: If True, use the content iterator unmodified.
                            Default behaviour is to wrap the content iterator
                            with :func:`encoder` to encode unicode strings
                            before output.
        :param kwargs: Arbitrary headers, provided as keyword arguments.
                       Underscores will be replaced with hyphens (eg
                       ``content_length`` becomes ``Content-Length``).

        Example usage::

            >>> # Construct a response
            >>> r = Response(
            ...     content=['hello world'],
            ...     status='200 OK',
            ...     headers=[('Content-Type', 'text/plain')]
            ... )
            >>>

        Changing headers or content::

            >>> r = r.add_header('X-Header', 'hello!')
            >>> r = r.replace(content=['whoa nelly!'],
            ...               content_type='text/html')

        """
        if content is None:
            content = _nocontent
            if status is None:
                status = '204 No Content'

        if status is None:
            self.status = '200 OK'
        else:
            try:
                self.status = '%d %s' % (status, HTTP_STATUS_CODES[status])
            except KeyError:
                self.status = str(status)

        if onclose is None:
            self.onclose = []
        elif callable(onclose):
            self.onclose = [onclose]
        else:
            self.onclose = list(onclose)

        if headers is None:
            headers = []
        if headers or kwargs:
            headers = make_headers(headers, kwargs)

        # Ensure a content-type header is set if a content iterator has been
        # provided
        if content is not _nocontent:
            if not any(k == 'Content-Type' for k, v in headers):
                headers = ([('Content-Type', self.default_content_type)] +
                           headers)

        self.headers = headers

        # Now we've dealt with the headers (including Content-Type,
        # which the charset property will look for when deciding how to
        # encode strings) we can pull the content into an iterable.
        # We optimize for the common cases (byte string, unicode string,
        # list of byte strings, list of unicode strings), otherwise
        # we wrap the iterator in :func:`encoder`, which iterates the content
        # and tries to encode each item as a byte string. Note that this
        # code assumes that lists are homogeneous.
        self.content = content
        if content_iterator:
            self.content = content
            self.content_iterator = content_iterator
        elif passthrough or content is _nocontent:
            self.content_iterator = content
        else:
            content_islist = isinstance(content, list)
            if content_islist:
                if len(content) == 0:
                    self.content_iterator = content
                elif isinstance(content[0], bytes):
                    self.content_iterator = content
                elif isinstance(content[0], ustr):
                    charset = self.charset
                    self.content_iterator = (c.encode(charset)
                                             for c in content)

            elif isinstance(content, bytes):
                self.content_iterator = [content]
            elif isinstance(content, ustr):
                self.content_iterator = [content.encode(self.charset)]
            else:
                self.content_iterator = _copy_close(
                    content, encoder(content, self.charset))

    def __call__(self, environ, start_response, exc_info=None):
        """
        WSGI callable. Calls ``start_response`` with assigned headers and
        returns an iterator over ``content``.
        """
        start_response(self.status, self.headers, exc_info)
        result = self.content_iterator
        if self.onclose:
            result = ClosingIterator(result, *self.onclose)
        return result

    def add_onclose(self, *funcs):
        """
        Add functions to be called as part of the response iterator's ``close``
        method.
        """
        return self.__class__(self.content,
                              self.status,
                              self.headers,
                              self.onclose + list(funcs))

    @classmethod
    def from_wsgi(cls, wsgi_callable, environ, start_response):
        """
        Return a ``Response`` object constructed from the result of calling
        ``wsgi_callable`` with the given ``environ`` and ``start_response``
        arguments.
        """
        responder = StartResponseWrapper(start_response)
        content = wsgi_callable(environ, responder)
        if responder.buf.tell():
            content = _copy_close(content,
                                  chain(content, [responder.buf.getvalue()]))

        if not responder.called:
            # Iterator has not called start_response yet. Call next(content)
            # to force the application to call start_response
            try:
                chunk = next(content)
            except StopIteration:
                pass
            except Exception:
                close = getattr(content, 'close', None)
                if close is not None:
                    close()
                raise
            else:
                content = _copy_close(content, chain([chunk], content))
        return cls(content, responder.status, headers=responder.headers,
                   passthrough=True)

    def get_headers(self, name):
        """\
        Return the list of headers set with the given name.

        Synopsis::

            >>> r = Response(set_cookie = ['cookie1', 'cookie2'])
            >>> r.get_headers('set-cookie')
            ['cookie1', 'cookie2']

        """
        return [value for header, value in self.headers
                      if header.lower() == name.lower()]

    def get_header(self, name, default=''):
        """\
        Return the concatenated values of the named header(s) or ``default`` if
        the header has not been set.

        As specified in RFC2616 (section 4.2), multiple headers will be
        combined using a single comma.

        Example usage::

            >>> r = Response(set_cookie = ['cookie1', 'cookie2'])
            >>> r.get_header('set-cookie')
            'cookie1,cookie2'
        """
        headers = self.get_headers(name)
        if not headers:
            return default
        return ','.join(headers)

    @property
    def status_code(self):
        """
        Return the numeric status code for the response as an integer::

            >>> Response(status='404 Not Found').status_code
            404
            >>> Response(status=200).status_code
            200
        """
        return int(self.status.split(' ', 1)[0])

    @property
    def content_type(self):
        """\
        Return the value of the ``Content-Type`` header if set, otherwise
        ``None``.
        """
        for key, val in self.headers:
            if key.lower() == 'content-type':
                return val
        return None

    def add_header(self, name, value, make_header_name=make_header_name):
        """\
        Return a new response object with the given additional header.

        Synopsis::

            >>> r = Response(content_type='text/plain')
            >>> r.headers
            [('Content-Type', 'text/plain')]
            >>> r.add_header('Cache-Control', 'no-cache').headers
            [('Content-Type', 'text/plain'), ('Cache-Control', 'no-cache')]
        """
        return self.replace(headers=(self.headers +
                                     [(make_header_name(name), value)]))

    def add_headers(self, headers=[], **kwheaders):
        """\
        Return a new response object with the given additional headers.

        Synopsis::

            >>> r = Response(content_type='text/plain')
            >>> r.headers
            [('Content-Type', 'text/plain')]
            >>> r.add_headers(
            ...     cache_control='no-cache',
            ... ).headers
            [('Content-Type', 'text/plain'), ('Cache-Control', 'no-cache')]
        """
        return self.replace(headers=make_headers(self.headers + headers,
                                                 kwheaders))

    def remove_headers(self, *headers):
        """\
        Return a new response object with the named headers removed.

        Synopsis::

            >>> r = Response(content_type='text/plain',
            ...              cache_control='no-cache')
            >>> r.headers
            [('Cache-Control', 'no-cache'), ('Content-Type', 'text/plain')]
            >>> r.remove_headers('Cache-Control').headers
            [('Content-Type', 'text/plain')]
        """
        toremove = [item.lower() for item in headers]
        return self.replace(headers=[h for h in self.headers
                                       if h[0].lower() not in toremove])

    def add_cookie(self, name, value, max_age=None, expires=None, path='/',
                   secure=None, domain=None, comment=None, httponly=False):
        """\
        Return a new response object with the given cookie added.

        Synopsis::

            >>> r = Response(content_type='text/plain')
            >>> r.headers
            [('Content-Type', 'text/plain')]
            >>> r.add_cookie('a', '1').headers
            [('Content-Type', 'text/plain'), ('Set-Cookie', 'a=1;Version=1')]
        """
        return self.add_header('Set-Cookie', Cookie(name, value, max_age,
                                                    expires, path, secure,
                                                    domain,
                                                    comment=comment,
                                                    httponly=httponly))

    def delete_cookie(self, name, path='/', domain=None):
        return self.add_cookie(name, '', max_age=0, path=path, domain=domain,
                               expires=datetime(1970, 1, 1))

    def add_vary(self, *vary_on):
        """
        Return a new response object with the given Vary header.
        Values specified will be added to any existing vary header.

        Synopsis::

            >>> r = Response().add_vary('Accept-Encoding')
            >>> r.headers
            [('Vary', 'Accept-Encoding')]
        """
        vary_on = set(vary_on)
        newheaders = []
        for k, v in self.headers:
            if k.lower() == 'vary':
                vary_on.update(s.strip() for s in v.split(','))
            else:
                newheaders.append((k, v))
        return self.replace(
            headers=newheaders + [('Vary', ', '.join(vary_on))])

    def replace(self, content=None, status=None, headers=None, **kwheaders):
        """\
        Return a new response object with any of content, status or headers
        changed.

        Synopsis::

            >>> r = Response(content_type='text/html')
            >>> r = r.replace(content='foo',
            ...               status=404,
            ...               headers=[('Content-Type', 'text/plain')],
            ...               content_length=3)

        """
        if content is None:
            content = self.content
            content_iterator = self.content_iterator
            onclose = self.onclose
        else:
            content_iterator = None
            close = getattr(self.content, 'close', None)
            onclose = self.onclose
            if close:
                onclose = [close] + onclose

        if headers is None:
            headers = self.headers

        if status is None:
            status = self.status

        if kwheaders:
            toremove = set(make_header_name(k) for k in kwheaders)
            headers = ([(k, v) for k, v in headers if k not in toremove] +
                       make_headers([], kwheaders))

        return self.__class__(content,
                              status,
                              headers,
                              onclose=onclose,
                              content_iterator=content_iterator)

    def buffered(self):
        """\
        Return a new response object with the content buffered into a list.
        This will also generate a content-length header.

        Example usage::

            >>> def generate_content():
            ...     yield "one two "
            ...     yield "three four five"
            ...
            >>> r = Response(content=generate_content())
            >>> r.content  # doctest: +ELLIPSIS
            <generator object ...>
            >>> r = Response(content=generate_content()).buffered()
            >>> r.content
            ['one two ', 'three four five']
        """
        content = list(self.content_iterator)
        content_length = sum(map(len, content))
        return self.replace(content=content, content_length=content_length)

    @property
    def charset(
        self,
        _parser=re.compile(r';\s*charset=([\w\d\-]+)', re.I).search
    ):
        for key, val in self.headers:
            if key == 'Content-Type':
                mo = _parser(val)
                if mo:
                    return mo.group(1)
                break
        return default_charset

    @classmethod
    def not_found(cls, request=None):
        """\
        Return an HTTP not found response (404).

        Synopsis::

            >>> def view():
            ...     return Response.not_found()
            ...
        """
        return cls(
            status=STATUS_NOT_FOUND,
            content=[
                "<html>\n"
                "<body>\n"
                "    <h1>Not found</h1>\n"
                "    <p>The requested resource could not be found.</p>\n"
                "</body>\n"
                "</html>"
            ]
        )

    @classmethod
    def forbidden(cls, message='Sorry, access is denied'):
        """\
        Return an HTTP forbidden response (403).

        Synopsis::

            >>> def view():
            ...     return Response.forbidden()
            ...
        """
        return cls(
            "<html>\n"
            "<body>\n"
            "<h1>%s</h1>\n"
            "</body>\n"
            "</html>" % (message,),
            status=STATUS_FORBIDDEN,
        )

    @classmethod
    def bad_request(cls, request=None):
        """\
        Return an HTTP bad request response.

        Synopsis::

            >>> def view():
            ...     return Response.bad_request()
            ...

        """
        return cls(
            status=STATUS_BAD_REQUEST,
            content=[
                "<html>"
                "<body>"
                "<h1>The server could not understand your request</h1>"
                "</body>"
                "</html>"
            ]
        )

    @classmethod
    def length_required(cls, request=None):
        """\
        Return an HTTP Length Required response (411).

        Synopsis::

            >>> def view():
            ...     return Response.length_required()
            ...

        """
        return cls(
            status=STATUS_LENGTH_REQUIRED,
            content=[
                "<html>"
                "<body>"
                "<h1>A Content-Length header is required</h1>"
                "</body>"
                "</html>"
            ]
        )

    @classmethod
    def payload_too_large(cls, request=None):
        """\
        Return an HTTP Payload Too Large response (413)::

            >>> response = Response.payload_too_large()

        """
        return cls(
            status=STATUS_PAYLOAD_TOO_LARGE,
            content=["<html>"
                     "<body>"
                     "<h1>Payload Too Large</h1>"
                     "</body>"
                     "</html>"])

    request_entity_too_large = payload_too_large

    @classmethod
    def method_not_allowed(cls, valid_methods):
        """\
        Return an HTTP method not allowed response (405)::

            >>> from fresco import context
            >>> def view():
            ...     if context.request.method == 'POST':
            ...         return Response.method_not_allowed(('POST', ))
            ...

        :param valid_methods: A list of HTTP methods valid for requested URL

        :return: A :class:`fresco.response.Response` instance
        """

        return cls(
            status=STATUS_METHOD_NOT_ALLOWED,
            allow=",".join(valid_methods),
            content=["<html>"
                     "<body>"
                     "<h1>Method not allowed</h1>"
                     "</body>"
                     "</html>"
                     ])

    @classmethod
    def internal_server_error(cls):
        """\
        Return an HTTP internal server error response (500).

        Synopsis::

            >>> def view():
            ...     return Response.internal_server_error()
            ...

        :return: A :class:`fresco.response.Response` instance
        """

        return cls(
            status=STATUS_INTERNAL_SERVER_ERROR,
            content=["<html>"
                     "<body>"
                     "<h1>Internal Server Error</h1>"
                     "</body>"
                     "</html>"])

    @classmethod
    def redirect(cls, location, request=None, status=STATUS_FOUND, **kwargs):
        """\
        Return an HTTP redirect reponse (302 or 301).

        :param location: The redirect location or a view specification.
        :param status: HTTP status code for the redirect, default is
                       ``STATUS_FOUND`` (temporary redirect)

        Synopsis:

            >>> def view():
            ...   return Response.redirect("/new-location")
            ...

        The location parameter is interpreted as follows:

        - If it is a callable it is assumed to be a view,
          and passed to :func:`fresco.core.urlfor` to resolve it to a URL.

        - If it is a string and contains '://' it is assumed to be an absolute
          URL and no further processing is done.

        - If it is a string and contains a slash,
          it is assumed to be a
          relative URL and resolved relative to the current request.

        - If it is any other string
          it is passed to :func:`fresco.core.urlfor` to resolve it to a URL.
          If this fails (ie raises RouteNotFound) it is assumed to be a
          relative URL and resolved relative to the current request.
        """
        if callable(location):
            location = fresco.context.app.urlfor(location, **kwargs)

        elif '://' in location:
            pass

        elif '/' in location:
            if request is None:
                request = fresco.context.request
            location = request.resolve_url(location)

        else:
            from fresco.routing import RouteNotFound
            try:
                location = fresco.context.app.urlfor(location, **kwargs)
            except RouteNotFound:
                if kwargs:
                    # kwargs only makes sense if this is a view spec
                    raise
                if request is None:
                    request = fresco.context.request
                location = request.resolve_url(location)

        return Response(
            "<html><head></head><body>\n"
            "<h1>Page has moved</h1>\n"
            "<p><a href='%s'>%s</a></p>\n"
            "</body></html>" % (location, location),
            status=status,
            location=location)

    @classmethod
    def redirect_permanent(cls, *args, **kwargs):
        """\
        Return an HTTP permanent redirect reponse.

        :param location: the URI of the new location. If relative this will be
                         converted to an absolute URL based on the current
                         request.

        """
        return cls.redirect(status=STATUS_MOVED_PERMANENTLY, *args, **kwargs)

    @classmethod
    def redirect_temporary(cls, *args, **kwargs):
        """\
        Return an HTTP permanent redirect reponse.

        :param location: the URI of the new location. If relative this will be
                         converted to an absolute URL based on the current
                         request.

        """
        return cls.redirect(status=STATUS_FOUND, *args, **kwargs)

    @classmethod
    def meta_refresh(cls, location, delay=1, request=None):
        """\
        Return an HTML page containing a <meta http-equiv="refresh"> tag,
        causing the browser to redirect to the given location after ``delay``
        seconds.

        :param location: the URI of the new location. If relative this will be
                         converted to an absolute URL based on the current
                         request.

        """
        if '://' not in location:
            if request is None:
                request = fresco.context.request
            location = request.resolve_url(location)
        return cls([(
            '<!DOCTYPE html>'
            '<html>'
            '<head><meta http-equiv="refresh" content="0; url={0}"></head>'
            '<body><p><a href="{0}">Click here to continue</a></p></body>'
            '</html>').format(location)
        ], content_type='text/html')

    @classmethod
    def json(cls,
             data,
             indent=None,
             separators=(',', ':'),
             content_type='application/json',
             status=None,
             headers=None,
             dumps=json.dumps,
             **kwargs):
        """
        Return an ``application/json`` response with the given data
        JSON serialized

        :param data: The data to json encode.
        :param indent: The indent level.
                       Defaults to ``None`` (no pretty printing)
        :param separators: Defaults to ``(',', ':')`` for the most compact JSON
                           representation
        :param kwargs: Other keyword arguments are passed to ``json.dumps``.
                       These may be used to change encoding paramters, for
                       example overriding the default ``JSONEncoder`` class.

        """
        return cls([dumps(data,
                          indent=indent,
                          separators=separators,
                          **kwargs)],
                   status=status,
                   headers=headers,
                   content_type=content_type,)


def dump_response(r, line_break=b'\r\n', encoding='UTF-8'):
    """\
    Return a byte-string representation of the given response, as for a HTTP
    response.
    """
    output = []
    output.append(r.status.encode('ascii'))
    output.append(line_break)
    for k, v in sorted(r.headers):
        output.append(k.encode('ascii'))
        output.append(b': ')
        output.append(v.encode('ascii'))
        output.append(line_break)
    output.append(line_break)
    output.extend(r.content_iterator)
    s = b''.join(output)
    if encoding:
        return s.decode(encoding)
    return s


def _copy_close(src, dst, marker=object()):
    """\
    Copy the ``close`` attribute from ``src`` to ``dst``, which are assumed to
    be iterators.

    If it is not possible to copy the attribute over (eg for
    ``itertools.chain``, which does not support the close attribute) an
    instance of ``ClosingIterator`` is returned which will proxy calls to
    ``close`` as necessary.
    """

    close = getattr(src, 'close', marker)
    if close is not marker:
        try:
            setattr(dst, 'close', close)
        except AttributeError:
            return ClosingIterator(dst, close)

    return dst

from .util.wsgi import StartResponseWrapper, ClosingIterator
