# -*- coding: utf-8 -*-
"""
    utils

    :license: see LICENSE for details.
"""
import os
from sentry_sdk import capture_exception
from functools import wraps

from trytond.exceptions import (
    UserError, UserWarning, ConcurrencyException, LoginException)

CONSULTANT = os.environ.get('TRYTON_CONSULTANT', '<CONSULTANT NAME>')


def patch(old_dispatch):
    """
    Patch the `old_dispatcher` with an exception handler to send exceptions
    which occur to sentry

    :param old_dispatch: the function/method to be patched
    """
    @wraps(old_dispatch)
    def wrapper(*args, **kwargs):
        try:
            return old_dispatch(*args, **kwargs)
        except (ConcurrencyException, UserError, UserWarning, LoginException):
            raise
        except Exception:
            event_id = capture_exception()
            raise UserError(
                "Oops! Something terrible happened\n\n"
                "Your ever loving friends at %s have been notified of "
                "this grave fault!\n"
                "However, if you wish to speak with an %s consultant "
                "about this issue, you may use the following reference:\n\n"
                "%s" % (CONSULTANT, CONSULTANT, event_id)
            )
    return wrapper
