# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

import threading

from django.http import HttpResponse


from tcell_agent.instrumentation.decorators import catches_generic_exception
from tcell_agent.instrumentation.djangoinst.blocking import check_patches_blocking
from tcell_agent.instrumentation.djangoinst.check_agent_startup import ensure_agent_started
from tcell_agent.instrumentation.djangoinst.headers import django_add_headers
from tcell_agent.instrumentation.djangoinst.meta import initialize_tcell_context
from tcell_agent.instrumentation.djangoinst.redirects import check_location_redirect


@catches_generic_exception(__name__, "Error running filters")
def run_filters(request, response):
    if isinstance(response, HttpResponse):
        response.content = request._tcell_context.filter_body(response.content)


class GlobalRequestMiddleware(object):
    _threadmap = {}

    def __init__(self, get_response=None):
        self.get_response = get_response

    # With respect to patches blocking, if a request should be blocked, an
    # HttpResponseForbidden needs to be return during the request phase
    # of the Django middleware.
    #
    # Appropriately returning an http response during the request phase
    # differs depending on Django's version as follows:
    #
    # __call__ method only exists in Django 1.10+ and is the only one that can
    # return an http response for Django 1.10+. Returning an http response
    # from process_request in Django 1.10+ will do nothing
    #
    # For Django < 1.10, process_request is the method in charge of returning
    # an http response, so returning an http response there will be
    # respected (__call__ method never gets called in Django < 1.10)
    #
    # This is the reason why both __call__ and process_request return a
    # block_response when appropriate
    def __call__(self, request):
        block_response = self.process_request(request)

        if block_response:
            return block_response

        response = self.get_response(request)
        return self.process_response(request, response)

    @classmethod
    def get_current_request(cls):
        try:
            return cls._threadmap[threading.current_thread().ident]
        except Exception:
            pass

    def process_request(self, request):
        ensure_agent_started()

        request._tcell_signals = {}

        initialize_tcell_context(request)

        self._threadmap[threading.current_thread().ident] = request

        block_response = check_patches_blocking(request)
        if block_response:
            return block_response

        return None

    def process_exception(self, _request, _exception):
        try:
            del self._threadmap[threading.current_thread().ident]
        except KeyError:
            pass

    def process_response(self, request, response):
        check_location_redirect(request, response)
        django_add_headers(request, response)
        run_filters(request, response)
        try:
            del self._threadmap[threading.current_thread().ident]
        except KeyError:
            pass
        return response
