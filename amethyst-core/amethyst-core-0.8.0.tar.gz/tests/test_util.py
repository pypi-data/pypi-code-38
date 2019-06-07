#!/usr/bin/env python
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: LGPL-3.0

from __future__ import division, absolute_import, print_function, unicode_literals
import six.moves
import threading
import unittest

from amethyst.core import cached_property, coalesce

class Foo(object):
    def __init__(self, bar=None):
        self.computed = 0
        self.errors = []
        self.local = threading.local()
        if bar is not None:
            self.bar = bar

    @cached_property
    def bar(self):
        self.computed += 1
        return 42

    @cached_property(delegate="local")
    def baz(self):
        self.computed += 1
        return six.moves._thread.get_ident()


class MyTest(unittest.TestCase):

    def test_coalesce(self):
        self.assertIsNone(coalesce(), "Nothing!")
        self.assertIsNone(coalesce(None, None, None), "None!")
        self.assertEqual(coalesce(42, None, None), 42, "Match first")
        self.assertEqual(coalesce(None, 42, None, None), 42, "Match middle")
        self.assertEqual(coalesce(None, None, None, "42"), "42", "Match last")
        self.assertEqual(coalesce(None, 0, None, None), 0, "Match zero")
        self.assertFalse(coalesce(None, False, None, None), "Match falsey")

    def _thread_test_cached_property(self, foo, ident, computed):
        # runs in thread, so have to save any exceptions to throw later
        try:
            self.assertEqual(foo.computed, computed)
            self.assertNotEqual(foo.baz, ident)
            self.assertEqual(foo.computed, computed + 1)
            self.assertNotEqual(foo.baz, ident)
            self.assertEqual(foo.computed, computed + 1)
            foo.thread_ok = True
        except Exception as err:
            foo.errors.append(err)

    def test_cached_property(self):
        foo = Foo()
        computed = 0

        self.assertEqual(foo.computed, computed, "Not calculated yet")
        computed += 1
        self.assertEqual(foo.bar, 42, "Computed")
        self.assertEqual(foo.computed, computed, "Calculated once")
        self.assertEqual(foo.bar, 42, "Cached")
        self.assertEqual(foo.computed, computed, "Calculated once (still)")

        foo.bar = 12
        self.assertEqual(foo.bar, 12, "Assigned")
        self.assertEqual(foo.computed, computed, "Calculated once (still)")

        del foo.bar
        computed += 1
        self.assertEqual(foo.bar, 42, "Recomputed")
        self.assertEqual(foo.computed, computed, "Calculated twice")

        foo = Foo(bar=12)
        computed = 0
        self.assertEqual(foo.bar, 12, "Assigned")
        self.assertEqual(foo.computed, computed, "Never calculated")

        del foo.bar
        computed += 1
        self.assertEqual(foo.bar, 42, "Cleared / Computed")
        self.assertEqual(foo.computed, computed, "Calculated finally")

        # threading
        computed += 1
        ident = foo.baz
        self.assertTrue(bool(ident))
        self.assertEqual(foo.computed, computed)
        self.assertEqual(foo.baz, ident)
        self.assertEqual(foo.computed, computed)
        self.assertEqual(foo.local.baz, ident, msg="Written to correct attribute")

        computed += 1
        del foo.baz
        self.assertEqual(foo.baz, ident)
        self.assertEqual(foo.computed, computed)

        thr = threading.Thread(target=self._thread_test_cached_property, args=(foo, ident, computed))
        thr.start()
        thr.join()
        for err in foo.errors:
            raise err
        self.assertTrue(foo.thread_ok) # Extra-paranoid check
        computed += 1                  # incremented in thread

        # Unchanged in this thread
        self.assertEqual(foo.baz, ident)
        self.assertEqual(foo.computed, computed)


if __name__ == '__main__':
    unittest.main()
