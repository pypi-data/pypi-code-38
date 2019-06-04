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
# flake8: noqa
from __future__ import absolute_import

from sys import version_info

PY3 = version_info >= (3, 3)

if PY3:
    string_types = (str,)
    ustr = str
else:
    string_types = (basestring,)
    ustr = unicode

if PY3:
    from threading import get_ident

else:
    from thread import get_ident

if PY3:
    from urllib.parse import (quote, quote_plus, unquote, urlparse, urlunparse,
                              ParseResult)

else:
    from urllib import quote, quote_plus, unquote
    from urlparse import urlparse, urlunparse, ParseResult


if PY3:
    def reraise(exc_info):
        raise exc_info[1].with_traceback(exc_info[2])

else:
    exec('def reraise(exc_info): raise exc_info[0], exc_info[1], exc_info[2]')

__all__ = 'PY3', 'string_types', 'ustr',\
          'get_ident', 'quote', 'quote_plus', 'unquote', 'urlparse', \
          'ParseResult', 'reraise'
