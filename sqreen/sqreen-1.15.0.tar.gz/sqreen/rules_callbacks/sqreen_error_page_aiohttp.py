# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
"""Custom error page for aiohttp."""

from logging import getLogger

from ..exceptions import RequestBlocked
from .headers_insert import convert_to_str
from .sqreen_error_page import BaseSqreenErrorPage

LOGGER = getLogger(__name__)


class SqreenErrorPageAioHTTP(BaseSqreenErrorPage):
    """Custom error page for aiohttp."""

    @staticmethod
    def _get_exception(handler, request, status=500, exc=None, message=None):
        if isinstance(exc, RequestBlocked):
            return exc

    @staticmethod
    def _get_response(exc, content, status_code, headers={}):
        from aiohttp.web_response import Response

        resp = Response(status=status_code, text=content)
        for header_name, header_value in convert_to_str(headers.items()):
            resp.headers[header_name] = header_value
        return resp
