# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

from tcell_agent.features.request_timing import start_timer, end_timer


class TimerMiddleware(object):

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)

        response = self.get_response(request)

        return self.process_response(request, response)

    def process_request(self, request):  # pylint: disable=no-self-use
        start_timer(request)

    def process_response(self, request, response):  # pylint: disable=no-self-use
        end_timer(request)
        return response
