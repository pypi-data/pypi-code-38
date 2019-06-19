# Copyright (c) 2013, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
Module for primitive, but useful, operations on files, lists and dictionaries.
"""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from collections import OrderedDict
from itertools import islice
from contextlib import contextmanager
import re
import os
import urllib
import sys
import unicodedata
import six
from six.moves import getcwd


_fs_encoding = sys.getfilesystemencoding()


def get_home_dir():
    """
    Return user's home directory or, if that can't be found, the current
    directory.
    """
    home_dir = os.path.expanduser(u'~')

    # os.path.expanduser can fail, for example on Windows if HOME or
    # USERPROFILE don't exist in the environment. If it fails it returns the
    # path unchanged.
    if home_dir == u'~':
        return getcwd()
    else:
        return home_dir


def containing_dirs(paths):
    """
    Filter contained paths leaving only the ones that are not contained in a
    subdirectory of any other path.
    Returns filtered paths.

    >>> paths = ['/usr/bin', '/usr', '/usr/local', '/opt', '/opt/local']
    >>> get_containing_dirs(paths)
    ['/usr', '/opt']
    """
    normal = [os.path.normcase(os.path.realpath(path)).rstrip(os.path.sep)
              for path in paths]
    unique = OrderedDict.fromkeys(normal).keys()
    return [path for path in unique
            if not any(path.startswith(other)
                       for other in unique if other != path)]


def resolve_relative_path(path):
    relative_path = ''
    if path:
        try:
            relative_path = os.path.relpath(six.text_type(path))
        except:
            relative_path = os.path.abspath(six.text_type(path))
    return relative_path


@contextmanager
def open_url(url, mode=None):
    open_file = None
    parsed = six.moves.urllib.parse.urlparse(url)
    if parsed.scheme == 'file' or parsed.scheme == '':
        url = uri_to_path(url)
        opener = lambda url, mode: open(url, mode=mode)
    else:
        opener = lambda url, mode: six.moves.urllib.request.urlopen(url)
    try:
        open_file = opener(url, mode)
        yield open_file
    finally:
        if open_file is not None:
            open_file.close()


def dottedpath(path):
    return path.replace(os.path.sep, '.').replace(':.', '.')


def uri_to_path(url):
    """
    Return a local file or UNC path from a file:-URI.

    The result depends on the host OS.

    On Windows:
    uri_to_path('file:///C:/Users') => 'C:\\Users'

    On Unix:
    uri_to_path('file:///home') => '/home'
    """
    if isinstance(url, six.text_type):
        url = url.encode('ascii')
    parsed = six.moves.urllib.parse.urlparse(url)
    path = parsed.path

    if six.PY3 and not isinstance(path, six.text_type):
        path = path.decode('ascii')

    netloc = parsed.netloc
    local_path = six.moves.urllib.request.url2pathname(path)

    if not six.PY3:
        local_path = local_path.decode('utf8')
        local_path = unicodedata.normalize(
            'NFC', local_path)

    if netloc:
        if isinstance(netloc, six.binary_type):
            netloc = netloc.decode('ascii')

        local_path = '//{}{}'.format(netloc, local_path)

    return os.path.sep.join(local_path.split('/'))


def localuri(path):
    """Create absolute uri from absolute local path."""
    try:
        encoded_path = six.moves.urllib.request.pathname2url(
            path.encode('utf8'))
    except TypeError:
        encoded_path = six.moves.urllib.request.pathname2url(path)
    return six.moves.urllib.parse.urljoin('file:', encoded_path)


def unipath(path):
    """
    Returns universal path for usage in URL, changing all native file
    separators to forward slashes (``'/'``).
    >>> unipath('/usr/bin')
    '/usr/bin'

    However:
    unipath('C:\\Users') should evaluate to C:/Users, on windows and other
    systems where \\ is a separator.
    """
    return '/'.join(path.split(os.sep))


def unipath_separators(path):
    return '/'.join(path.split('\\'))


def nativepath_separators(path):
    return path.replace('\\', os.path.sep).replace('/', os.path.sep)


def nativepath(path):
    """
    Returns a native path from an URL, changing all forward slashes to native
    file separators.
    """
    return os.path.normpath(path)


def concat(nestedlist):
    """
    Concatenate one level of list nesting.
    Returns a new list with one level less of nesting.
    """
    return [item for sublist in nestedlist for item in sublist]


def flip(nested):
    """
    Flips a double nested dict so that the inner dict becomes the outer one.
    Returns a new flipped dictionary.
    """
    result = {}
    for key1, value1 in nested.items():
        for key2, value2 in value1.items() if value1 else {}:
            result[key2] = result.get(key2, {})
            result[key2][key1] = value2
    return result


def group_pairs(pair_list):
    """Return new list of key-value pairs grouped by key."""
    result = OrderedDict()
    for key, value in pair_list:
        acc = result.setdefault(key, [])
        acc.append(value)
    return result.items()


def ungroup_pairs(pair_list):
    """Return new ungrouped list of key-value pairs."""
    return [(key, value) for key, values in pair_list for value in values]


def fuzzy_filter(pattern, items):
    """Filter items whose keys do not match pattern."""
    def fix(char):
        special = """'"*^-.?${},+[]()"""
        if char in special:
            return '\\' + char
        else:
            return char

    escaped = [fix(char) for char in pattern]
    pattern = re.compile('.*'.join([''] + escaped + ['']), re.IGNORECASE)
    return [(key, value) for key, value in items
            if pattern.match(key)]


def nth(iterable, n, default=None):
    """Returns the nth item or a default value."""
    return next(islice(iterable, n, None), default)


def encode_basic(basic, encoding='utf-8'):
    """
    Encode basic structure consisting of basic python types, such as the
    result of using json.load so that all six.text_type strings are encoded.
    Dictionary keys included.
    Return new encoded structure.
    """
    if isinstance(basic, dict):
        return {encode_basic(key, encoding): encode_basic(value, encoding)
                for key, value in six.iteritems(basic)}
    elif isinstance(basic, list):
        return [encode_basic(value, encoding) for value in basic]
    elif isinstance(basic, six.text_type):
        return basic.encode(encoding)
    else:
        return basic


def memoize(function):
    """Memoization of function with non-keyword arguments."""
    memoized = {}

    def wrapper(*args):
        if args not in memoized:
            result = function(*args)
            memoized[args] = result
            return result
        return memoized[args]
    wrapped_function = wrapper
    wrapped_function.__name__ = wrapper.__name__
    wrapped_function.__doc__ = wrapper.__doc__
    return wrapped_function


def combined_key(string):
    """
    Alphanumeric key function.
    It computes the sorting key from string using the string and integer parts
    separately.
    """
    def to_int(string):
        try:
            return int(string)
        except ValueError:
            return string
    return [to_int(part) for part in re.split('([0-9]+)', string)]


def absolute_paths(root, paths):
    return [os.path.normpath(
        path if os.path.isabs(path)
        else os.path.join(root, path)) for path in paths]


def import_statements(filenames):
    """Return a list of all import statements in filenames."""
    regex = re.compile(
        b'^((?:import .*|from [^\.][^\n]* import (?:\([^\)]+\)|.*)?))',
        re.MULTILINE)
    result = []

    for filename in filenames:
        try:
            with open(filename, 'rb') as f:
                result.extend(regex.findall(f.read()))
        except:
            pass

    return sorted(set(
        re.sub(b'[ ]+', b' ',
               re.sub(b'[\n\r()]', b' ', i)).rstrip().decode('ascii')
        for i in set(result)))


def limit_traceback(full_traceback, filename=None):
    """
    Take a full traceback in the format returned by traceback.format_exception
    and return a string produced by joining the lines.

    If filename is specified then traceback rows that are found before the
    first line containing filename will be dropped.
    """
    if filename is None:
        return ''.join(full_traceback)

    filename = os.path.basename(filename)
    start = 1

    for i, row in enumerate(full_traceback):
        if filename in row:
            start = i
            break

    return ''.join([full_traceback[0]] + full_traceback[start:])


def resources_path():
    """Return the path to the Resource folder."""
    file_ = __file__
    if isinstance(file_, six.binary_type):
        file_ = file_.decode(_fs_encoding)

    path = os.path.dirname(file_)
    return os.path.abspath(os.path.join(path, '..', '..', '..',
                                        'Gui', 'Resources'))


def icons_path():
    """Return the path to the icons folder."""
    return os.path.join(resources_path(), 'icons')


def get_icon_path(name):
    """Return the absolute path for the icon with name `name`."""
    return os.path.join(icons_path(), name)


def format_display_string(string, length=0):
    """
    Removes newlines and other whitespace and replaces them with a single
    space. Also removes whitespace at the beginning and the end of the string.
    If length is not zero the returned string will be truncated to that length.
    """
    new_string = re.sub(r'\s+', ' ', string, flags=re.UNICODE).strip()
    return new_string if length == 0 else new_string[:length]
