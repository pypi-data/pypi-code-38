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
# See LICENSE.txt for terms of redistribution and use.

from __future__ import absolute_import
from __future__ import unicode_literals
from io import BytesIO
import re

from hypothesis import given, strategies as st
import pytest

from fresco.compat import quote, ustr
from fresco.exceptions import RequestParseError
from fresco.util.http import (parse_querystring,
                              parse_post,
                              parse_parameters,
                              encode_multipart,
                              )
from fresco import FrescoApp, context, Response, POST

from . import form_data


class TestParseQueryString(object):

    def p(self, value):
        return list(parse_querystring(value))

    def test_empty(self):
        self.p('') == []

    def test_simple_key_value(self):
        assert self.p('a=b') == [('a', 'b')]

    def test_key_with_space(self):
        assert self.p('a+b=c') == [('a b', 'c')]

    def test_value_with_space(self):
        assert self.p('a=b+c') == [('a', 'b c')]

    def test_double_equals(self):
        assert self.p('a==b') == [('a', '=b')]

    def test_escaped_chars(self):
        assert self.p('%20==c%3D') == [(' ', '=c=')]

    def test_charset(self):
        assert self.p('a=el%20ni%C3%B1o') == [('a', 'el niño')]


class TestParseMultipart(object):

    def _make_env(self, data):
        data = (b'----XX\r\n' + data + b'----XX--\r\n')
        return (BytesIO(data),
                {'CONTENT_LENGTH': len(data),
                'CONTENT_TYPE': 'multipart/form-data; boundary=--XX'})


    def test_multipart(self):
        for data in form_data.multipart_samples:
            io = BytesIO(data['data'])
            io.seek(0)
            environ = {
                'CONTENT_LENGTH': data['content_length'],
                'CONTENT_TYPE': data['content_type'],
            }
            parsed = sorted(list(parse_post(environ, io, 'UTF-8')))

            assert [name for name, value in parsed] == \
["empty-text-input", "file-upload", "text-input-ascii", "text-input-unicode"]

            assert parsed[0] == ("empty-text-input", "")
            assert parsed[2] == ("text-input-ascii", "abcdef")
            assert parsed[3] == ("text-input-unicode",
                                    b"\xce\xb1\xce\xb2\xce\xb3\xce\xb4"
                                    .decode("utf8"))

            fieldname, fileupload = parsed[1]
            assert fieldname == "file-upload"
            assert fileupload.filename == "test.data"
            assert fileupload.headers['content-type'] == \
                        "application/octet-stream"
            assert fileupload.file.read() == form_data.FILE_UPLOAD_DATA

    def test_non_ascii_headers(self):
        """
        Ensure that headers containing non-ascii characters are handled.
        NB the stdlib email.parser module that we use for parsing replaces
        any 8-bit characters with the unicode replacement character.
        """
        filename = 'café.txt'.encode('utf8')
        data = (
            b'----XXXXXX\r\n'
            b'Content-Disposition: form-data; name="u"; '
            b'filename="' + filename + b'"\r\n'
            b'Content-Type: application/octet-stream\r\n\r\n'
            b'1234567890\r\n'
            b'----XXXXXX--\r\n')
        environ = {
            'CONTENT_LENGTH': len(data),
            'CONTENT_TYPE': 'multipart/form-data; boundary=--XXXXXX'}
        f = BytesIO(data)
        parsed = list(parse_post(environ, f, 'UTF-8'))
        fieldname, fileupload = parsed[0]
        assert fileupload.filename == 'caf\uFFFD\uFFFD.txt'

    def test_malformed_headers_raise_exceptions(self):
        # Missing '=' in parameter
        data, env = self._make_env(
            b'Content-Disposition: form-data; name; \r\n\r\n'
            b'1234567890\r\n'
        )
        with pytest.raises(RequestParseError):
            list(parse_post(env, data))

    def test_fileupload_too_big(self):
        """\
        Verify that multipart/form-data encoded POST data raises an exception
        if the total data size exceeds request.MAX_SIZE bytes
        """

        def view():
            request = context.request
            request.MAX_MULTIPART_SIZE = 500
            request.get('f1')
            return Response(['ok'])
        app = FrescoApp()
        app.route('/', POST, view)

        with app.requestcontext_post(
                '/', files=[('f1', 'filename.txt', 'text/plain', 'x' * 1000)]):
            assert app.view().status == "413 Payload Too Large"

        with app.requestcontext_post(
                '/',
                files=[('f1', 'filename.txt', 'text/plain', 'x' * 400)],
                data={'f2': 'x' * 101}):
            assert app.view().status == "413 Payload Too Large"

    def test_fileupload_with_invalid_content_length(self):

        def view():
            request = context.request
            request.get('f1')
            return Response(['ok'])
        app = FrescoApp()
        app.route('/', POST, view)

        with app.requestcontext_post(
                '/',
                files=[('f1', 'filename.txt', 'text/plain', 'x' * 1000)]) as c:
            c.request.environ['CONTENT_LENGTH'] = str('500')
            assert app.view().status == "400 Bad Request"

    def test_multipart_field_too_big(self):
        """
        Verify that multipart/form-data encoded POST data raises an exception
        if it contains a single field exceeding request.MAX_SIZE bytes
        """
        def view():
            request = context.request
            request.MAX_MULTIPART_SIZE = 500
            request.MAX_SIZE = 100
            request.get('f1')
            return Response(['ok'])
        app = FrescoApp()
        app.route('/', POST, view)

        with app.requestcontext_post('/',
                                     multipart=True,
                                     data=[('f1', 'x' * 200)]):
            assert app.view().status == "413 Payload Too Large"


class TestParseFormEncodedData(object):

    char_latin1 = b'\xa3'
    char_utf8 = b'\xc2\xa3'
    char = char_latin1.decode('latin1')

    assert char_latin1.decode('latin1') == char_utf8.decode('utf8') == char

    def test_formencoded_data_too_big(self):
        """
        Verify that application/x-www-form-urlencoded POST data raises an
        exception if it exceeds request.MAX_SIZE bytes
        """
        def view():
            request = context.request
            request.MAX_SIZE = 100
            request.get('f1')
            return Response(['ok'])
        app = FrescoApp()
        app.route('/', POST, view)

        with app.requestcontext_post('/',
                                     data=[('f1', 'x' * 200)]):
            assert app.view().status == "413 Payload Too Large"

    def test_posted_data_contains_non_ascii_chars(self):
        """
        Verify that it raises an exception if POST data contains invalid
        characters.
        """
        def view():
            context.request.get('f1')

        app = FrescoApp()
        app.route('/', POST, view)

        data = 'foo=bár'.encode('utf8')

        with app.requestcontext(
                '/',
                REQUEST_METHOD='POST',
                CONTENT_LENGTH=ustr(len(data)),
                CONTENT_TYPE='application/x-www-form-urlencoded',
                wsgi_input=data):
            response = app.view()
            assert response.status == "400 Bad Request"

    def test_non_utf8_data_posted(self):

        data = b'char=' + quote(self.char_latin1).encode('ascii')
        env = {'REQUEST_METHOD': 'POST',
               'CONTENT_LENGTH': str(len(data)),
               'wsgi.input': BytesIO(data)}

        with FrescoApp().requestcontext(environ=env) as c:
            request = c.request
            request.charset = 'latin1'
            assert request.form['char'] == self.char

    def test_non_utf8_data_getted(self):

        data = 'char=' + quote(self.char_latin1)
        env = {'REQUEST_METHOD': 'GET', 'QUERY_STRING': data}

        with FrescoApp().requestcontext(environ=env) as c:
            request = c.request
            request.charset = 'latin1'
            assert request.query['char'] == self.char


class TestEncodeMultipart(object):

    def test_it_encodes_a_data_dict(self):
        data, headers = encode_multipart([('foo', 'bar baf')])
        data = data.getvalue()
        assert b'Content-Disposition: form-data; name="foo"\r\n\r\nbar baf' \
                in data

    def test_it_encodes_a_file_tuple(self):
        data, headers = encode_multipart(
            files=[('foo', 'foo.txt', 'ascii', 'bar')])
        data = data.getvalue()
        expected = (b'Content-Disposition: form-data; '
                    b'name="foo"; filename="foo.txt"\r\n'
                    b'Content-Type: ascii\r\n'
                    b'\r\n'
                    b'bar')
        assert expected in data


class TestParseParameters(object):

    token = st.text(alphabet=''.join(chr(c)
                                     for c in range(33, 127) if chr(c) not in
                                     '()<>@,;:\/[]?="'),
                    min_size=1)

    @given(items=st.lists(st.tuples(token, token)))
    def test_parse_tokens(self, items):
        s = ';'.join('{}={}'.format(k, v) for k,v in items)
        assert parse_parameters(s) == dict(items)

    @given(items=st.lists(st.tuples(token, st.text(min_size=1))))
    def test_parse_parameters(self, items):
        def escape(s):
            return re.sub(r'(["\\\r])', r'\\\1', s)
        s = ';'.join('{}="{}"'.format(k, escape(v)) for k,v in items)
        assert parse_parameters(s) == dict(items)

    def test_semicolons_in_parameters(self):
        assert parse_parameters('name=";"') == {'name': ';'}

    def test_quoted_strings_in_parameters(self):
        assert parse_parameters('name="\\""') == {'name': '"'}

    def test_it_preserves_backslashes(self):
        assert parse_parameters('f="C:\\a.txt"', True) == {'f': 'C:\\a.txt'}
