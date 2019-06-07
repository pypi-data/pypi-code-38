"""
Tests of the testing-helpers. :-/
"""
from builtins import object

from twisted.web.http_headers import Headers

from klein import Klein

from pytest import fixture, inlineCallbacks

from crosscap import testing


@fixture
def srv():
    """
    A server built with klein, for testing tools that test servers built with klein
    """
    class AServer(object):
        app = Klein()

        @app.route('/hello')
        def hello(self, request):
            return 123

    return testing.EZServer(AServer)


@inlineCallbacks
def test_handler(srv):
    """
    Call a handler on the test server with the handler() helper, assert that the route returns its value
    """
    res = yield srv.handler("hello")
    assert res == 123


def test_request(srv):
    """
    Test various ways to construct a request
    """
    req = testing.request([], requestAttr=True)
    assert req.requestAttr
    req = testing.request([], session_attr=True)
    assert req.session.attr
    rh = {'Accept-Language': 'klingon'}
    req = testing.request([], responseHeaders=list(rh.items()))
    assert req.responseHeaders == Headers({'accept-language': ['klingon']})
    assert req.code == 200
