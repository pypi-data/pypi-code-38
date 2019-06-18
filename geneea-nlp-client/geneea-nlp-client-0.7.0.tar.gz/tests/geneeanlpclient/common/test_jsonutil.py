from unittest import TestCase

from typing import NamedTuple

from geneeanlpclient.common.dictutil import getValue, DictBuilder


class TestDictBuilder(TestCase):
    def test_addIfPresent(self):
        d = DictBuilder({})
        d.addIfNotNone('k1', 'v1')
        self.assertDictEqual({'k1': 'v1'}, d.build())

        d.addIfNotNone('k2', None)
        self.assertDictEqual({'k1': 'v1'}, d.build())

        d.addIfNotNone('k2', None, allowEmpty=True)
        self.assertDictEqual({'k1': 'v1'}, d.build())

        d.addIfNotNone('k2', 0)
        self.assertDictEqual({'k1': 'v1', 'k2': 0}, d.build())

        d.addIfNotNone('k2', 0, allowEmpty=True)
        self.assertDictEqual({'k1': 'v1', 'k2': 0}, d.build())

        d.addIfNotNone('k3', '')
        self.assertDictEqual({'k1': 'v1', 'k2': 0}, d.build())

        d.addIfNotNone('k3', '', allowEmpty=True)
        self.assertDictEqual({'k1': 'v1', 'k2': 0, 'k3': ''}, d.build())

        d.addIfNotNone('k4', [1, 2, 3])
        self.assertDictEqual({'k1': 'v1', 'k2': 0, 'k3': '', 'k4': [1, 2, 3]}, d.build())

        d.addIfNotNone('k5', [])
        self.assertDictEqual({'k1': 'v1', 'k2': 0, 'k3': '', 'k4': [1, 2, 3]}, d.build())

        d.addIfNotNone('k5', [], allowEmpty=True)
        self.assertDictEqual({'k1': 'v1', 'k2': 0, 'k3': '', 'k4': [1, 2, 3], 'k5': []}, d.build())

    def test_addIdIfPresent(self):
        class Ided(NamedTuple):
            id: str
            val: int

        d = DictBuilder({})

        v1 = Ided(id='a', val=1)

        d.addId('k1', v1)
        self.assertDictEqual({'k1': 'a'}, d.build())

        d.addId('k2', None)
        self.assertDictEqual({'k1': 'a'}, d.build())

        with self.assertRaises(AttributeError):
            d.addId('k3', ['a'])

        with self.assertRaises(AttributeError):
            d.addId('k3', 'aa')

    def test_addIdsIfPresent(self):
        class Ided(NamedTuple):
            id: str
            val: int

        d = DictBuilder({})

        v1 = Ided(id='a', val=1)

        d.addIds('k1', [v1])
        self.assertDictEqual({'k1': ['a']}, d.build())

        d.addIds('k2', None)
        self.assertDictEqual({'k1': ['a']}, d.build())

        d.addIds('k2', [])
        self.assertDictEqual({'k1': ['a']}, d.build())

        with self.assertRaises(AttributeError):
            d.addIds('k3', ['a'])

        with self.assertRaises(AttributeError):
            d.addIds('k3', 'aa')


class TestJsonUtil(TestCase):

    def test_getValue(self):
        d = {
            'k1': 'v1',
            'k2': 2,
            'k3': {
                'k3k1': 'v2',
                'k3k2': 'v3',
                'k3k3': {
                    'k3k3k1': 'v4',
                    'k3k3k2': 'v5',
                    'k3k3k3': None
                },
            },
            'k4': None,
            'k5': []
        }

        self.assertEqual(None, getValue(None, 'k1'))
        self.assertEqual(2, getValue(None, 'k1', default=2))

        self.assertEqual('v1', getValue(d, 'k1'))
        self.assertEqual('v1', getValue(d, 'k1', default=2))

        self.assertEqual(None, getValue(d, 'xyz'))
        self.assertEqual(2, getValue(d, 'xyz', default=2))

        self.assertEqual(None, getValue(d, 'k1.xyz'))
        self.assertEqual(2, getValue(d, 'k1.xyz', default=2))

        self.assertEqual('v2', getValue(d, 'k3.k3k1'))
        self.assertEqual('v2', getValue(d, 'k3.k3k1', default=2))

        self.assertEqual('v4', getValue(d, 'k3.k3k3.k3k3k1'))
        self.assertEqual('v5', getValue(d, 'k3.k3k3.k3k3k2'))
        self.assertEqual(None, getValue(d, 'k3.k3k3.k3k3k3'))
        self.assertEqual(2, getValue(d, 'k3.k3k3.k3k3k3', default=2))

        self.assertEqual(None, getValue(d, 'k4'))
        self.assertEqual(2, getValue(d, 'k4', default=2))
        self.assertEqual([], getValue(d, 'k5'))
        self.assertEqual([], getValue(d, 'k5', default=2))
