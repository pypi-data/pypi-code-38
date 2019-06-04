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
fresco.request
--------------

The :class:`Request` class models an incoming HTTP request, allowing access to
HTTP headers and request data (eg query string or submitted form data).
"""
from __future__ import absolute_import

import json
import posixpath
import re

from fresco import exceptions
from fresco.compat import (ustr, quote, urlparse, urlunparse,
                           ParseResult)
from fresco.util.wsgi import environ_to_unicode

import fresco

from .multidict import MultiDict
from .cookie import parse_cookie_header
from .util.urls import normpath, make_query

__all__ = 'Request', 'currentrequest'

KB = 1024
MB = 1024 * KB


class Request(object):
    """
    Models an HTTP request, given a WSGI ``environ`` dictionary.
    """

    #: Maximum size for application/x-www-form-urlencoded post data, or maximum
    #: field size in multipart/form-data encoded data, not including file
    #: uploads
    MAX_SIZE = 16 * KB

    #: Maximum size for multipart/form-data encoded post data
    MAX_MULTIPART_SIZE = 2 * MB

    #: Support broken IE content-disposition escaping
    IE_CONTENT_DISPOSITION_WORKAROUND = True

    _body_bytes = None
    _parsed_content_type = None
    _form = None
    _files = None
    _query = None
    _cookies = None
    _parsed_url = None

    STATE_ENV_KEY = 'fresco._request_state'

    #: WSGI key for the session variable. The default value is configured for
    #: use with `beaker <http://beaker.groovie.org/>`_
    SESSION_ENV_KEY = 'beaker.session'

    #: The WSGI environ dict
    environ = None

    #: Encoding used to decode WSGI parameters, notably PATH_INFO and form data
    default_charset = fresco.DEFAULT_CHARSET

    #: The decoder class to use for JSON request payloads
    json_decoder_class = json.JSONDecoder

    def __init__(self, environ):
        if self.STATE_ENV_KEY in environ:
            self.__dict__ = environ[self.STATE_ENV_KEY]
        else:
            environ[self.STATE_ENV_KEY] = self.__dict__
        self.environ = environ

    def __str__(self):
        """
        Return a useful text representation of the request
        """
        return "<%s %s %s>" % (
                self.__class__.__name__,
                self.method,
                self.url,
        )

    @property
    def charset(self,
                parse_charset=re.compile(r';\s*charset=([\w\d\-]+)').search):
        try:
            return self.environ['fresco.request.charset']
        except KeyError:
            r = self.default_charset
            ct = self.environ.get('CONTENT_TYPE')
            if ct is not None:
                match = parse_charset(ct)
                if match is not None:
                    r = self.environ['fresco.request.charset'] = match.group(1)
        return r

    @charset.setter
    def charset(self, value):
        self.environ['fresco.request.charset'] = value

    @property
    def form(self):
        """
        Return the contents of submitted form data

        This will return the ``POST`` or ``PUT`` data when available, otherwise
        querystring (``GET``)  data. Querystring data is always available via
        the ``query`` property.
        """
        if self._form is None:
            if self.environ['REQUEST_METHOD'] in ('PUT', 'POST'):
                self._form = MultiDict(
                    parse_post(self.environ,
                               self.environ['wsgi.input'],
                               self.charset,
                               self.MAX_SIZE,
                               self.MAX_MULTIPART_SIZE,
                               ie_workaround=self.IE_CONTENT_DISPOSITION_WORKAROUND)
                )
            else:
                data = environ_to_unicode(self.environ.get('QUERY_STRING', ''))
                self._form = MultiDict(parse_querystring(data, self.charset))
        return self._form

    @property
    def content_type_encoding(self):
        if self._parsed_content_type is None:
            self._parsed_content_type = get_content_type_info(self.environ)
        return self._parsed_content_type.encoding

    @property
    def content_type(self):
        if self._parsed_content_type is None:
            self._parsed_content_type = get_content_type_info(self.environ)
        return self._parsed_content_type.content_type

    @property
    def body_bytes(self):
        if self._body_bytes is None:
            self._body_bytes = get_body_bytes(self.environ, self.MAX_SIZE)
        return self._body_bytes

    @property
    def body(self):
        body = self.body_bytes
        if body is None:
            return None
        encoding = self.content_type_encoding or self.charset
        try:
            return body.decode(encoding)
        except UnicodeDecodeError:
            raise exceptions.RequestParseError(
                "Payload contains data that could not be decoded using " +
                encoding)

    def get_json(self, *args, **kwargs):
        """
        Return a decoded JSON request body.

        ``*args`` and ``**kwargs`` are passed to the ``JSONDecoder``
        constructor.

        This will try to decode a json string regardless of the mime type sent
        by the client.
        """
        try:
            return self.json_decoder_class(*args, **kwargs).decode(self.body)
        except ValueError:
            raise exceptions.RequestParseError("Payload is not valid JSON")

    @property
    def files(self):
        """
        Return a MultiDict of all ``FileUpload`` objects available.
        """
        if self._files is None:
            self._files = MultiDict((k, v) for k, v in self.form.allitems()
                                           if isinstance(v, FileUpload))
        return self._files

    @property
    def query(self, environ_to_unicode=environ_to_unicode):
        """
        Return a ``MultiDict`` of any querystring submitted data.

        This is available regardless of whether the original request was a
        ``GET`` request.

        Synopsis::

            >>> from fresco import FrescoApp
            >>> with FrescoApp().requestcontext('/?animal=moose') as c:
            ...     c.request.query['animal']
            u'moose'

        This property always returns querystring data, regardless of the
        request method used.
        """
        if self._query is None:
            query = environ_to_unicode(self.environ.get('QUERY_STRING', ''))
            self._query = MultiDict(parse_querystring(query, self.charset))

        return self._query

    def __getitem__(self, key):
        """
        Return the value of ``key`` from submitted form values.
        """
        marker = []
        v = self.get(key, marker)
        if v is marker:
            raise KeyError(key)
        return v

    def get(self, key, default=None):
        """
        Look up ``key`` in submitted form values
        """
        return self.form.get(key, default)

    def getlist(self, key):
        """
        Return a list of submitted form values for ``key``
        """
        return self.form.getlist(key)

    def __contains__(self, key):
        """
        Return ``True`` if ``key`` is in the submitted form values
        """
        return key in self.form

    @property
    def cookies(self):
        """
        Return a :class:`fresco.multidict.MultiDict` of cookies read from the
        request headers::

            >>> from fresco import FrescoApp
            >>> with FrescoApp().requestcontext(
            ...     HTTP_COOKIE='''Customer="WILE_E_COYOTE";
            ...     Part="Rocket_0001";
            ...     Part="Catapult_0032"
            ... ''') as c:
            ...     request = c.request
            ...
            >>> request.cookies.getlist('Customer')
            ['WILE_E_COYOTE']
            >>> request.cookies.getlist('Part')
            ['Rocket_0001', 'Catapult_0032']

        See rfc2109, section 4.4
        """
        if self._cookies is None:
            self._cookies = MultiDict(
                parse_cookie_header(self.environ.get('HTTP_COOKIE', '')))
        return self._cookies

    def get_header(self, name, default=None):
        """
        Return an arbitrary HTTP header from the request.

        :param name: HTTP header name, eg 'User-Agent' or 'If-Modified-Since'.
        :param default: default value to return if the header is not set.

        Headers in the original HTTP request are always formatted like this::

            If-Modified-Since: Thu, 04 Jan 2007 21:41:08 GMT

        However in the WSGI environment they appear as follows::

            {'HTTP_IF_MODIFIED_SINCE': 'Thu, 04 Jan 2007 21:41:08 GMT'}

        This method expects the former style (eg ``If-Modified-Since``) and is
        not case sensitive.
        """
        return self.environ.get(
            'HTTP_' + name.upper().replace('-', '_'),
            default
        )

    @property
    def path(self):
        """\
        Return the path component of the requested URL
        """
        return environ_to_unicode(self.environ.get('SCRIPT_NAME', '') +
                                  self.environ.get('PATH_INFO', ''))

    @property
    def url(self):
        """\
        Return the full URL, including query parameters.
        """
        return urlunparse(self.parsed_url)

    @property
    def application_url(self):
        """\
        Return the base URL of the WSGI application (up to SCRIPT_NAME but not
        including PATH_INFO or query information).

        Synopsis::

            >>> from fresco import FrescoApp
            >>> with FrescoApp().requestcontext(HTTP_HOST='example.com',
            ...                                 SCRIPT_NAME='/animals',
            ...                                 PATH_INFO='/lion.html') as c:
            ...     c.request.application_url
            u'http://example.com/animals'
        """
        scheme, netloc, path, params, query, frag = self.parsed_url

        return urlunparse((scheme, netloc,
                           quote(self.script_name.encode(self.charset)), '',
                           '', ''))

    @property
    def parsed_url(self):
        """\
        Return the current URL as a tuple of the form::

            (addressing scheme, network location, path,
             parameters, query, fragment identifier)

        Synopsis::

            >>> from fresco import FrescoApp
            >>> app = FrescoApp()
            >>> with app.requestcontext(
            ...          'https://example.com/animals/view?name=lion') as c:
            ...     c.request.parsed_url  # doctest: +ELLIPSIS
            ParseResult(scheme=u'https', netloc=u'example.com', ...)

        Components are returned as unicode strings
        """
        if self._parsed_url:
            return self._parsed_url

        env = self.environ.get
        script_name = quote(self.script_name.encode(self.charset))
        path_info = quote(self.path_info.encode(self.charset))
        query_string = self.query_string
        scheme = environ_to_unicode(env('wsgi.url_scheme', 'http'))

        try:
            host = environ_to_unicode(self.environ['HTTP_HOST'])
            if ':' in host:
                host, port = host.split(':', 1)
            else:
                if scheme == 'https':
                    port = '443'
                else:
                    port = '80'
        except KeyError:
            host = environ_to_unicode(self.environ['SERVER_NAME'])
            port = environ_to_unicode(self.environ['SERVER_PORT'])

        if (scheme == 'http' and port == '80') \
                or (scheme == 'https' and port == '443'):
            netloc = host
        else:
            netloc = host + ':' + port

        self._parsed_url = ParseResult(scheme,
                                       netloc,
                                       script_name + path_info,
                                       '',  # Params
                                       query_string,
                                       '',  # Fragment
                                       )
        return self._parsed_url

    @property
    def path_info(self, environ_to_unicode=environ_to_unicode):
        """
        The PATH_INFO value as a unicode string

        Note that PATH_INFO is already unquoted by the server
        """
        try:
            return environ_to_unicode(self.environ.get('PATH_INFO', ''),
                                      self.charset)
        except UnicodeDecodeError:
            raise exceptions.BadRequest

    @property
    def script_name(self):
        """\
        The SCRIPT_NAME value as a unicode string

        Note that SCRIPT_NAME is already unquoted by the server
        """
        try:
            return environ_to_unicode(self.environ.get('SCRIPT_NAME', ''),
                                      self.charset)
        except UnicodeDecodeError:
            raise exceptions.BadRequest

    @property
    def query_string(self, environ_to_unicode=environ_to_unicode):
        """\
        The QUERY_STRING value as a unicode string
        """
        s = self.environ.get('QUERY_STRING')
        if s is None:
            return s
        return environ_to_unicode(s)

    @property
    def referrer(self):
        """
        Return the HTTP referer header, or ``None`` if this is not available.
        """
        s = self.environ.get('HTTP_REFERER')
        if s is None:
            return s
        return environ_to_unicode(s)

    @property
    def method(self):
        """
        Return the HTTP method used for the request, eg ``GET`` or ``POST``.
        """
        return self.environ["REQUEST_METHOD"]

    @property
    def remote_addr(self):
        """
        Return the remote address of the client
        """
        s = self.environ.get('REMOTE_ADDR')
        if s is None:
            return s
        return environ_to_unicode(s)

    @property
    def session(self):
        """
        Return the session associated with this request.

        Requires a session object to have been inserted into the WSGI
        environment by a middleware application.
        """
        return self.environ.get(self.SESSION_ENV_KEY)

    @property
    def is_secure(self):
        """
        Return ``True`` if the request is served over a secure connection.
        """
        return self.environ['wsgi.url_scheme'] == 'https'

    def make_url(self, scheme=None, netloc=None, path=None, parameters=None,
                 query=None, query_add=None, query_replace=None, fragment=None,
                 SCRIPT_NAME=None, PATH_INFO=None, **kwargs):
        r"""\
        Make a new URL based on the current URL, replacing any of the six
        URL elements (scheme, netloc, path, parameters, query or fragment). The
        current request's query string is not included in the generated URL
        unless you explicitly pass it in.

        :param scheme:      The URL scheme, eg ``http`` or ``https``
        :param netloc:      The netloc portion of the URL, eg 'example.com:80'
        :param path:        The path portion of the URL, eg '/my/page.html'
        :param parameters:  RFC2396 path parameters (see also the stdlib
                            urlparse module)
        :param fragment:    The URL fragment
        :param query:       Query data, as a list of tuples, a dict or a string
        :param query_add:   Query parameters to add. If the current url already
                            contains query parameters with the same name, these
                            will be supplemented with the new values.
        :param query_replace: Query parameters to replace. If the current url
                              already contains query parameters with the same
                              name, these will be replaced with the new values.
        :param PATH_INFO:   The PATH_INFO portion of the path. Overrides
                            ``path``
        :param SCRIPT_NAME: The SCRIPT_NAME portion of the path. Overrides
                            ``path``
        :param kwargs:      Any remaining keyword arguments are appended to the
                            querystring
        :rtype: str

        All arguments (other than query related arguments, see examples below)
        may be byte strings or unicode strings (native strings in python 3).
        Where necessary values will be converted to utf-8 encoded byte strings.

        Examples:

        Reproduce the request URL::

            >>> from fresco import FrescoApp
            >>> with FrescoApp().requestcontext(HTTP_HOST='example.com',
            ...                                 SCRIPT_NAME='/fruitsalad',
            ...                                 PATH_INFO='/banana',
            ...                                 QUERY_STRING='cream=n') as c:
            ...     request = c.request

            >>> request.make_url(query=request.query)
            u'http://example.com/fruitsalad/banana?cream=n'

        Replace the URL scheme::

            >>> request.make_url(scheme='ftp')
            u'ftp://example.com/fruitsalad/banana'

        Replace the entire path::

            >>> request.make_url(path='/sausages')
            u'http://example.com/sausages'

        Replace just the path_info portion::

            >>> request.make_url(PATH_INFO='/sausages')
            u'http://example.com/fruitsalad/sausages'

        Add a query string::

            request.make_url(query={'portions': '2'}, cherries='n')
            u'http://example.com/fruitsalad/banana?portions=2;cherries='n'

        If a relative path is passed, the returned URL is joined to the old in
        the same way as a web browser would interpret a relative HREF in a
        document at the current location::

            >>> request.make_url(path='kiwi')
            u'http://example.com/fruitsalad/kiwi'

            >>> request.make_url(path='../strawberry')
            u'http://example.com/strawberry'

            >>> request.make_url(path='../../../plum')
            u'http://example.com/plum'

        The ``query`` argument can take a dictionary, a list of ``(name,
        value)`` pairs or any other type convertable to a MultiDict::

            >>> request.make_url(query='a=tokyo&b=milan')
            u'http://example.com/fruitsalad/banana?a=tokyo&b=milan'

            >>> request.make_url(query={'a': 'tokyo', 'b': 'milan'})
            u'http://example.com/fruitsalad/banana?a=tokyo;b=milan'

            >>> request.make_url(query=[('a', 'tokyo'),
            ...                         ('b', 'milan'),
            ...                         ('b', 'paris')])
            u'http://example.com/fruitsalad/banana?a=tokyo;b=milan;b=paris'

        The ``query_add`` and ``query_replace`` arguments add or replace
        values in an existing query string. If either of these is specified
        then the current request's query string (or value of ``query``, if
        specified) will be extended with the given values.
        These arguments take a dict, a list of ``(key, value)`` tuples, or any
        other type convertable to a MultiDict.
        """
        url = []
        parsed_url = self.parsed_url

        if path is not None:
            if not isinstance(path, bytes):
                path = path.encode('utf-8')
            path = quote(path)

            if path[0] != '/':
                path = posixpath.join(
                        posixpath.dirname(parsed_url[2]), path)
                path = posixpath.normpath(path)

        elif SCRIPT_NAME is not None or PATH_INFO is not None:
            if SCRIPT_NAME is None:
                SCRIPT_NAME = self.script_name
            if PATH_INFO is None:
                PATH_INFO = self.path_info
            path = SCRIPT_NAME + PATH_INFO
            if not isinstance(path, bytes):
                path = path.encode('utf-8')
            path = quote(path)

        else:
            path = parsed_url[2]

        if query is not None:
            if isinstance(query, ustr):
                # Unicode queries should be pre-encoded and thus contain ascii
                # characters only
                query = query.encode('ASCII')
            elif isinstance(query, bytes):
                if kwargs:
                    if query:
                        query += ';'
                    query += make_query(kwargs)

        if (query_add or query_replace) and isinstance(query, bytes):
            query = MultiDict(parse_querystring(query.decode('ASCII')))

        if query_add is not None:
            query = query if query is not None else self.query.copy()
            query.extend(query_add)

        if query_replace is not None:
            query = query if query is not None else self.query.copy()
            query.update(query_replace)

        if query and not isinstance(query, bytes):
            query = make_query(query, **kwargs)

        url = [scheme if scheme is not None else parsed_url[0],
               netloc if netloc is not None else parsed_url[1],
               path if path is not None else parsed_url[2],
               parameters if parameters is not None else parsed_url[3],
               query,
               fragment]

        return urlunparse(url)

    def resolve_url(self, url, relative='app'):
        """
        Resolve a partially qualified URL in context of the current request.

        :param url:      A url, may be fully or partially qualified
        :param relative: One of 'app' or 'server'
        :return: A fully qualified URL

        Examples::

            >>> from fresco import FrescoApp
            >>> app = FrescoApp()
            >>> with app.requestcontext('http://example.net/foo/bar') as c:
            ...     request = c.request
            ...
            >>> request.resolve_url('/baz')
            'http://example.net/baz'
            >>> request.resolve_url('baz')
            'http://example.net/foo/baz'
            >>> request.resolve_url('http://anotherhost/bar')
            'http://anotherhost/bar'

        The returned URL path will be normalized:

            >>> app = FrescoApp()
            >>> with app.requestcontext('http://example.net/foo/bar') as c:
            ...     c.request.resolve_url('../bar')
            ...
            'http://example.net/bar'

        URLs can be resolved relative to the application's base URL (including
        SCRIPT_NAME) or the server root via the ``relative`` argument::

            >>> from fresco import FrescoApp
            >>> app = FrescoApp()
            >>> with app.requestcontext(SCRIPT_NAME='/foo',
            ...                         PATH_INFO='bar') as c:
            ...     request = c.request
            >>> request.resolve_url('/baz', relative='app')
            'http://localhost/foo/baz'
            >>> request.resolve_url('/baz', relative='server')
            'http://localhost/baz'

        If not specified, application relative paths will be assumed.
        """
        env = self.environ.get

        if '://' not in url:
            scheme = env('wsgi.url_scheme', 'http')

            if scheme == 'https':
                port = ':' + env('SERVER_PORT', '443')
            else:
                port = ':' + env('SERVER_PORT', '80')

            if scheme == 'http' and port == ':80' \
               or scheme == 'https' and port == ':443':
                port = ''

            parsed = urlparse(url)
            path_info = env('PATH_INFO', '')
            script_name = env('SCRIPT_NAME', '')

            if path_info[-1] != '/':
                path_info = path_info[:path_info.rfind('/') + 1]

            if relative == 'app':
                path = posixpath.join(quote(path_info), parsed[2])
                path = quote(script_name) + normpath(path)

            else:
                path = posixpath.join(quote(script_name) + path_info,
                                      parsed[2])

            url = urlunparse((
                env('wsgi.url_scheme', ''),
                env('HTTP_HOST', env('SERVER_NAME', '') + port),
                normpath(path),
                parsed[3],
                parsed[4],
                parsed[5],
            ))
        return url


def currentrequest():
    """\
    Return the current value of ``context.request``, or ``None`` if there is no
    request in scope.
    """
    try:
        return fresco.context.request
    except AttributeError:
        return None

from .util.http import (FileUpload, parse_querystring, parse_post,
                        get_content_type_info, get_body_bytes)
