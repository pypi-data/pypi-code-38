# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Look for known crawlers user-agents
"""
from logging import getLogger

from ..frameworks.django_framework import DjangoRequest, DjangoResponse
from .record_request_context import RecordRequestContext

LOGGER = getLogger(__name__)


class RecordRequestContextDjango(RecordRequestContext):
    def pre(self, original, request, view_func, view_args, view_kwargs):
        self._store_request(
            DjangoRequest(request, view_func, view_args, view_kwargs)
        )

    def post(self, *args, **kwargs):
        self.storage.store_response(DjangoResponse(args[1]))
        self._clear_request()

    @staticmethod
    def failing(*args, **kwargs):
        """ Post is always called in a Django Middleware, don't clean the
        request right now as it may be needed in a post callback
        """
        pass
