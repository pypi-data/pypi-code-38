# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Pools context resources
"""
import logging
from threading import Lock
from weakref import WeakKeyDictionary

from py_mini_racer.py_mini_racer import MiniRacer

LOGGER = logging.getLogger(__name__)


class JSContextPool:
    def __init__(self):
        self.lock = Lock()
        self.contexts = []  # needed?
        self.total = 0

    def with_context(self, func):
        context = self._fetch_context()
        try:
            return func(context)
        finally:
            self._give_back_context(context)

    def _fetch_context(self):
        with self.lock:
            if not self.contexts:  # empty
                self.total += 1
                LOGGER.info("Creating new V8 context. "
                            "Count for this pool is %d", self.total)
                return DefinitionTrackingMiniRacer()
            else:
                return self.contexts.pop()

    def _give_back_context(self, context):
        context.garbage_collect()
        if context.gc_load > 30:
            if context.gc_threshold_in_bytes == DEFAULT_GC_THRESHOLD:
                context.gc_threshold_in_bytes *= 2
                LOGGER.warning("Context %s had too many close garbage "
                               "collections; doubling the threshold to %d bytes",
                               context, context.gc_threshold_in_bytes)
                context.gc_load = 0
            else:
                LOGGER.warning("Context %s had too many close garbage "
                               "collections; discarding it", context)
                del context
                return

        with self.lock:
            self.contexts.append(context)

    class DummyRunner:
        pass

    _runner_pool_map = WeakKeyDictionary()
    _dummy_runner = DummyRunner()

    @classmethod
    def fetch_for_runner(cls, runner):
        if runner is None:
            runner = cls._dummy_runner

        if runner in cls._runner_pool_map:
            return cls._runner_pool_map[runner]
        else:
            new_pool = cls()
            cls._runner_pool_map[runner] = new_pool
            return new_pool


DEFAULT_GC_THRESHOLD = 15000000  # 15 MB


class DefinitionTrackingMiniRacer(MiniRacer):

    def __init__(self, *args, **kwargs):
        super(DefinitionTrackingMiniRacer, self).__init__(*args, **kwargs)
        self.code_ids = set()
        self.failed_code_ids = set()
        self.gc_load = 0
        self.gc_threshold_in_bytes = DEFAULT_GC_THRESHOLD

    def add_code(self, code_id, code):
        try:
            LOGGER.debug("Adding code with md5 %s to %s", code_id, self)
            self.eval('(function() {{ {} }})()'.format(code))
            self._transf_global_funcs(code_id)
            self.code_ids.add(code_id)
        except Exception:
            self.failed_code_ids.add(code_id)
            raise

    def _transf_global_funcs(self, code_id):
        snippet = '''
            if (typeof sqreen_data === 'undefined') {{
              sqreen_data = {{}};
            }}

            group = {{}};
            Object.keys(this).forEach(name => {{
              if (typeof this[name] === "function") {{
                group[name] = this[name];
                this[name] = undefined;
              }}
            }});
            sqreen_data['{}'] = group
            delete group;
        '''.format(code_id)
        self.eval(snippet)

    def garbage_collect(self):
        stats = self.heap_stats()

        # garbage collections max 1 in every 4 calls (avg)
        if stats['total_heap_size'] > self.gc_threshold_in_bytes:
            LOGGER.debug("Doing low memory notification for context")
            self.low_memory_notification()
            self.gc_load += 4
        else:
            self.gc_load = max(0, self.gc_load - 1)
