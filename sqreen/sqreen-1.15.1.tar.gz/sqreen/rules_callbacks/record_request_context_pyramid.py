# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Look for known crawlers user-agents
"""
from logging import getLogger

from ..frameworks.pyramid_framework import PyramidRequest, PyramidResponse
from .record_request_context import RecordRequestContext

LOGGER = getLogger(__name__)


class RecordRequestContextPyramid(RecordRequestContext):
    def pre(self, original, request):
        self._store_request(PyramidRequest(request))

    def post(self, *args, **kwargs):
        self.storage.store_response(PyramidResponse(args[1]))
        self._clear_request()
