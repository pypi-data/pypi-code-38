# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Package for framework middlewares integrations
"""
from ...utils import HAS_ASYNCIO
from .django_middleware import DjangoMiddleware
from .flask_middleware import FlaskMiddleware
from .pyramid_middleware import PyramidMiddleware

if HAS_ASYNCIO:
    from .aiohttp_middleware import AioHTTPMiddleware

__all__ = [
    "AioHTTPMiddleware",
    "DjangoMiddleware",
    "FlaskMiddleware",
    "PyramidMiddleware",
]
