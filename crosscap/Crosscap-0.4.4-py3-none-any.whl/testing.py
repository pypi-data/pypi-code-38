"""
Tools for testing applications that use crosscap
"""
from builtins import object

from twisted.internet import defer
from twisted.web.test.requesthelper import DummyRequest as _DummyRequest

import attr


DEFAULT_HEADERS = (
    ('user-agent', ['Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0)']),
    ('cookie', ['']),
    )


class DummyRequest(_DummyRequest):
    """
    Patch a weird bug in twisted's _DummyRequest - it doesn't set .code, it sets .responseCode
    """
    def setResponseCode(self, code, message=None):
        _DummyRequest.setResponseCode(self, code, message)
        self.code = code


def request(postpath, requestHeaders=DEFAULT_HEADERS, responseHeaders=(), **kwargs):
    """
    Build a fake request for tests
    """
    req = DummyRequest(postpath)
    req.setResponseCode(200)
    for hdr, val in requestHeaders:
        req.requestHeaders.setRawHeaders(hdr, val)

    for hdr, val in responseHeaders:
        req.setHeader(hdr, val)

    for k, v in list(kwargs.items()):
        if k.startswith('session_'):
            ses = req.getSession()
            setattr(ses, k[8:], v)
        else:
            setattr(req, k, v)

    return req


@attr.s(init=False)
class EZServer(object):
    """
    Convenience abstraction over Server/APIServer to simplify test code
    """
    cls = attr.ib()
    inst = attr.ib(default=None)

    def __init__(self, cls):
        self.cls = cls
        self.inst = cls()

    def handler(self, handlerName, req=None, *a, **kw):
        """
        Convenience method, call a Server.app endpoint with a request
        """
        if req is None:
            # postpath is empty by default because we're directly executing the
            # endpoint, so there should be nothing left to consume in the url
            # path. In other words, we've already found the final resource when
            # execute_endpoint is called.
            postpath = kw.pop('postpath', [])
            req = request(postpath)

        d = defer.maybeDeferred(
                self.inst.app.execute_endpoint,
                handlerName, req, *a, **kw
                )
        return d
