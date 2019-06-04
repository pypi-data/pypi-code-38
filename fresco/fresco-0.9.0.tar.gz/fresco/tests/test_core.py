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

from wsgiref.util import setup_testing_defaults

from mock import Mock, call
import pytest

from fresco import Request, Response
from fresco import FrescoApp, GET, POST, PUT, DELETE
from fresco import Route, urlfor, context
from fresco.util.wsgi import ClosingIterator, make_environ
from . import fixtures


def create_env(**env):
    setup_testing_defaults(env)
    return env


class CustomException(Exception):
    pass


class TestFrescoApp(object):

    def test_route_operates_as_a_decorator(self):

        app = FrescoApp()

        @app.route('/', GET)
        def view():
            return Response([b'ok'])

        with app.requestcontext('/'):
            assert list(app.view().content_iterator) == [b'ok']

    def test_route_operates_as_a_function(self):

        def view():
            return Response([b'ok'])

        app = FrescoApp()
        app.route('/', GET, view)
        with app.requestcontext('/'):
            assert list(app.view().content_iterator) == [b'ok']

    def test_route_returns_route_instance(self):
        def view():
            return Response([b'ok'])

        app = FrescoApp()
        assert isinstance(app.route('/', GET, view), Route)

    def test_route_http_methods(self):

        def view():
            return Response([context.request.environ['REQUEST_METHOD']])

        app = FrescoApp()
        app.route('/get', GET, view)
        app.route('/post', POST, view)

        with app.requestcontext('/get', REQUEST_METHOD='GET'):
            assert app.view().status_code == 200

        with app.requestcontext('/get', REQUEST_METHOD='POST'):
            assert app.view().status_code == 405

        with app.requestcontext('/post', REQUEST_METHOD='GET'):
            assert app.view().status_code == 405

        with app.requestcontext('/post', REQUEST_METHOD='POST'):
            assert app.view().status_code == 200

    def test_HEAD_request_delegated_to_GET_view(self):

        app = FrescoApp()

        @app.route('/', GET)
        def view():
            return Response([], x_original_view='GET')

        with app.requestcontext('/', REQUEST_METHOD='HEAD'):
            assert app.view().get_header('X-Original-View') == 'GET'

    def test_NotFound_observed_when_raised_in_handler(self):

        def app1():
            from fresco.exceptions import NotFound
            if 'foo' in context.request.path_info:
                raise NotFound()
            return Response([b'app1'])

        def app2():
            return Response([b'app2'])

        app = FrescoApp()
        app.route_all('/', GET, app1)
        app.route_all('/', GET, app2)

        with app.requestcontext('/bar'):
            assert list(app.view().content_iterator) == [b'app1']

        with app.requestcontext('/foo'):
            assert list(app.view().content_iterator) == [b'app2']

    def test_NotFound_final_observed_when_raised_in_handler(self):

        def app1():
            from fresco.exceptions import NotFound
            if 'foo' in context.request.path_info:
                raise NotFound(final=True)
            return Response([b'app1'])

        def app2():
            return Response([b'app2'])

        app = FrescoApp()
        app.route_all('/', GET, app1)
        app.route_all('/', GET, app2)

        with app.requestcontext('/bar'):
            assert list(app.view().content_iterator) == [b'app1']

        with app.requestcontext('/foo/'):
            assert app.view().status_code == 404

    def test_apps_called_in_correct_order(self):

        def view(value=''):
            return Response([value])

        app = FrescoApp()
        app.route_all('/f', GET, view, value=b'foo')
        app.route_all('/', GET, view, value=b'bar')

        with app.requestcontext('/f/bar'):
            assert list(app.view().content_iterator) == [b'foo']

        with app.requestcontext('/b/bar'):
            assert list(app.view().content_iterator) == [b'bar']

    def test_wsgi_app_handles_response_exceptions(self):

        from fresco.exceptions import NotFound

        def view():
            raise NotFound()

        app = FrescoApp()
        app.route('/', GET, view)

        with app.requestcontext('/'):
            assert app.view().status_code == 404

    def test_route_wsgi_app(self):

        def wsgiapp(environ, start_response):

            start_response('200 OK',
                           [('Content-Type', 'application/x-pachyderm')])
            return [b'pretty pink elephants']

        app = FrescoApp()
        app.route_wsgi('/', wsgiapp)

        with app.requestcontext('/'):
            assert list(app.view().content_iterator) == \
                    [b'pretty pink elephants']
            assert app.view().get_header('Content-Type') == \
                    'application/x-pachyderm'

    def test_get_methods_matches_on_path(self):

        app = FrescoApp()
        app.route('/1', POST, lambda: None)
        app.route('/1', PUT, lambda: None)
        app.route('/2', GET, lambda: None)
        app.route('/2', DELETE, lambda: None)

        with app.requestcontext() as c:
            assert app.get_methods(app, c.request, '/1') == set([POST, PUT])

        with app.requestcontext() as c:
            assert app.get_methods(app, c.request, '/2') == set([GET, DELETE])

    def test_get_methods_matches_on_predicate(self):

        p1 = Mock(return_value=True)
        p2 = Mock(return_value=False)

        app = FrescoApp()
        app.route('/', POST, lambda: None, predicate=p1)
        app.route('/', PUT, lambda: None, predicate=p2)

        with app.requestcontext('/') as c:
            assert app.get_methods(app, c.request, '/') == set([POST])
            assert p1.call_args_list == [call(c.request)]
            assert p2.call_args_list == [call(c.request)]

    def test_invalid_path_encoding_triggers_bad_request(self):
        app = FrescoApp()
        with app.requestcontext(
                PATH_INFO=fixtures.misquoted_wsgi_unicode_path):
            assert app.view().status_code == 400

    def test_remove_middleware(self):
        app = FrescoApp()
        m1 = Mock()
        m2 = Mock()
        app.add_middleware(m1)
        app.add_middleware(m2)
        app.remove_middleware(m1)
        app(create_env(), Mock()).close()
        assert m1.call_count == 0
        assert m2.call_count == 1

    def test_insert_middleware(self):

        calls = []

        def middleware(app, name):

            def middleware(env, start_response):
                calls.append(name)
                return app(env, start_response)
            return middleware

        app = FrescoApp()
        app.add_middleware(middleware, 'venus')
        app.add_middleware(middleware, 'mercury')
        app.insert_middleware(0, middleware, 'earth')

        # Put a request through app to initialize the WSGI stack
        with app.requestcontext('/'):
            app.view()

        # Middleware is called from the outside-in, so the item inserted in
        # position 0 is last to be called
        assert calls == ['mercury', 'venus', 'earth']

    def test_routing_falls_though_with_fallthrough_on(self):

        app = FrescoApp()
        app.route('/', GET=lambda: Response(status='204 No Content'),
                  fallthrough_on={204})
        app.route('/', GET=lambda: Response(status='200 OK'))

        with app.requestcontext('/'):
            response = app.view()

        assert response.status_code == 200


class TestAppHooks(object):

    def test_process_request_continues_on_none(self):
        app = FrescoApp()
        view = Mock(return_value=Response())
        app.route('/', GET, view)

        @app.process_request
        def process_request(request):
            assert isinstance(request, Request)
            return None

        with app.requestcontext('/'):
            app.view()
            assert view.call_count == 1

    def test_process_request_replaces_response(self):
        app = FrescoApp()
        view = Mock(return_value=Response())
        app.route('/', GET, view)
        new_response = Response()

        @app.process_request
        def process_request(request):
            return new_response

        with app.requestcontext('/'):
            assert app.view() is new_response
            assert view.call_count == 0

    def test_process_view_continues_on_none(self):
        app = FrescoApp()
        view = Mock(return_value=Response())
        app.route('/', GET, view)

        @app.process_view
        def process_view(request, v, args, kwargs):
            assert v is view
            return None

        with app.requestcontext('/'):
            app.view()
            assert view.call_count == 1

    def test_process_view_replaces_view(self):
        app = FrescoApp()
        view = Mock(return_value=Response())
        view2 = Mock(return_value=Response())
        app.route('/', GET, view)

        @app.process_view
        def process_view(request, v, args, kwargs):
            assert v is view
            return view2

        with app.requestcontext('/'):
            app.view()
            assert view.call_count == 0
            assert view2.call_count == 1

    def test_process_view_replaces_response(self):
        app = FrescoApp()
        new_response = Response()
        view = Mock(return_value=Response())
        app.route('/', GET, view)

        @app.process_view
        def process_view(request, v, args, kwargs):
            assert v is view
            return new_response

        with app.requestcontext('/'):
            assert app.view() is new_response
            assert view.call_count == 0

    def test_process_response_continues_on_none(self):
        app = FrescoApp()
        response = Response()
        view = Mock(return_value=response)
        app.route('/', GET, view)

        @app.process_response
        def process_response(req, res):
            assert res is response
            return None

        with app.requestcontext('/'):
            assert app.view() is response

    def test_process_response_replaces_response(self):
        app = FrescoApp()
        new_response = Response()
        view = Mock(return_value=Response())
        app.route('/', GET, view)

        @app.process_response
        def process_response(req, res):
            return new_response

        with app.requestcontext('/'):
            assert app.view() is new_response

    def test_process_http_error_response_continues_on_none(self):
        app = FrescoApp()
        response = Response.not_found()
        view = Mock(return_value=response)
        app.route('/', GET, view)

        @app.process_http_error_response
        def process_http_error_response(req, res):
            return None

        with app.requestcontext('/'):
            assert app.view() is response

    def test_process_http_error_response_replaces_response(self):
        app = FrescoApp()
        new_response = Response()
        view = Mock(return_value=Response.not_found())
        app.route('/', GET, view)

        @app.process_http_error_response
        def process_http_error_response(req, res):
            return new_response

        with app.requestcontext('/'):
            assert app.view() is new_response

    def test_process_http_error_response_called_on_internal_errors(self):
        app = FrescoApp()
        new_response = Response()
        view = Mock(return_value=Response())
        app.route('/', GET, view)

        hook = Mock(return_value=new_response)
        app.process_http_error_response(hook)

        # POSTing to a GET route should generate 405 method not supported
        with app.requestcontext_post('/'):
            assert app.view() is new_response
            hook_args, hook_kwargs = hook.call_args
            assert hook_args[1].status_code == 405

        # Should generate a 404 not found
        with app.requestcontext_post('/asdf'):
            assert app.view() is new_response
            hook_args, hook_kwargs = hook.call_args
            assert hook_args[1].status_code == 404

    def test_process_http_error_response_not_called_on_success(self):
        app = FrescoApp()
        ok_response = Response([''], status='200 OK')
        redirect_response = Response([''], status='302 Found', location='/')
        ok_view = Mock(return_value=ok_response)
        redirect_view = Mock(return_value=redirect_response)
        app.route('/ok', GET, ok_view)
        app.route('/redirect', GET, redirect_view)

        @app.process_http_error_response
        def process_http_error_response(req, res):
            assert False, "Hook should not be called"

        with app.requestcontext('/ok'):
            assert app.view() is ok_response

        with app.requestcontext('/redirect'):
            assert app.view() is redirect_response

    def test_process_http_error_response_can_be_associated_with_status(self):
        app = FrescoApp()
        process_404 = Mock(return_value=None)
        process_500 = Mock(return_value=None)
        app.route('/404', GET, Response.not_found)
        app.route('/500', GET, Response.internal_server_error)

        app.process_http_error_response(404)(process_404)
        app.process_http_error_response(500)(process_500)

        with app.requestcontext('/404'):
            app.view()
            assert process_500.call_count == 0
            assert process_404.call_count == 1

        with app.requestcontext('/500'):
            app.view()
            assert process_500.call_count == 1
            assert process_404.call_count == 1

    def test_process_teardown_called_on_teardown(self):
        app = FrescoApp()
        fn = Mock()
        app.process_teardown(fn)
        with app.requestcontext('/'):
            app.view()
            assert fn.call_count == 0
        assert fn.call_count == 1

    def test_adding_process_teardown_raises_error_after_app_starts(self):
        app = FrescoApp()
        with app.requestcontext('/') as c:
            iterator = app(c.request.environ, Mock())
            iterator.close()
        with pytest.raises(Exception):
            app.process_teardown(Mock())

    def test_exception_in_process_hooks_do_not_stop_processing(self):

        for hook, view in [('process_request', Response),
                           ('process_view', Response),
                           ('process_response', Response),
                           ('process_exception',
                            Mock(side_effect=CustomException())),
                           ('process_http_error_response', Response.not_found),
                           ('process_teardown', Response)]:
            faulty_hook = Mock(side_effect=CustomException())
            process_teardown = Mock(return_value=None)

            app = FrescoApp()
            app.route('/', GET, view)
            getattr(app, hook)(faulty_hook)
            app.process_teardown(process_teardown)

            with app.requestcontext('/'):
                app.view()

            assert faulty_hook.call_count == 1, hook
            assert process_teardown.call_count == 1

    def test_it_raises_exception_in_route_resolution(self):

        from fresco.routing import register_converter, StrConverter

        @register_converter('bugs')
        class Converter(StrConverter):
            def from_string(self, s):
                raise AssertionError("Oops!")

        app = FrescoApp()
        app.route('/<x:bugs>', GET=lambda: Response)
        with app.requestcontext('/abc'):
            with pytest.raises(AssertionError):
                app.view()


class TestProcessException(object):

    def exception_view(self):
        raise CustomException()

    def iterator_exception_view(self):
        def content_iterator():
            yield b'fish'
            raise CustomException()
            yield b'chips'
        return Response(content_iterator())

    def test_it_reraises_if_no_error_handlers_installed(self):
        app = FrescoApp()

        app.route('/', GET, self.exception_view)
        with app.requestcontext('/'):
            with pytest.raises(CustomException):
                app.view()

    def test_it_reraises_if_no_500_error_handler_installed(self):

        app = FrescoApp()
        app.process_http_error_response(lambda req, res: None, 404)

        app.route('/', GET, self.exception_view)
        with app.requestcontext('/'):
            with pytest.raises(CustomException):
                app.view()

    def test_it_calls_process_exception_handlers(self):
        app = FrescoApp()

        app.route('/', GET, self.exception_view)
        new_response = Response()
        process_exception = Mock(return_value=new_response)
        app.process_exception(process_exception)

        with app.requestcontext('/'):
            assert app.view() is new_response
            assert process_exception.call_count == 1

    def test_it_returns_first_not_none_process_exception_handler(self):
        app = FrescoApp()

        app.route('/', GET, self.exception_view)
        new_response1 = Response()
        new_response2 = Response()
        process_exception1 = Mock(return_value=None)
        process_exception2 = Mock(return_value=new_response1)
        process_exception3 = Mock(return_value=new_response2)
        app.process_exception(process_exception1)
        app.process_exception(process_exception2)
        app.process_exception(process_exception3)

        with app.requestcontext('/'):
            assert app.view() is new_response1
            assert process_exception1.call_count == 1
            assert process_exception2.call_count == 1
            assert process_exception3.call_count == 0

    def test_it_calls_process_exception_handlers_in_content_iteration(self):
        app = FrescoApp()

        app.route('/', GET, self.iterator_exception_view)
        process_exception = Mock(return_value=None)
        app.process_exception(process_exception)

        with app.requestcontext('/') as c:
            content_iterator = app(c.request.environ, Mock())
            assert process_exception.call_count == 0
            list(content_iterator)
            assert process_exception.call_count == 1

    def test_it_reraises_when_exc_info_returned(self):
        app = FrescoApp()

        app.route('/', GET, self.exception_view)
        app.process_exception(lambda req, exc_info: exc_info)

        with app.requestcontext('/'):
            with pytest.raises(CustomException):
                app.view()

    def test_it_calls_error_handlers_in_middleware(self):
        """
        If a faulty middleware layer raises an exception it should
        trigger error handling.
        """
        def faulty_middleware(app):
            def middleware(environ, start_response):
                raise CustomException()
            return middleware

        app = FrescoApp([Route('/', GET, lambda: Response("foo"))])
        app.add_middleware(faulty_middleware)
        process_exception = Mock(return_value=None)
        app.process_exception(process_exception)
        process_http_error_response = Mock(return_value=Response(b"bar"))
        app.process_http_error_response(process_http_error_response, 500)

        content = list(app(make_environ(), Mock()))
        assert process_exception.call_count == 1
        assert process_http_error_response.call_count == 1
        assert content == [b'bar']

    def test_it_associates_with_given_exception(self):

        def exception_view():
            raise ValueError()

        app = FrescoApp()
        app.route('/', GET, exception_view)
        process_TypeError = Mock(return_value=None)
        process_ValueError = Mock(return_value=None)
        app.process_exception(TypeError)(process_TypeError)
        app.process_exception(ValueError)(process_ValueError)

        with app.requestcontext('/'):
            app.view()
            assert process_TypeError.call_count == 0
            assert process_ValueError.call_count == 1

    def test_it_calls_http_error_handler(self):
        app = FrescoApp()

        app.route('/', GET, self.exception_view)
        new_response = Response()
        process_http_error_response = Mock(return_value=new_response)
        app.process_http_error_response(process_http_error_response)

        with app.requestcontext('/'):
            assert app.view() is new_response
            assert process_http_error_response.call_count == 1
            req, res = process_http_error_response.call_args[0]
            assert res.status_code == 500


class TestIncludeApp(object):

    def test_it_routes_to_an_included_app(self):

        app = FrescoApp()

        @app.route('/', GET)
        def view():
            return Response([b'ok'])

        app2 = FrescoApp()
        app2.include('/app1', app)

        with app2.requestcontext('/'):
            assert app2.view().status_code == 404

        with app2.requestcontext('/app1/'):
            assert list(app2.view().content_iterator) == [b'ok']

    def test_included_app_can_use_urlfor(self):

        def view():
            url = urlfor(view)
            return Response(url)

        app = FrescoApp()
        app.route('/', GET, view)
        app2 = FrescoApp()
        app2.include('/app1', app)

        with app2.requestcontext('/app1/'):
            assert list(app2.view().content_iterator) == \
                    [b'http://localhost/app1/']


class TestTrailingSlashes(object):
    """\
    The general principle is that if a GET or HEAD request is received for a
    URL without a trailing slash and no match is found, the app will look for a
    URL with a trailing slash, and redirect the client if such a route exists.
    """

    def test_no_trailing_slash(self):

        def foo():
            return Response(['foo'])

        app = FrescoApp()
        app.route('/foo/', GET, foo)

        with app.requestcontext('/foo'):
            assert app.view().status_code == 301
            assert app.view().get_header('location') == 'http://localhost/foo/'


class TestViewCollection(object):

    def test_appdef(self):

        app = FrescoApp()
        app.include('/', fixtures.CBV('bananas!'))
        with app.requestcontext('/'):
            assert list(app.view().content_iterator) == [b'bananas!']

    def test_appdef_url_generation(self):

        foo = fixtures.CBV('foo!')
        bar = fixtures.CBV('bar!')
        baz = fixtures.CBV('baz!')

        app = FrescoApp(views=foo)
        app.include('/bar', bar)
        app.include('/baz', baz)

        with app.requestcontext():
            assert urlfor(foo.index_html) == 'http://localhost/'
            assert urlfor(bar.index_html) == 'http://localhost/bar/'
            assert urlfor(baz.index_html) == 'http://localhost/baz/'

    def test_instance_available_in_context(self):

        s = []

        class MyCBV(fixtures.CBV):

            def index_html(self):
                from fresco import context
                s.append(context.view_self)
                return Response([])

        instance = MyCBV('foo!')
        app = FrescoApp(views=instance)

        with app.requestcontext('/'):
            app.view()
            assert s[0] is instance


class TestContextAttributes(object):

    def test_app_is_set(self):

        def check_app(expected):
            assert context.app is expected
            return Response([])

        app1 = FrescoApp()
        app2 = FrescoApp()

        app1.route('/', GET, check_app, {'expected': app1})
        app2.route('/', GET, check_app, {'expected': app2})

        with app1.requestcontext('/'):
            app1.view()

        with app2.requestcontext('/'):
            app2.view()


class TestAppRequestContext(object):

    def _middleware(self, app):
        def middleware(environ, start_response):
            environ['sausages'] = 1
            return app(environ, start_response)
        return middleware

    def test_creates_isolated_context(self):

        app = FrescoApp()
        with app.requestcontext():
            context.request = 'foo'

            with app.requestcontext():
                context.request = 'bar'
                assert context.request == 'bar'

            assert context.request == 'foo'

    def test_parses_full_url(self):

        with FrescoApp().requestcontext('https://arthur@example.org:123/?x=y'):
            assert context.request.environ['HTTPS'] == 'on'
            assert context.request.environ['REMOTE_USER'] == 'arthur'
            assert context.request.environ['HTTP_HOST'] == 'example.org:123'
            assert context.request.environ['SCRIPT_NAME'] == ''
            assert context.request.environ['PATH_INFO'] == '/'
            assert context.request.environ['QUERY_STRING'] == 'x=y'

    def test_it_posts_data(self):
        with FrescoApp().requestcontext_post(data={'foo': 'bar'}) as c:
            assert c.request.method == 'POST'
            assert list(c.request.form.allitems()) == [('foo', 'bar')]
            assert list(c.request.query.allitems()) == []

    def test_it_puts_data(self):
        with FrescoApp().requestcontext_put(data={'foo': 'bar'}) as c:
            assert c.request.method == 'PUT'
            assert list(c.request.form.allitems()) == [('foo', 'bar')]

    def test_it_posts_data_multipart(self):
        with FrescoApp().requestcontext_post(
                files=[('foo', 'foo.txt', 'text/plain', b'bar')]) as c:
            assert c.request.files['foo'].filename == 'foo.txt'
            assert c.request.files['foo'].file.read() == b'bar'

    def test_it_posts_raw_data(self):
        with FrescoApp().requestcontext_post(data=b'xyzzy',
                                             content_type='text/spell') as c:
            assert c.request.body == 'xyzzy'

    def test_it_converts_header_names(self):
        with FrescoApp().requestcontext(user_agent='foo'):
            assert context.request.environ['HTTP_USER_AGENT'] == 'foo'

    def test_it_converts_wsgi_keys(self):
        # CONTENT_TYPE is both a WSGI core environ key and a standard request
        # header. The WSGI key must win.
        with FrescoApp().requestcontext(content_type='foo'):
            assert context.request.environ['CONTENT_TYPE'] == 'foo'

    def test_it_invokes_middleware(self):

        app = FrescoApp()
        app.add_middleware(self._middleware)
        with app.requestcontext() as c:
            assert 'sausages' in c.request.environ

    def test_it_skips_middleware(self):

        app = FrescoApp()
        app.add_middleware(self._middleware)
        with app.requestcontext(middleware=False) as c:
            assert 'sausages' not in c.request.environ

    def test_it_closes_middleware(self):

        close = Mock()

        def middleware(app):
            def middleware(environ, start_response):
                return ClosingIterator(app(environ, start_response), close)
            return middleware

        app = FrescoApp()
        app.add_middleware(middleware)
        with app.requestcontext():
            pass
        assert close.call_count == 1

    def test_it_calls_first_iteration(self):
        """
        Some middleware waits until the first iteration to do things, so make
        sure we trigger this
        """
        from itertools import count
        counter = count()

        def middleware(app):
            def middleware(environ, start_response):
                iterator = app(environ, start_response)
                for item in iterator:
                    yield next(counter)
            return middleware

        app = FrescoApp()
        app.add_middleware(middleware)
        with app.requestcontext():
            assert next(counter) == 1

    def test_it_calls_late_added_middleware(self):

        calls = []

        def middleware(app):
            calls.append('middleware initialized')

            def middleware(env, start_response):
                calls.append('middleware called')
                return app(env, start_response)
            return middleware

        app = FrescoApp()
        app.route('/', GET, lambda: Response())

        # Put a request through app to initialize the WSGI stack
        with app.requestcontext('/'):
            app.view()

        app.add_middleware(middleware)

        # The request should cause the WSGI app to be rebuilt with the new
        # middleware included
        with app.requestcontext('/'):
            app.view()

        assert calls == ['middleware initialized', 'middleware called']

    def test_it_passes_a_valid_start_response_to_middleware(self):

        calls = []

        def middleware(app):
            def middleware(env, start_response):
                calls.append('middleware called')
                write = start_response('200 OK', [])
                assert callable(write)
                return app(env, lambda *a, **k: lambda s: None)
            return middleware

        app = FrescoApp()
        app.add_middleware(middleware)
        app.route('/', GET, lambda: Response())

        with app.requestcontext('/'):
            app.view()

        assert calls == ['middleware called']


class TestUrlfor(object):

    def test_urlfor_on_aliased_functions(self):

        view = lambda: None
        setattr(fixtures, 'aliased_view', view)

        app = FrescoApp()
        app.route('/', GET, view)
        with app.requestcontext():
            assert urlfor(view) == 'http://localhost/'
            assert urlfor('fresco.tests.fixtures.aliased_view') == \
                    'http://localhost/'

        delattr(fixtures, 'aliased_view')

    def test_urlfor_with_view_function(self):

        def view():
            return Response(['ok'])

        app = FrescoApp()
        app.route('/foo', GET, view)
        with app.requestcontext():
            assert urlfor(view) == 'http://localhost/foo'

    def test_urlfor_allows_script_name(self):

        def view():
            return Response(['ok'])

        app = FrescoApp()
        app.route('/foo', GET, view)
        with app.requestcontext():
            assert urlfor(view, _script_name='/abc') ==\
                    'http://localhost/abc/foo'

    def test_urlfor_with_string(self):
        app = FrescoApp()
        app.route('/myviewfunc', GET, fixtures.module_level_function)
        with app.requestcontext():
            assert urlfor('fresco.tests.fixtures.module_level_function') ==\
                    'http://localhost/myviewfunc'

    def test_urlfor_drops_query(self):
        myviewfunc = lambda req: Response([])
        app = FrescoApp()
        app.route('/', GET, myviewfunc)
        with app.requestcontext():
            assert urlfor(myviewfunc) == 'http://localhost/'

    def test_urlfor_generates_first_route(self):

        myviewfunc = lambda req: Response([])
        app = FrescoApp()
        app.route('/1', GET, myviewfunc)
        app.route('/2', GET, myviewfunc)
        with app.requestcontext():
            assert urlfor(myviewfunc) == 'http://localhost/1'

    def test_urlfor_with_class_based_view_spec(self):

        app = FrescoApp()
        app.include('/foo', fixtures.CBV('x'))
        with app.requestcontext():
            assert urlfor('fresco.tests.fixtures.CBV.index_html') == \
                        'http://localhost/foo/'

    def test_it_uses_values_from_path_defaults(self):
        app = FrescoApp()
        app.route('/<test:int>', GET, lambda: None,
                  name='test', test_default=1)
        with app.requestcontext():
            assert urlfor('test') == 'http://localhost/1'

    def test_it_uses_callable_values_from_path_defaults(self):
        generate_value = Mock(return_value=1)
        app = FrescoApp()
        app.route('/<test:int>', GET, lambda: None,
                  name='test', test_default=generate_value)
        with app.requestcontext() as c:
            assert urlfor('test') == 'http://localhost/1'
            assert generate_value.call_args_list == [call(c.request)]

    def test_path_defaults_removed_from_view_kwargs(self):
        app = FrescoApp()
        view = Mock(return_value=Response())
        app.route('/<test:int>', GET, view,
                  name='test', test_default=1)
        with app.requestcontext('/2'):
            app.view()
            assert view.call_args_list == [call(test=2)]
