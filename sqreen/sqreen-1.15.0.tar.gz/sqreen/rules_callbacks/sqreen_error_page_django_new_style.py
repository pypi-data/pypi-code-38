# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Custom error page for Django new style middlewares
"""
from ..exceptions import RequestBlocked
from .sqreen_error_page_django import SqreenErrorPageDjango


class SqreenErrorPageDjangoNewStyle(SqreenErrorPageDjango):
    @staticmethod
    def _get_exception(request, exc, *args, **kwargs):
        if not exc:
            return

        if not isinstance(exc, RequestBlocked):
            return

        return exc
