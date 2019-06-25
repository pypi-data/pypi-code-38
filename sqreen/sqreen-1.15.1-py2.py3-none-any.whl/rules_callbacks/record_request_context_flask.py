# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Record the current request in flask application
"""
from logging import getLogger

from ..frameworks.flask_framework import FlaskRequest, FlaskResponse
from .record_request_context import RecordRequestContext

LOGGER = getLogger(__name__)


class RecordRequestContextFlask(RecordRequestContext):
    def pre(self, original, *args, **kwargs):
        from flask import request

        self._store_request(FlaskRequest(request))

    def post(self, *args, **kwargs):
        self.storage.store_response(FlaskResponse(args[1]))
        self._clear_request()
