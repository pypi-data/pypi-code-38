# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
"""Utility functions for asyncio."""

import asyncio
import threading

# Dedicated event loop for calling coroutines in a synchronous context.
_EVENT_LOOP = None


def _run_event_loop(loop):
    """Set the current event loop and run it forever."""
    asyncio.set_event_loop(loop)
    loop.run_forever()


def _get_loop():
    """Return a running event loop.

    If called for the first time, define _EVENT_LOOP and run it forever in a
    dedicated thread.
    """
    global _EVENT_LOOP
    if _EVENT_LOOP is None:
        _EVENT_LOOP = asyncio.new_event_loop()
        thread = threading.Thread(
            target=_run_event_loop, args=(_EVENT_LOOP,), daemon=True
        )
        thread.start()
    return _EVENT_LOOP


def run_coroutine(coro):
    """Run a coroutine in a synchronous context."""
    future = asyncio.run_coroutine_threadsafe(coro=coro, loop=_get_loop())
    return future.result()
