# encoding=UTF-8
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

from fresco import Route, GET, Response
from fresco.compat import PY3, ustr

# A unicode path that can't be represented using ASCII encoding
if PY3:
    unquoted_unicode_path = '/ø'
else:
    unquoted_unicode_path = ustr('/ø', 'UTF-8')

# IRI quoted version of the same path. This is the string the server
# would receive as the HTTP Request-URI
quoted_unicode_path = '/%C3%B8'

# WSGI encoded version of the path. This is the string that appears in the
# environ dict, and will be a native (unicode) string in python3 and a byte
# string in python 2
if PY3:
    wsgi_unicode_path = b'/\xc3\xb8'.decode('latin1')
else:
    wsgi_unicode_path = b'/\xc3\xb8'

# Malformed path, as sent to the server by a non conforming client.
# The code point has been incorrectly encoded in latin-1 instead of
# UTF-8
if PY3:
    misquoted_wsgi_unicode_path = b'/\xf8'.decode('latin1')
else:
    misquoted_wsgi_unicode_path = b'/\xf8'


class CBV(object):
    """
    A class based view
    """

    __routes__ = [
        Route('/', GET, 'index_html'),
        Route('/page', GET, 'view_page'),
        Route('/page2', GET, 'view_page', tag='page2'),
    ]

    def __init__(self, s):
        self.s = s

    def index_html(self):
        return Response([self.s])

    def view_page(self):
        return Response([])


def module_level_function():
    """
    A module level function
    """
