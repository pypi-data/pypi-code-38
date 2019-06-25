# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
"""Patch an async event loop class with a context-aware task factory."""

import logging

from ...async_context import create_task_factory
from .import_hook import ImportHookStrategy

LOGGER = logging.getLogger(__name__)


def _patch_loop_cls(loop_cls):
    """Patch an async event loop class with a context-aware task factory.

    Return the modified class constructor.
    """
    orig_init = loop_cls.__init__
    orig_set_task_factory = loop_cls.set_task_factory

    def __init__(self, *args, **kwargs):
        orig_init(self, *args, **kwargs)
        self.set_task_factory(None)

    def set_task_factory(self, factory):
        factory = create_task_factory(factory)
        orig_set_task_factory(self, factory)

    setattr(loop_cls, "__init__", __init__)
    setattr(loop_cls, "set_task_factory", set_task_factory)
    return loop_cls


class AsyncEventLoopStrategy(ImportHookStrategy):
    """Patch an async event loop class with a context-aware task factory."""

    def import_hook_callback(self, original):
        return _patch_loop_cls(original)
