
from __future__ import division, print_function, unicode_literals, absolute_import

import unittest
import pickle
from collections import OrderedDict

try:
    import context
except ImportError:
    from . import context

import ordered_namespace as ons


"""
Kinds of tests:
    self.assertTrue(value)
    self.assertFalse(value)

    self.assertGreater(first, second, msg=None)
    self.assertGreaterEqual(first, second, msg=None)
    self.assertLess(first, second, msg=None)
    self.assertLessEqual(first, second, msg=None)

    self.assertAlmostEqual(first, second, places=7, msg=None, delta=None)
    self.assertNotAlmostEqual(first, second, places=7, msg=None, delta=None)

    self.assertItemsEqual(actual, expected, msg=None)
    self.assertSequenceEqual(seq1, seq2, msg=None, seq_type=None)
    self.assertListEqual(list1, list2, msg=None)
    self.assertTupleEqual(tuple1, tuple2, msg=None)
    self.assertSetEqual(set1, set2, msg=None)
    self.assertDictEqual(expected, actual, msg=None)

    self.assertRaises(Exception, some_func, arg, arg_nother)

    np.testing.assert_equal(A, B)
    np.testing.assert_allclose(actual, desired, rtol=1e-07, atol=0, err_msg='', verbose=True)
"""

#------------------------------------------------

class TestBasic(unittest.TestCase):
    # def setUp(self):
    #     pass

    # def tearDown(self):
    #     pass

    def test_does_it_run(self):
        info = ons.Struct()

    def test_attributes(self):
        info = ons.Struct()

        item = [1, 2, 3]
        info.AA = item

        self.assertTrue(item == info.AA)

    def test_keys(self):
        info = ons.Struct()

        item = [1, 2, 3]
        info['AA'] = item

        self.assertTrue(item == info['AA'])

    def test_attributes_keys(self):
        info = ons.Struct()

        item = [1, 2, 3]
        info['AA'] = item

        self.assertTrue(item == info.AA)

    def test_special_keys(self):
        info = ons.Struct()

        item = [1, 2, 3]
        def fn():
            info['_odict'] = item

        self.assertRaises(KeyError, fn)

    def test_order(self):
        keys = ['Z', 'z', 'a', 'B00', 'B1', 'B0']
        values = list(range(len(keys)))

        info_1 = ons.Struct()
        info_2 = ons.Struct()

        for k, v in zip(keys, values):
            info_1[k] = v

        for k, v in zip(keys[::-1], values[::-1]):
            info_2[k] = v

        keys_test_1 = list(info_1.keys())
        keys_test_2 = list(info_2.keys())

        self.assertTrue(keys_test_1 == keys_test_2[::-1])

    def test_nested_flag_set(self):
        info = ons.Struct(nested=True)
        self.assertTrue(info.__dict__['_nested'])

    def test_nested_flag_not_set(self):
        info = ons.Struct(nested=False)
        self.assertFalse(info.__dict__['_nested'])

    def test_nested_flag_default_not_set(self):
        info = ons.Struct()
        self.assertFalse(info.__dict__['_nested'])

    def test_nested_dict_converted(self):
        info = ons.Struct(nested=True)

        nuts = {'a': [1, 2], 'X': 'hello'}
        corn = {'b': [6, 9], 'Y': 'bye'}

        info.AA = nuts
        self.assertTrue(type(info.AA) == ons.Struct)

        info.AA.BB = corn
        self.assertTrue(type(info.AA.BB) == ons.Struct)

    def test_not_nested_dict_converted(self):
        info = ons.Struct(nested=False)

        nuts = {'a': [1, 2], 'X': 'hello'}

        info.AA = nuts
        self.assertTrue(type(info.AA) == dict)

    def test_nested_dict_update(self):
        info = ons.Struct(nested=True)

        nuts = {'a': [1, 2], 'X': 'hello'}
        corn = {'b': [6, 9], 'Y': 'bye', 'm': nuts}
        yikes = {'c': [6, 9], 'Z': 'hello', 'n': corn}

        info.CC = yikes

        self.assertTrue(type(info.CC) == ons.Struct)
        self.assertTrue(type(info.CC.n) == ons.Struct)
        self.assertTrue(type(info.CC.n.m) == ons.Struct)

    def test_nested_dict_define(self):
        nuts = {'a': [1, 2], 'X': 'hello'}
        corn = {'b': [6, 9], 'Y': 'bye', 'm': nuts}
        yikes = {'c': [6, 9], 'Z': 'hello', 'n': corn}

        info = ons.Struct(yikes, nested=True)

        self.assertTrue(type(info.n) == ons.Struct)
        self.assertTrue(type(info.n.m) == ons.Struct)

    def test_nested_dict_list(self):
        nuts = {'a': [1, 2], 'X': 'hello'}
        corn = {'b': [6, 9], 'Y': 'bye'}
        yikes = {'c': [6, 9], 'Z': 'hello'}

        stuff = [nuts, corn, yikes]

        info = ons.Struct(nested=True)
        info.S = stuff

        self.assertTrue(type(info.S[0]) == ons.Struct)

    def test_as_dict(self):
        info = ons.Struct(nested=True)

        nuts = {'a': [1, 2], 'X': 'hello'}
        corn = {'b': [6, 9], 'Y': 'bye'}

        info.AA = nuts
        info.AA.BB = corn

        info = info.asdict()

        self.assertTrue(type(info) == OrderedDict)
        self.assertTrue(type(info['AA']) == OrderedDict)
        self.assertTrue(type(info['AA']['BB']) == OrderedDict)



class TestFancy(unittest.TestCase):
    # def setUp(self):
    #     pass

    # def tearDown(self):
    #     pass

    def test_does_it_pickle(self):
        info = ons.Struct()
        info.A = [1, 2, 3, 4, 'A']

        z = pickle.dumps(info)

    def test_does_it_unpickle(self):
        info = ons.Struct()
        info.A = [1, 2, 3, 4, 'WW']

        z = pickle.dumps(info)
        anfo = pickle.loads(z)

    def test_pickle_unpickle_keys(self):
        info = ons.Struct()
        info.A = [1, 2, 3, 4, 'WW']

        z = pickle.dumps(info)
        anfo = pickle.loads(z)

        for k, v in info.items():
            self.assertTrue(k in anfo)

    def test_pickle_unpickle_value(self):
        info = ons.Struct()
        info.A = [1, 2, 3, 4, 'WW']
        info.SS = 4
        info.WWW = {'d': [1,2,3]}

        z = pickle.dumps(info)
        anfo = pickle.loads(z)

        for k, v in info.items():
            self.assertTrue(v == anfo[k])

#------------------------------------------------

if __name__ == '__main__':
    unittest.main(verbosity=2)
