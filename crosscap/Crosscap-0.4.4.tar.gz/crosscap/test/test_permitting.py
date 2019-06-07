# coding: utf-8
"""
Confirmation of the permitting API
"""
from datetime import datetime
import time

from builtins import object

import jwt

from twisted.python import components
from twisted.web.test.requesthelper import DummyRequest

from pytest import fixture, mark, raises

from mock import Mock

from crosscap import permitting
from crosscap.testing import request as ctrequest


ADMIN = 'admin'
BILLING_CONTACT = 'billing'
SECRET = 'q354809hreuinjvm '

MARIO_BROS = ('mario', 'luigi')

Y = "authenticated"
N = "FORBIDDEN"


class AuthUser(object):
    def __init__(self, req):
        self.req = req
    
    def authenticated(self, user):
        return Y

    def forbidden(self):
        return N

    def authenticate(self):
        return self.req.user and self.req.user.userID in MARIO_BROS

    @property
    def roles(self):
        return self.req.user.roles

components.registerAdapter(AuthUser, DummyRequest, permitting.ICurrentUser)


@fixture
def u_admin():
    """
    An instance of authuser with some roles
    """
    return Mock(roles=[ADMIN], userID='luigi')


@fixture
def u_user():
    """
    An instance of authuser with no roles
    """
    return Mock(roles=[], userID='mario')


@fixture
def u_hacker():
    """
    A user we don't recognize, trying to hack his way in
    """
    return Mock(roles=['waaa'], userID='waluigi')


def test_role_in(u_admin, u_user):
    """
    Do I check roles correctly for users?
    """
    assert not permitting.role_in([])(u_user)
    assert not permitting.role_in([])(u_admin)
    assert not permitting.role_in([ADMIN])(u_user)
    assert permitting.role_in([ADMIN])(u_admin)
    assert permitting.role_in([ADMIN, BILLING_CONTACT])(u_admin)


def test_create_timed_token():
    """
    Do I generate a sensible output or error for various calls
    """
    exp = int(time.time() + permitting.core.JWT_DURATION)

    # no duration
    tok1 = permitting.create_timed_token('myuser', SECRET, duration=None)
    assert jwt.decode(tok1, SECRET, algorithms=permitting.core.JWT_ALGO) == {'sub': 'myuser'}

    # default duration
    tok2 = permitting.create_timed_token('myuser', SECRET)
    assert jwt.decode(tok2, SECRET, algorithms=permitting.core.JWT_ALGO) == {'sub': 'myuser', 'exp': exp}

    # different algorithm
    tok3 = permitting.create_timed_token('myuser', SECRET, algorithm='HS512')
    assert jwt.decode(tok3, SECRET, algorithms=['HS512']) == {'sub': 'myuser', 'exp': exp}

    # missing SECRET
    with raises(TypeError):
        permitting.create_timed_token('myuser', '')

    # missing sub
    with raises(TypeError):
        permitting.create_timed_token('', SECRET)


def test_validate_token():
    """
    Do valid tokens pass our validator function? Also invalid tokens, not pass
    """
    sub = 'myuser'

    # token without an expiration, so it should validate
    tok1 = b'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJteXVzZXIifQ.4agU_-BTje86l4JtbRdvLwTI9cHgKJ0Asg-hftuZUEM'
    assert permitting.validate_token(tok1, SECRET)['sub'] == sub

    # token we created, with default expiration of 10 minutes
    tok2 = permitting.create_timed_token(sub, SECRET)
    payload2 = permitting.validate_token(tok2, SECRET)
    assert payload2['sub'] == sub
    assert 'exp' in payload2

    # expired token (no default, raise an exception)
    tok3 = jwt.encode({'sub': sub, 'exp': datetime(year=1970, month=1, day=1)}, SECRET, algorithm='HS256')
    with raises(jwt.exceptions.ExpiredSignatureError):
        permitting.validate_token(tok3, SECRET)

    _my_default = object()

    # malformed token, with a default
    tok2x = tok2[:-2]
    assert permitting.validate_token(tok2x, SECRET, _my_default) is _my_default

    # correct token, incorrect secret
    secretx = SECRET[:-2]
    assert permitting.validate_token(tok2, secretx, _my_default) is _my_default

    # token is None
    assert permitting.validate_token(None, SECRET, _my_default) is _my_default


def test_extract_bearer_token():
    """
    Do I parse an authorization header with a bearer token correctly, returning just the token
    """
    good_val = "bearer skdjfh"
    assert permitting.extract_bearer_token(good_val) == "skdjfh"
    good_val2 = "beAreR  skdjfh"
    assert permitting.extract_bearer_token(good_val2) == "skdjfh"
    good_val3 = "bearer skdj fh"
    assert permitting.extract_bearer_token(good_val3) == "skdj"
    bad_val = "bear 🐻 raar"
    assert permitting.extract_bearer_token(bad_val) is None

    with raises(TypeError):
        permitting.extract_bearer_token(None)

    with raises(TypeError):
        permitting.extract_bearer_token('')


@mark.parametrize("who,role_in,expect", [
    # u_admin accesses a public resource
    ["u_admin", None, Y],

    # u_admin accesses a logged-in resource
    ["u_admin", [], Y],

    # u_admin accesses an admin resource
    ["u_admin", ["admin", "billing"], Y],

    # u_admin tries to access a billing-only resource
    ["u_admin", ["billing"], N],

    # u_user accesses a public resource
    ["u_user", None, Y],

    # u_user accesses a logged-in resource
    ["u_user", [], Y],

    # u_user tries to access an admin resource
    ["u_user", ["admin", "billing"], N],

    # u_hacker tries to access a logged-in resource
    ["u_hacker", [], N],

    # anonymous user accesses a public resource
    [None, None, Y],

    # anonymous user tries to access a logged-in resource
    [None, [], N],

    # anonymous user tries to access an admin resource
    [None, ["admin", "billing"], N],
    ])
def test_permits_fn(request, who, role_in, expect):
    """
    Do functions decorated with me do the required action (forbid or allow)

    Note: permits() doesn't actually require you to implement the concept of tokens, so we
    have no assertions here for various invalid token conditions, these should be covered
    by the tests of create_timed_token and validate_token.
    """
    who = request.getfixturevalue(who) if who else None

    # None means no `permits' decorator at all, this is accessible to everyone
    if role_in is None:
        decorator = lambda fn: fn

    # [] means a logged-in user is required, but no role checks
    elif role_in == []:
        decorator = permitting.permits()

    else:
        decorator = permitting.permits(permitting.role_in(role_in))

    @decorator
    def handler(req):
        return Y

    req = ctrequest([])
    req.user = who

    assert handler(req) == expect


def test_permits_tornadolike(u_user):
    """
    Does permits use the right object for the request handler when it's in the instance `self' argument, instead of a non-method argument
    """
    class MyPage(object):
        user = u_user

        @permitting.permits()
        def handler(self):
            return Y

        def write(self, s): # pragma: nocover
            "no-op for this test"

    components.registerAdapter(AuthUser, MyPage, permitting.ICurrentUser)

    pg = MyPage()
    assert pg.handler() == Y


def test_permits_badfunction():
    """
    Do I raise an appropriate exception when the decorator is used on something inappropriate?
    """
    @permitting.permits()
    def handler(): # pragma: nocover
        return Y

    with raises(TypeError):
        handler()
