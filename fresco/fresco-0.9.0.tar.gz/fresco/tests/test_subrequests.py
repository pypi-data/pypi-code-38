# encoding: UTF-8
from fresco import FrescoApp, GET, Route, Response
from fresco.routeargs import GetArg, routearg
from fresco.subrequests import subrequest, subrequest_raw, subrequest_bytes

from mock import Mock
import pytest


class TestSubRequest(object):

    def test_it_raises_exception_if_decoding_impossible(self):

        def view_bytes():
            return Response(b'caf\xe9', content_type='text/plain')

        with FrescoApp().requestcontext():
            with pytest.raises(ValueError):
                subrequest(view_bytes)

    def test_it_decodes_response_content(self):

        def view_latin1():
            return Response(u'café'.encode('latin1'),
                            content_type='text/plain; charset=Latin-1')

        def view_utf8():
            return Response(u'café'.encode('UTF-8'),
                            content_type='text/plain; charset=UTF-8')

        def view_string():
            return Response(u'café', content_type='text/plain; charset=UTF-8')

        def view_list_of_strings():
            return Response([u'café'],
                            content_type='text/plain; charset=UTF-8')

        with FrescoApp().requestcontext():
            assert subrequest(view_utf8) == u'café'
            assert subrequest(view_latin1) == u'café'
            assert subrequest(view_string) == u'café'
            assert subrequest(view_list_of_strings) == u'café'

    def test_it_returns_a_markup_string(self):

        def view_html():
            return Response(u'<html>',
                            content_type='text/html; charset=UTF-8')

        def view_text():
            return Response(u'text',
                            content_type='text/plain; charset=UTF-8')

        with FrescoApp().requestcontext():
            assert hasattr(subrequest(view_html), '__html__')
            assert not hasattr(subrequest(view_text), '__html__')

    def test_it_returns_raw_response(self):
        r = Response('foo')
        with FrescoApp().requestcontext():
            assert subrequest_raw(lambda: r) is r

    def test_it_returns_content_as_bytes(self):
        view = lambda: Response(u'café'.encode('latin1'),
                                content_type='text/plain; charset=Latin-1')
        with FrescoApp().requestcontext():
            assert subrequest_bytes(view) == b'caf\xe9'

    def test_it_calls_response_onclose(self):
        m = Mock()
        r = Response(onclose=m)
        with FrescoApp().requestcontext():
            assert subrequest(lambda: r) == u''
        assert m.call_count == 1

    def test_viewspec_resolves(self):
        def view():
            return Response('foo')

        app = FrescoApp()
        app.route('/view', GET, view, name='named view')
        with app.requestcontext():
            assert subrequest('named view') == 'foo'

    def test_viewspec_uses_routeargs(self):

        def view(a, b):
            return Response(['*' + a + b + '*'])

        app = FrescoApp()
        app.route('/view', GET, view,
                  a=GetArg(),
                  b=routearg(lambda r: r.method))

        with app.requestcontext('/view?a=foo'):
            assert subrequest(view, _resolve=True) == '*fooGET*'
            assert subrequest(view, _resolve=True, a='bar', b='baz') \
                    == '*barbaz*'

    def test_viewspec_resolves_dynamic(self):

        class Views(object):

            def __init__(self, a):
                self.a = a

            def view(self, b):
                return Response('*' + self.a + b + '*')

            __routes__ = [Route('/<b:str>', GET, 'view', name='named view')]

        app = FrescoApp()
        app.delegate('/<a:str>', Views, dynamic=True, name='named collection')

        with app.requestcontext():
            assert subrequest(
                'named collection:named view', a='foo', b='bar') == '*foobar*'

    def test_it_does_a_full_request(self):

        request_hook = Mock(return_value=None)
        view = Mock(return_value=Response())

        app = FrescoApp()
        app.route('/view', GET, view)
        app.process_request(request_hook)
        with app.requestcontext():
            subrequest(view)
            assert view.call_count == 1
            assert request_hook.call_count == 0

            subrequest(view, _full=True)
            assert view.call_count == 2
            assert request_hook.call_count == 1
