# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
"""Middleware class for aiohttp."""

import asyncio
import sys
from logging import getLogger

from ...exceptions import RequestBlocked
from ...runtime_storage import runtime
from ...utils import update_wrapper
from .base import BaseMiddleware

LOGGER = getLogger(__name__)


def aiohttp_web_middleware(func):
    """Identical to aiohttp.web.middleware."""
    # This function was reimplemented in the agent to avoid importing aiohttp.
    func.__middleware_version__ = 1
    return func


class AioHTTPMiddleware(BaseMiddleware):
    """Middleware class for aiohttp."""

    # Decorator aiohttp.web.middleware is used internally by aiohttp to
    # distinguish between "regular" middlewares (decorated) and middleware
    # factories default.

    def __call__(self, original):
        """Wrap the original aiohttp middleware with callbacks."""
        from aiohttp import web

        @aiohttp_web_middleware
        @asyncio.coroutine
        def wrapped(request, handler):
            try:
                self.strategy.before_hook_point()
                self.execute_pre_callbacks((request,), record_attack=True)
                try:
                    response = yield from original(request, handler)
                except web.HTTPException as exc:
                    # Each HTTP status code is a subclass of HTTPException.
                    # These exceptions are also a subclass of Response.
                    response = exc
                except Exception:
                    self.execute_failing_callbacks(sys.exc_info())
                    raise
                return self.execute_post_callbacks(
                    response, record_attack=True
                )
            except RequestBlocked:
                runtime.clear_request(self.queue, self.observation_queue)
                raise
            finally:
                runtime.clear_request()

        update_wrapper(wrapped, original)
        return wrapped

    # The decorator order is important here. The flag aiohttp.web.middleware is
    # lost on a static method, and aiohttp will consider this method to be a
    # middleware factory and raise an error if the middleware is enabled but not
    # hooked.

    @staticmethod
    @aiohttp_web_middleware
    @asyncio.coroutine
    def handle(request, handler):
        """Instrumentation point, do nothing."""
        resp = yield from handler(request)
        return resp

    @staticmethod
    @asyncio.coroutine
    def factory(app, handler):
        """Old style middleware factory, used in aiohttp 2.2."""

        # This function is a coroutine (direct call to another coroutine
        # function).
        def middleware_handler(request):
            return AioHTTPMiddleware.handle(request, handler)

        return middleware_handler
