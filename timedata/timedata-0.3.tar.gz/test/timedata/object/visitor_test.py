from timedata.object import visitor
import collections
import unittest


class VisitorTest(unittest.TestCase):
    maxDiff = 10000

    def test_pre(self):
        results = []

        def visitor_fn(parent, key, node):
            results.append((key, node))

        visitor.visit(DATA, visitor_fn, pre=True)
        self.assertEqual(results, PRE)

    def test_post(self):
        results = []

        def visitor_fn(parent, key, node):
            results.append((key, node))

        visitor.visit(DATA, visitor_fn)
        self.assertEqual(results, POST)


DATA = collections.OrderedDict(
    (('foo', 'bar'), ('baz', [0, True, None, 3.5]), ('bing', {'bong': {}}))
)

PRE = [
    (None, DATA),
    ('foo', 'bar'),
    ('baz', [0, True, None, 3.5]),
    (0, 0),
    (1, True),
    (2, None),
    (3, 3.5),
    ('bing', {'bong': {}}),
    ('bong', {}),
]

POST = [
    ('foo', 'bar'),
    (0, 0),
    (1, True),
    (2, None),
    (3, 3.5),
    ('baz', [0, True, None, 3.5]),
    ('bong', {}),
    ('bing', {'bong': {}}),
    (None, DATA),
]
