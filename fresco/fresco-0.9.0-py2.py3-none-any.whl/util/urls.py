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
Utilities functions for URL building and manipulation
"""

from __future__ import absolute_import

try:
    from functools import lru_cache
except ImportError:
    def dummy_lru_cache(size):
        def lru_cache(func):
            return func
        return lru_cache
    lru_cache = dummy_lru_cache

import posixpath
import re
from fresco.compat import quote_plus, urlparse, urlunparse, ustr, string_types

import fresco
from fresco.multidict import MultiDict

__all__ = 'join_path', 'url_join', 'strip_trailing_slashes', 'normpath'


def join_path(a, b):
    """
    Join two URL path segments together.
    Unlike ``os.path.join``, this removes leading slashes before joining the
    paths, so absolute paths are appended as if they were relative.

    Synopsis::

        >>> join_path('/', '/abc')
        '/abc'

        >>> join_path('/', '/abc/')
        '/abc/'

        >>> join_path('/foo', '/bar/')
        '/foo/bar/'

        >>> join_path('/foo/', '/bar/')
        '/foo/bar/'

        >>> join_path('/foo', 'bar')
        '/foo/bar'
    """

    if not b:
        return a

    while a and a[-1] == '/':
        a = a[:-1]

    while b and b[0] == '/':
        b = b[1:]

    return a + '/' + b


def url_join(base, rel):
    """
    Examples::

        >>> from fresco.util.urls import url_join
        >>> url_join('http://example.org/', 'http://example.com/')
        'http://example.com/'
        >>> url_join('http://example.com/', '../styles/main.css')
        'http://example.com/styles/main.css'
        >>> url_join('http://example.com/subdir/', '../styles/main.css')
        'http://example.com/styles/main.css'
        >>> url_join('http://example.com/login', '?error=failed+auth')
        'http://example.com/login?error=failed+auth'
        >>> url_join('http://example.com/login', 'register')
        'http://example.com/register'
    """
    prel = urlparse(rel)

    # Link is already absolute, return it unchanged
    if prel.scheme:
        return rel

    pbase = urlparse(base)
    path = pbase.path
    if prel.path:
        path = normpath(posixpath.join(posixpath.dirname(pbase.path),
                                       prel.path))

    return urlunparse((
        pbase.scheme,
        pbase.netloc,
        path,
        prel.params,
        prel.query,
        prel.fragment
    ))


def strip_trailing_slashes(path):
    """\
    Remove trailing slashes from the given path.

    :param path: a path, eg ``'/foo/bar/'``
    :return: The path with trailing slashes removed, eg ``'/foo/bar'``
    """
    while path and path[-1] == '/':
        path = path[:-1]
    return path


@lru_cache(50)
def normpath(path):
    """
    Return ``path`` normalized to remove '../' etc.

    This differs from ``posixpath.normpath`` in that:

    * trailing slashes are preserved
    * multiple consecutive slashes are always condensed to a single slash

    Examples::

        >>> normpath('/hello/../goodbye')
        '/goodbye'
        >>> normpath('//etc/passwd')
        '/etc/passwd'
        >>> normpath('../../../../etc/passwd')
        'etc/passwd'
        >>> normpath('/etc/passwd/')
        '/etc/passwd/'
    """
    segments = path.split('/')
    newpath = []
    newpath_append = newpath.append
    last = len(segments) - 1
    for pos, seg in enumerate(segments):
        if seg == '' or seg == '.':
            seg = ''
            allow_empty = (
                pos == 0 or
                pos == last and newpath and newpath[-1] != '' or
                pos == last and newpath == [''])
            if not allow_empty:
                continue

        elif seg == '..':
            if newpath and newpath != ['']:
                newpath.pop()
            continue

        newpath_append(seg)

    return '/'.join(newpath)


def make_query(data=None, separator=';', charset=None, **kwargs):
    """\
    Return a query string formed from the given dictionary data.

    Note that the pairs are separated using a semicolon, in accordance with
    `the W3C recommendation
<http://www.w3.org/TR/1999/REC-html401-19991224/appendix/notes.html#h-B.2.2>`_

    If no encoding is given, unicode values are encoded using the character set
    specified by ``fresco.DEFAULT_CHARSET``.

    Basic usage::

        >>> make_query({'search': 'foo bar', 'type': u'full'})
        'search=foo+bar;type=full'

        >>> make_query(search='foo', type=u'quick')
        'search=foo;type=quick'

    Changing the separator to '&'::

        >>> make_query({'search': 'foo', 'type': u'full'}, separator='&')
        'search=foo&type=full'

    Multiple values can be provided per key::

        >>> make_query(search=['foo', u'bar'])
        'search=foo;search=bar'

    Exclude values by setting them to ``None``::

        >>> make_query(x=1, y=None)
        'x=1'

    :param data: data for query string
    :param separator: separator used between each key value pair
    :param charset: encoding to be used for unicode values
    :rtype: str
    """
    if isinstance(data, MultiDict):
        items = list(data.allitems())
    elif isinstance(data, dict):
        items = list(data.items())
    elif data is None:
        items = []
    else:
        items = list(data)
    items += list(kwargs.items())

    if charset is None:
        charset = fresco.DEFAULT_CHARSET

    items = _repeat_keys(items)
    items = ((k, v) for k, v in items if v is not None)
    return separator.join(_qs_frag(k, v, charset=charset) for k, v in items)


def _qs_frag(key, value, charset=None):
    """\
    Return a fragment of a query string in the format 'key=value'::

        >>> _qs_frag('search-by', 'author, editor')
        'search-by=author%2C+editor'

    If no encoding is specified, unicode values are encoded using the character
    set specified by ``fresco.DEFAULT_CHARSET``.

    :rtype: str
    """
    if charset is None:
        charset = fresco.DEFAULT_CHARSET

    key = ustr(key).encode(charset)
    value = ustr(value).encode(charset)

    return quote_plus(key) + '=' + quote_plus(value)


def _repeat_keys(iterable):
    """
    Return a list of ``(key, scalar_value)`` tuples given an iterable
    containing ``(key, iterable_or_scalar_value)``.

    Example::

        >>> list(
        ...     _repeat_keys([('a', 'b')])
        ... )
        [('a', 'b')]
        >>> list(
        ...     _repeat_keys([('a', ['b', 'c'])])
        ... )
        [('a', 'b'), ('a', 'c')]
    """

    for key, value in iterable:
        if isinstance(value, string_types):
            value = [value]
        else:
            try:
                value = iter(value)
            except TypeError:
                value = [value]

        for subvalue in value:
            yield key, subvalue


_valid_url_chars = re.compile(
    r"^(?:[A-Za-z0-9\-._~:/?#\[\]@!$&'\(\)\*\+,;=']+|%[0-9A-Fa-f]{2})*$")


def is_safe_url(url,
                allowed_hosts=frozenset(),
                allowed_schemes={'http', 'https'},
                valid_url=_valid_url_chars.match,
                urlparse=urlparse):
    """
    Return True if the given URL is for a trusted origin and can safely be
    redirected to.

    :param allowed_hosts: a list of hosts considered trusted. If not supplied
                          the current HTTP_HOST and SERVER_NAME are used.
    :param allowed_schemes: a list of permitted URL schemes. Defaults to
                            ``{'http', 'https'}``
    """
    if not url:
        return False
    if url.startswith('///'):
        return False
    if not valid_url(url):
        return False

    if not allowed_hosts:
        try:
            from fresco import context
            env = context.request.environ.get
        except AttributeError:
            env = {}.get
        allowed_hosts = {env('HTTP_HOST', env('SERVER_NAME', ''))}

    parsed = urlparse(url)
    scheme = parsed.scheme
    netloc = parsed.netloc

    return (
        (scheme in allowed_schemes and netloc in allowed_hosts) or
        (scheme == '' and netloc == '') or
        (scheme == '' and netloc in allowed_hosts))
