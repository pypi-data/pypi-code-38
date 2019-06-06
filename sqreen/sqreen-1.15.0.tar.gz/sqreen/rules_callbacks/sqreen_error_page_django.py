# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Custom error page for Django
"""
from ..exceptions import RequestBlocked
from .headers_insert import convert_to_str
from .sqreen_error_page import BaseSqreenErrorPage


class SqreenErrorPageDjango(BaseSqreenErrorPage):
    @staticmethod
    def _get_exception(handler, request, resolved, exc_infos, *args, **kwargs):
        if not exc_infos:
            return

        exc_class = exc_infos[0]

        # Ignore exception which are not attack blocked
        if not issubclass(exc_class, RequestBlocked):
            return

        return exc_infos[1]

    @staticmethod
    def _get_response(exception, content, status_code, headers=None):
        from django.http import HttpResponse

        response = HttpResponse(content)
        response.status_code = status_code

        if headers:
            for header_name, header_value in convert_to_str(headers.items()):
                response[header_name] = header_value

        return response
