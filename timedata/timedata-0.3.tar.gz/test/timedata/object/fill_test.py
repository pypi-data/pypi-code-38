import unittest
from timedata.object import fill


class Bar:
    @classmethod
    def __eq__(cls, other):
        return isinstance(other, cls)


class BazSimple(Bar):
    TIMEDATA_ATTRIBUTES = ['foo', 'bar']


class Baz(Bar):
    TIMEDATA_ATTRIBUTES = {'foo': True, 'bar': lambda x: 1000 + x}


class FillTest(unittest.TestCase):
    def test_trivial(self):
        fill.fill({})

    def test_simple(self):
        a = {'_': __name__ + '.Bar', 'foo': 'foo', 'bar': 2}
        expected = dict(a, _class=Bar, _object=Bar())

        fill.fill(a)
        self.assertEqual(a, expected)
        self.assertEqual(a['_object'].foo, 'foo')
        self.assertEqual(a['_object'].bar, 2)

    def test_attributes_simple(self):
        a = {'_': __name__ + '.BazSimple', 'foo': 'foo', 'bar': 2}
        expected = dict(a, _class=BazSimple, _object=BazSimple())
        fill.fill(a)
        self.assertEqual(a, expected)
        self.assertEqual(a['_object'].foo, 'foo')
        self.assertEqual(a['_object'].bar, 2)

    def test_attributes(self):
        a = {'_': __name__ + '.Baz', 'foo': 'foo', 'bar': 2}
        expected = dict(a, _class=Baz, _object=Baz())
        fill.fill(a)
        self.assertEqual(a, expected)
        self.assertEqual(a['_object'].foo, 'foo')
        self.assertEqual(a['_object'].bar, 1002)

    def test_error(self):
        with self.assertRaises(ValueError):
            fill.fill({'_': __name__ + '.Baz', 'baz': 1})
