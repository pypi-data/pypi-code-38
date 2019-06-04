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

from fresco.core import FrescoApp
from fresco.util.urls import normpath, make_query
from fresco.util.urls import is_safe_url

# Greek letters as unicode strings (require multi-byte representation in UTF-8)
alpha = b'\xce\xb1'.decode('utf8')
beta = b'\xce\xb2'.decode('utf8')
gamma = b'\xce\xb3'.decode('utf8')


class TestNormPath(object):

    def test_empty_string(selfself):
        assert normpath('') == ''

    def test_root_url(self):
        assert normpath('/') == '/'

    def test_condenses_consecutive_slashes(self):
        assert normpath('//') == '/'
        assert normpath('///') == '/'

    def test_remove_single_dot(self):
        assert normpath('/./') == '/'

    def test_double_dot_interpreted(self):
        assert normpath('/../') == '/'
        assert normpath('/foo/../') == '/'

    def test_triple_dot_preserved(self):
        assert normpath('/.../') == '/.../'

    def test_combined_patterns(self):
        assert normpath('/..//../') == '/'
        assert normpath("/hello/.//dolly//") == "/hello/dolly/"
        assert normpath("///hello/.//dolly//./..//.//sailor") \
                == "/hello/sailor"

    def test_trailing_slash_preserved(self):
        assert normpath("/sliced/bread/") == "/sliced/bread/"


class TestMakeQuery(object):

    def test_make_query(self):
        assert sorted(make_query(a='1', b=2).split(';')) == ['a=1', 'b=2']
        assert make_query(a='one two three') == 'a=one+two+three'
        assert make_query(a=['one', 'two', 'three']) == 'a=one;a=two;a=three'

    def test_make_query_unicode(self):
        assert make_query(a=[alpha, beta, gamma], charset='utf8') \
                == 'a=%CE%B1;a=%CE%B2;a=%CE%B3'

    def test_make_query_unicode_default_encoding(self):
        assert make_query(a=[alpha, beta, gamma], charset='utf8') \
                == make_query(a=[alpha, beta, gamma])


class TestSafeURL(object):

    def test_it_loads_defaults_from_context(self):
        with FrescoApp().requestcontext(**{'wsgi.url_scheme': 'https',
                                           'HTTP_HOST': 'foo.example.org'}):
            assert is_safe_url("http://foo.example.org/") is True
            assert is_safe_url("https://foo.example.org/") is True
            assert is_safe_url("//foo.example.org/") is True
            assert is_safe_url("http://example.org/") is False
            assert is_safe_url("https://example.org/") is False
            assert is_safe_url("//example.org/") is False

    def test_it_passes_safe_urls(self):
        safe = [
            '/foo',
            'http://good.example.org/x',
            'https://good.example.org/',
            'HTTPS://good.example.org/',
            '//good.example.org/',
            '/path?next_url=http://bad.example.org/',
        ]
        for u in safe:
            assert is_safe_url(u, allowed_hosts={'good.example.org'}) is True

    def test_it_catches_unsafe_urls(self):
        unsafe = [
            '///foo',
            'http://good.example.org@bad.example.org/',
            'http://good.example.org:good.example.org@bad.example.org/',
            'javascript:do_something_bad()',
            '',
            '\x00http://good.example.org',
            'http://good.example.org\nHost: http://bad.example.org',
        ]
        for u in unsafe:
            assert is_safe_url(u, allowed_hosts={'good.example.org'}) is False
