# -*- coding: UTF-8 -*-

import unittest

from . import LFUDACache, memoize

KEY, VALUE, HITS, PREV, NEXT, MISSES, UPDATES = range(7)


class TestCache(unittest.TestCase):
    @property
    def misses(self):
        return self.root[MISSES]

    @property
    def data(self):
        return self.cache._data

    @property
    def root(self):
        return self.cache._root

    def setUp(self):
        self.size = 5
        self.cache = LFUDACache(self.size)

    def assertIterEqual(self, a, b):
        self.assertListEqual(list(a), list(b))

    def items(self):
        return list(self.cache.items())

    def test_eviction(self):
        items = [(i, 'value for %s' % i) for i in range(self.size + 1)]
        for k, v in items:
            self.cache[k] = v

        self.assertNotIn(0, self.cache)
        self.assertNotIn(0, self.data)

        self.assertListEqual(sorted(self.cache.items()), items[1:])

    def test_pop(self):
        self.cache['a'] = 1
        self.assertEqual(self.cache.pop('a'), 1)
        self.assertIterEqual(self.cache, ())

        with self.assertRaises(KeyError):
            self.cache.pop('a')

        self.assertEqual(self.cache.pop('a', 2), 2)

    def test_popitem(self):
        self.cache['b'] = 2
        self.cache['a'] = 1
        self.assertEqual(self.cache.popitem(), ('b', 2))
        self.assertEqual(self.cache.popitem(), ('a', 1))
        self.assertRaises(KeyError, self.cache.popitem)

    def test_equal(self):
        a = LFUDACache(3)
        b = LFUDACache(2)

        for i in range(2):
            for c in (a, b):
                c[i] = 2 ** i

        self.assertEqual(a, b)
        a[0] = 3
        self.assertNotEqual(a, b)

    def test_clear(self):
        items = [(i, 'value for %s' % i) for i in range(self.size)]
        for k, v in items:
            self.cache[k] = v

        self.cache.clear()
        self.assertListEqual(self.items(), [])

        # Check circularity (empty)
        self.assertIs(self.root, self.root[NEXT])
        self.assertIs(self.root, self.root[NEXT])

        self.cache['a'] = 1
        self.assertListEqual(self.items(), [('a', 1)])

        # Check circularity (1 item)
        self.assertIs(self.root[NEXT], self.root[PREV])
        self.assertIs(self.root, self.root[NEXT][PREV])
        self.assertIs(self.root, self.root[NEXT][NEXT])

    def test_aging(self):
        items = [(i, 'value for %s' % i) for i in range(self.size)]
        for k, v in items:
            self.cache[k] = v

        for k, _ in self.items():
            self.cache.get(k)  # raise hit counter

        self.cache['a1'] = 'va1'  # rejected item
        self.assertNotIn('a1', self.cache)  # do not raise misses

        self.cache['a2'] = 'va2'  # another rejected item
        self.assertRaises(KeyError, self.cache.__getitem__, 'a2')  # misses

        self.cache['a3'] = 'va3'  # accepted item
        self.assertEqual(self.cache.get('a3'), 'va3')

        for k, v in self.items():
            self.cache.get(k, v)  # raise hit counter

        self.cache['a4'] = 'v4'  # rejected item
        self.assertNotIn('a4', self.cache)

    def test_ordering(self):
        self.cache['b'] = 2
        self.cache['a'] = 1

        self.assertIterEqual(self.cache, 'ab')
        self.assertEqual(self.cache.get('b'), 2)
        self.assertIterEqual(self.cache, 'ba')
        self.assertEqual(self.cache.peek('a'), 1)
        self.assertIterEqual(self.cache, 'ba')
        self.assertEqual(self.cache.peek('b'), 2)
        self.assertIterEqual(self.cache, 'ba')

        self.cache.get('x')
        self.cache.get('x')
        self.cache.get('x')
        self.cache.get('x')
        self.cache['c'] = 3
        self.assertIterEqual(self.cache, 'cba')
        self.cache['d'] = 4
        self.assertIterEqual(self.cache, 'dcba')

        self.cache['a'] = 1
        self.assertIterEqual(self.cache, 'adcb')

        self.cache['a'] = 1
        self.cache['d'] = 1
        del self.cache['c']
        self.assertIterEqual(self.cache, 'adb')

        self.assertIterEqual(reversed(self.cache), 'bda')

    def test_delitem(self):
        self.cache['a'] = 1
        del self.cache['a']
        self.assertIterEqual(self.cache, ())

        with self.assertRaises(KeyError):
            del self.cache['a']

    def test_missing(self):
        self.assertRaises(KeyError, self.cache.peek, 'c')
        self.assertRaises(KeyError, self.cache.__getitem__, 'c')
        self.assertEqual(self.cache.get('c', 3), 3)

    def test_iters(self):
        items = [(i, 'value for %s' % i) for i in range(self.size)]
        for k, v in items[::-1]:
            self.cache[k] = v

        self.assertEqual(list(self.cache), [k for k, _ in items])
        self.assertEqual(list(self.cache.keys()), [k for k, _ in items])
        self.assertEqual(list(self.cache.values()), [v for _, v in items])
        self.assertEqual(list(self.cache.items()), items)

    def test_properties(self):
        self.assertEqual(self.misses, 0)
        self.cache.get('a')
        self.assertEqual(self.misses, 1)


class TestMemoize(unittest.TestCase):
    def fnc(self, *args, **kwargs):
        self.calls += 1
        return args, kwargs

    def setUp(self):
        self.calls = 0
        self.memoized = memoize(5)(self.fnc)

    def test_caching(self):
        self.memoized('a')
        self.memoized('a')
        self.assertEqual(self.calls, 1)

        self.calls = 0
        self.memoized('a')
        self.memoized('b')
        self.assertEqual(self.calls, 1)

    def test_expiration(self):
        self.memoized('c')
        self.memoized('d')
        self.memoized('e')
        self.memoized('f')
        self.memoized('g')
        self.memoized('h')
        self.assertEqual(self.calls, 6)

        self.memoized('d')
        self.assertEqual(self.calls, 6)

        self.memoized('c')
        self.assertEqual(self.calls, 7)

    def test_method(self):
        class A(object):
            calls = 0

            @memoize(2)
            def method(self, param):
                self.calls += 1
                return param + 1

        o = A()
        self.assertEqual(o.method(1), 2)
        self.assertEqual(o.calls, 1)
        self.assertEqual(o.method(1), 2)
        self.assertEqual(o.calls, 1)
        self.assertEqual(o.method(2), 3)
        self.assertEqual(o.calls, 2)
