# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

from tcell_agent.instrumentation.decorators import catches_generic_exception


@catches_generic_exception(__name__, "Error adding user and session to tcell context")
def add_user_and_session(request):
    try:
        if hasattr(request, "user") and request.user.is_authenticated() and request.user.id:
            uid = request.user.id
            if uid is not None:
                uid = str(uid)
            request._tcell_context.user_id = uid
    except Exception:
        pass

    if hasattr(request, "session") and hasattr(request.session, "session_key"):
        request._tcell_context.session_id = request.session.session_key


class AfterAuthMiddleware(object):

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)

        return self.get_response(request)

    def process_request(self, request):  # pylint: disable=no-self-use
        add_user_and_session(request)
