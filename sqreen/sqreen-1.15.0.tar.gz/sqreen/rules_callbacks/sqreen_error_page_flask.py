# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Custom error page for Flask
"""
from ..exceptions import RequestBlocked
from .headers_insert import convert_to_str
from .sqreen_error_page import BaseSqreenErrorPage


class SqreenErrorPageFlask(BaseSqreenErrorPage):
    @staticmethod
    def _get_exception(app, exception, *args, **kwargs):
        if not exception:
            return

        # Ignore exception which are not attack blocked
        if not isinstance(exception, RequestBlocked):
            return

        return exception

    @staticmethod
    def _get_response(exception, content, status_code, headers={}):
        from flask import make_response

        response = make_response(content)
        response.status_code = status_code

        for header_name, header_value in convert_to_str(headers.items()):
            response.headers[header_name] = header_value

        return response
