# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

from django.http import HttpResponse

from tcell_agent.agent import TCellAgent
from tcell_agent.policies.policy_types import PolicyTypes
from tcell_agent.instrumentation.djangoinst.appfirewall import inspect_request_response
from tcell_agent.instrumentation.djangoinst.meta import get_appsensor_meta
from tcell_agent.instrumentation.decorators import catches_generic_exception
from tcell_agent.instrumentation.djangoinst.routes import make_route_table, get_route_id
from tcell_agent.routes.routes_sender import ensure_routes_sent


@catches_generic_exception(__name__, "Error assiging route ID to route")
def assign_route_id(request):
    if request._tcell_context.route_id is None:
        request._tcell_context.route_id = get_route_id(request)


@catches_generic_exception(__name__, "Error assiging path parameters")
def assign_path_dictionary_for_request(request, path_dict):
    appfirewall_policy = TCellAgent.get_policy(PolicyTypes.APPSENSOR)
    if appfirewall_policy.appfirewall_enabled:
        meta = get_appsensor_meta(request)
        meta.path_parameters_data(path_dict)


class TCellLastMiddleware(object):

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)

        response = self.get_response(request)

        return self.process_response(request, response)

    def process_request(self, _request):  # pylint: disable=no-self-use
        # Note: It's important this happens in this middleware because this
        #       middleware is the last to execute during an app request.
        #       If this happens in an earlier middleware the customer's app
        #       may still not be fully loaded. Route reporting will load
        #       a customer's urls.py file which in turns loads a big portion
        #       of the user's app. This can lead to cyclical dependency issues
        #       that may only appear when tcell-agent is present.
        ensure_routes_sent(make_route_table)

    def process_view(self, request, view_func, view_args, view_kwargs):  # pylint: disable=unused-argument,no-self-use
        assign_route_id(request)

        if view_kwargs:
            assign_path_dictionary_for_request(request, view_kwargs)

        return None

    def process_template_response(self, request, response):  # pylint: disable=no-self-use
        assign_route_id(request)
        return response

    def process_response(self, request, response):  # pylint: disable=no-self-use
        assign_route_id(request)
        inspect_request_response(HttpResponse, request, response)
        return response
