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

from mock import Mock
import pytest

from fresco import FrescoApp, GET
from fresco.cookie import Cookie
from fresco.response import Response
from fresco.routing import RouteNotFound


class TestCannedResponses(object):

    def test_redirect(self):
        with FrescoApp().requestcontext():
            r = Response.redirect('/new_location')
        assert b'http://localhost/new_location' in b''.join(r.content_iterator)
        assert r.get_header('Location') == 'http://localhost/new_location'
        assert r.status == '302 Found'

    def test_redirect_temporary(self):
        with FrescoApp().requestcontext():
            r = Response.redirect_temporary('/new_location')
        assert b'http://localhost/new_location' in b''.join(r.content_iterator)
        assert r.get_header('Location') == 'http://localhost/new_location'
        assert r.status == '302 Found'

    def test_redirect_permanent(self):
        with FrescoApp().requestcontext():
            r = Response.redirect_permanent('/new_location')
        assert b'http://localhost/new_location' in b''.join(r.content_iterator)
        assert r.get_header('Location') == 'http://localhost/new_location'
        assert r.status == '301 Moved Permanently'

    def test_redirect_to_view(self):
        app = FrescoApp()
        view = Mock(return_value=Response())
        app.route('/arfle/<barfle:int>', GET, view)
        with app.requestcontext():
            r = Response.redirect(view, barfle=42)
        assert r.get_header('Location') == 'http://localhost/arfle/42'

    def test_redirect_to_view_spec(self):
        app = FrescoApp()
        view = Mock(return_value=Response())
        app.route('/arfle/<barfle:int>', GET, view, name='gloop')
        with app.requestcontext():
            r = Response.redirect('gloop', barfle=42)
        assert r.get_header('Location') == 'http://localhost/arfle/42'

    def test_redirect_to_simple_string(self):
        with FrescoApp().requestcontext():
            r = Response.redirect('gloop')
        assert r.get_header('Location') == 'http://localhost/gloop'

    def test_redirect_raises_RouteNotFound(self):
        view = Mock()
        with FrescoApp().requestcontext():
            with pytest.raises(RouteNotFound):
                Response.redirect('gloop', arfle='a')
            with pytest.raises(RouteNotFound):
                Response.redirect(view)

    def test_not_found(self):
        with FrescoApp().requestcontext():
            r = Response.not_found()
        assert b'not found' in b''.join(r.content_iterator).lower()
        assert r.status_code == 404

    def test_method_not_allowed(self):
        with FrescoApp().requestcontext():
            r = Response.method_not_allowed(valid_methods=('PUT', 'DELETE'))
        assert b'not allowed' in b''.join(r.content_iterator).lower()
        assert r.status == '405 Method Not Allowed'
        assert r.get_header('Allow') == 'PUT,DELETE'

    def test_meta_refresh(self):
        with FrescoApp().requestcontext():
            r = Response.meta_refresh('/next_page')
        content = b''.join(r.content_iterator)
        assert b'<a href="http://localhost/next_page">' in content
        assert b'<meta http-equiv="refresh" content="0;'\
               b' url=http://localhost/next_page">' in content
        assert r.status == '200 OK'
        assert r.get_header('Content-Type') == 'text/html'

    def test_json(self):
        with FrescoApp().requestcontext():
            r = Response.json({'arfle': 'barfle'},
                              status=201,
                              indent=4,
                              separators=(',', ':\t'))
        assert r.status == '201 Created'
        assert r.get_header('Content-Type') == 'application/json'
        assert b''.join(r.content_iterator) == b'{\n    "arfle":\t"barfle"\n}'


class TestResponse(object):

    def test_unknown_response_header_from_python_symbol(self):
        r = Response(x_myheader='Foo', content_type=None)
        assert r.headers == [('X-Myheader', 'Foo')]

    def test_standard_headers_capitalized_from_symbol(self):
        r = Response(etag='foo')
        assert r.headers == [('ETag', 'foo')]

        r = Response(x_ua_compatible='foo')
        assert r.headers == [('X-UA-Compatible', 'foo')]

    def test_content_type_added_only_if_content(self):
        r = Response(content=[])
        assert 'Content-Type' in dict(r.headers)

        r = Response()
        assert 'Content-Type' not in dict(r.headers)

        r = Response(content=None)
        assert 'Content-Type' not in dict(r.headers)

    def test_add_response_header(self):
        r = Response(x_myheader='Foo')
        r = r.add_header('X-Myheader', 'Bar')
        assert r.headers == [('X-Myheader', 'Foo'), ('X-Myheader', 'Bar')]

    def test_set_content_type_header(self):
        r = Response(content_type='text/rtf; charset=ISO-8859-1')
        assert r.get_header('Content-Type') == 'text/rtf; charset=ISO-8859-1'

    def test_set_cookie(self):
        r = Response(set_cookie=Cookie(name='fruit', value='banana'))
        assert r.get_header('Set-Cookie') == 'fruit=banana;Path=/'

    def test_delete_cookie(self):
        r = Response().delete_cookie(name='fruit')
        assert r.get_header('Set-Cookie') == (
            'fruit=;Expires=Thu, 01 Jan 1970 00:00:00 GMT;Max-Age=0;Path=/')

    def test_response_get_headers(self):

        r = Response(['whoa nelly!'],
                     content_type='text/plain',
                     x_test_header=["1", "2"])
        assert r.get_header('content-type') == 'text/plain'
        assert r.get_header('x-test-header') == '1,2'
        assert r.get_header('X-Test-Header') == '1,2'
        assert r.get_header('x-does-not-exist', 'boo!') == 'boo!'

    def test_response_buffered_sets_content_length(self):
        r = Response(['whoa nelly!']).buffered()
        assert r.get_header('content-length') == '11'

        r = Response([u'whoa nélly!']).buffered()
        assert r.get_header('content-length') == '12'

    def test_it_encodes_a_unicode_string_according_to_content_type(self):
        r = Response(u'café', content_type='text/plain; charset=utf-8')
        assert list(r({}, Mock())) == [u'café'.encode('utf-8')]
        r = Response(u'café', content_type='text/plain; charset=latin-1')
        assert list(r({}, Mock())) == [u'café'.encode('latin-1')]


class TestAddVary(object):

    def test_it_adds_a_vary_header(self):
        r = Response(content_type='text/plain').add_vary('Accept-Encoding')
        assert ('Vary', 'Accept-Encoding') in r.headers

    def test_it_extends_an_existing_header(self):
        r = Response(content_type='text/plain')\
                .add_vary('Accept-Encoding')\
                .add_vary('Cookie')
        assert 'Cookie' in r.get_header('vary')
        assert 'Accept-Encoding' in r.get_header('vary')
