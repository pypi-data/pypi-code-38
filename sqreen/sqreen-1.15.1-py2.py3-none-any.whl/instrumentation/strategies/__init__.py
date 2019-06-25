# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Hijacking strategies
"""

from ...utils import HAS_ASYNCIO
from .base import BaseStrategy
from .dbapi2 import DBApi2Strategy
from .django_strategy import DjangoStrategy
from .flask_strategy import FlaskStrategy
from .import_hook import ImportHookStrategy
from .psycopg2_strategy import Psycopg2Strategy
from .pyramid_strategy import PyramidStrategy

if HAS_ASYNCIO:
    from .aiohttp_strategy import AioHTTPHookStrategy, AioHTTPInstallStrategy
    from .async_event_loop import AsyncEventLoopStrategy
    from .async_import_hook import AsyncImportHookStrategy

__all__ = [
    "AioHTTPHookStrategy",
    "AioHTTPInstallStrategy",
    "AsyncEventLoopStrategy",
    "AsyncImportHookStrategy",
    "BaseStrategy",
    "DBApi2Strategy",
    "DjangoStrategy",
    "FlaskStrategy",
    "ImportHookStrategy",
    "Psycopg2Strategy",
    "PyramidStrategy",
]
