from __future__ import absolute_import

import functools
from ...responses import UnauthorizedResponse, ForbiddenResponse


def login_required(func):
    @functools.wraps(func)
    def wrapped(request, *args, **kw):
        if not request.user.is_authenticated():
            return UnauthorizedResponse(request)
        return func(request, *args, **kw)
    return wrapped


def staff_member_required(func):
    @functools.wraps(func)
    @login_required
    def wrapped(request, *args, **kw):
        if not request.user.is_staff:
            return ForbiddenResponse(request)
        return func(request, *args, **kw)
    return wrapped
