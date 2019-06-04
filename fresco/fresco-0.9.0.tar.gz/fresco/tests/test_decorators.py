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

from fresco import FrescoApp, GET, Response
from fresco.decorators import extract_getargs, json_response


class TestExtractGetArgs(object):

    def test_mixed_with_dispatcher_args(self):

        app = FrescoApp()

        @app.route(r'/<arg1:str>/<arg2:str>', GET)
        @extract_getargs(arg1=str, arg2=int)
        def handler(arg1, arg2):
            return Response([
                'Received %r:%s, %r:%s' % (arg1, type(arg1).__name__,
                                           arg2, type(arg2).__name__)
            ])

        with app.requestcontext('/foo/29'):
            assert list(app.view().content_iterator) == \
                    [b"Received 'foo':str, 29:int"]

    def test_query_args(self):

        @extract_getargs(arg1=str, arg2=int)
        def view(arg1, arg2):
            return Response([
                'Received %r:%s, %r:%s' % (arg1, type(arg1).__name__,
                                           arg2, type(arg2).__name__)
            ])

        app = FrescoApp()
        app.route('/', GET, view)
        with app.requestcontext('/?arg1=foo;arg2=29'):
            assert list(app.view().content_iterator) == \
                    [b"Received 'foo':str, 29:int"]

    def test_missing_args_with_one_default_argument(self):

        @extract_getargs(arg1=str, arg2=int)
        def view(arg1, arg2):
            return Response([
                'Received %r:%s, %r:%s' % (arg1, type(arg1).__name__,
                                           arg2, type(arg2).__name__)
            ])

        app = FrescoApp()
        app.route('/', GET, view)
        with app.requestcontext('/?arg1=foo'):
            assert app.view().status_code == 400

    def test_missing_args(self):

        @extract_getargs(arg1=str, arg2=int)
        def view(arg1, arg2=None):
            return Response([
                'Received %r:%s, %r:%s' % (arg1, type(arg1).__name__,
                                           arg2, type(arg2).__name__)
            ])

        app = FrescoApp()
        app.route('/', GET, view)
        with app.requestcontext('/?arg1=foo'):
            assert app.view().status == '200 OK'
            assert list(app.view().content_iterator) == \
                    [b"Received 'foo':str, None:NoneType"]

    def test_conversion_error_without_default(self):

        @extract_getargs(arg1=int)
        def view(arg1):
            return Response([])

        app = FrescoApp()
        app.route('/', GET, view)
        with app.requestcontext('/?arg1=foo'):
            assert app.view().status_code == 400

    def test_conversion_error_with_strict_checking(self):

        @extract_getargs(arg1=int, strict_checking=True)
        def view(arg1=None):
            return Response([
                'Received %r:%s' % (arg1, type(arg1).__name__)
            ])

        app = FrescoApp()
        app.route('/', GET, view)
        with app.requestcontext('/?arg1=foo'):
            assert app.view().status_code == 400

    def test_no_conversion_error_with_default(self):

        @extract_getargs(arg1=int)
        def view(arg1=None):
            return Response([
                'Received %r:%s' % (arg1, type(arg1).__name__)
            ])

        app = FrescoApp()
        app.route('/', GET, view)
        with app.requestcontext('/?arg1=foo'):
            assert list(app.view().content_iterator) == \
                    [b'Received None:NoneType']


class TestJSONResponse(object):

    def test_it_allows_custom_formatting(self):
        r = json_response({'l': [1, 2, 3]},
                          indent=1, separators=(', ', ': '))
        assert list(r.content_iterator) == \
                [b'{\n "l": [\n  1, \n  2, \n  3\n ]\n}']

    def test_it_acts_as_a_filter(self):
        r = json_response({'l': [1, 2, 3]})
        assert list(r.content_iterator) == [b'{"l":[1,2,3]}']
        assert r.get_header('content-type') == 'application/json'

    def test_it_acts_as_a_decorator(self):
        @json_response()
        def f():
            return {'l': [1, 2, 3]}
        assert list(f().content_iterator) == [b'{"l":[1,2,3]}']

    def test_it_acts_as_a_decorator_without_arguments(self):
        @json_response
        def f():
            return {'l': [1]}
        assert list(f().content_iterator) == [b'{"l":[1]}']
