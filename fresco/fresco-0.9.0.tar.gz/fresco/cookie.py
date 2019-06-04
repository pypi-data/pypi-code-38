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

try:
    from urllib.parse import quote, unquote
except ImportError:
    from urllib import quote, unquote  # NOQA
from datetime import datetime, timedelta
import warnings

from .compat import ustr


class RequestCookie(ustr):

    @property
    def value(self):
        warnings.warn("The value attribute on request cookies is deprecated",
                      DeprecationWarning, stacklevel=2)
        return self


class Cookie(object):
    """
    Represents an HTTP cookie.

    See rfc2109, HTTP State Management Mechanism

    Example:

        >>> from fresco.cookie import Cookie
        >>> c = Cookie('session_id', 'abc123')
        >>> c.path = '/cgi-bin'
        >>> c.domain = '.example.org'
        >>> c.path
        '/cgi-bin'
        >>> str(c)
        'session_id=abc123;Domain=.example.org;Path=/cgi-bin'
    """
    attributes = [
        ("Comment", "comment"),
        ("Domain", "domain"),
        ("Expires", "expires"),
        ("Max-Age", "max_age"),
        ("Path", "path"),
        ("Secure", "secure"),
        ("HttpOnly", "httponly"),
    ]

    bool_attributes = set(['secure', 'httponly'])

    def __init__(
        self, name, value, max_age=None, expires=None, path='/',
        secure=False, domain=None, comment=None, httponly=False,
        version=1
    ):
        """
        Initialize a ``Cookie`` instance.
        """
        self.name = name
        self.value = value
        self.max_age = max_age
        self.path = path
        self.secure = secure
        self.domain = domain
        self.comment = comment
        self.version = version
        self.expires = expires
        self.httponly = httponly

    def __str__(self):
        """
        Returns a string representation of the cookie in the format, eg
        ``session_id=abc123;Path=/cgi-bin;Domain=.example.com;HttpOnly``
        """
        cookie = ['%s=%s' % (self.name, quote(str(self.value)))]
        for cookie_name, att_name in self.attributes:
            value = getattr(self, att_name, None)
            if att_name in self.bool_attributes:
                if value:
                    cookie.append(cookie_name)
            elif value is not None:
                if att_name == 'expires':
                    value = format_date(self._expires.utctimetuple())
                cookie.append('%s=%s' % (cookie_name, str(value)))
        return ';'.join(cookie)

    def __bytes__(self):
        return bytes(str(self))

    def set_expires(self, dt):
        """
        Set the cookie ``expires`` value to ``datetime`` object ``dt``
        """
        if dt is not None and not isinstance(dt, datetime):
            raise ValueError("%r is not a datetime" % (dt,))
        self._expires = dt

    def get_expires(self):
        """
        Return the cookie ``expires`` value as an instance of ``datetime``.
        """
        if self._expires is None and self.max_age is not None:
            if self.max_age == 0:
                # Make sure immediately expiring cookies get a date firmly in
                # the past.
                self._expires = datetime(1980, 1, 1)
            else:
                self._expires = datetime.now() + timedelta(seconds=self.max_age)

        return self._expires

    expires = property(get_expires, set_expires)


def expire_cookie(cookie_or_name, *args, **kwargs):
    """
    Synopsis:

        >>> from fresco import Response
        >>> from fresco.cookie import expire_cookie
        >>> def view():
        ...     return Response(set_cookie=expire_cookie('X', path='/'))
        ...
        >>> from fresco import FrescoApp
        >>> with FrescoApp().requestcontext() as c:
        ...     print(view().get_header('Set-Cookie'))
        ...
        X=;Expires=Tue, 01 Jan 1980 00:00:00 GMT;Max-Age=0;Path=/
    """
    if isinstance(cookie_or_name, Cookie):
        expire = cookie_or_name
    else:
        expire = Cookie(name=cookie_or_name, value='', *args, **kwargs)
    return Cookie(
        name=expire.name,
        value='',
        expires=datetime(1980, 1, 1),
        max_age=0,
        domain=kwargs.get('domain', expire.domain),
        path=kwargs.get('path', expire.path)
    )


def parse_cookie_header(cookie_string, unquote=unquote):
    """
    Return a list of cookie (name, value) pairs read from the request headers.

    :param cookie_string: The cookie, eg ``CUSTOMER=FRED``
    :param unquote: A function to decode values. By default values are assumed
                    to be url quoted. If ``None`` the raw value will be
                    returned
    """
    if not cookie_string:
        return []
    cookies = []

    for part in cookie_string.split(";"):

        try:
            k, v = part.strip().split("=", 1)
        except ValueError:
            continue

        if k[0] == '$':
            # An attribute (eg path or domain) pertaining to the most recently
            # read cookie.
            # These were defined in RFC2109 and RFC2965, but removed in RFC6265
            # (April 2011) and as far as I know not used by browsers.
            # In any case we are only interested in parsing the value,
            # so we can drop these.
            continue

        # Unquote quoted values ('"..."' => '...')
        if v and '"' == v[0] == v[-1] and len(v) > 1:
            v = v[1:-1]

        if unquote:
            k, v = unquote(k), unquote(v)
        cookies.append((k, RequestCookie(v)))

    return cookies


def format_date(utctimetuple):
    """
    Format a date for inclusion in a Set-Cookie header, eg
    'Sun, 06 Nov 1994 08:49:37 GMT'.

    According to RFC6265, this must be an
    "rfc1123-date, defined in RFC2616, Section 3.3.1"

    RFC2616 says in turn:

        HTTP applications have historically allowed three different formats
        for the representation of date/time stamps:

        Sun, 06 Nov 1994 08:49:37 GMT  ; RFC 822, updated by RFC 1123
        Sunday, 06-Nov-94 08:49:37 GMT ; RFC 850, obsoleted by RFC 1036
        Sun Nov  6 08:49:37 1994       ; ANSI C's asctime() format

        The first format is preferred as an Internet standard[...]

    """
    return '%s, %02d %s %04d %02d:%02d:%02d GMT' % (
        ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')[utctimetuple[6]],
        utctimetuple[2],
        ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct',
         'Nov', 'Dec')[utctimetuple[1] - 1],
        utctimetuple[0],
        utctimetuple[3],
        utctimetuple[4],
        utctimetuple[5],
    )
