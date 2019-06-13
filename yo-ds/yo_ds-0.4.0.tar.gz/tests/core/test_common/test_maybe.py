import unittest
from yo_core._common import *
import numpy as np

class TestClass:
    def __init__(self):
        self.number = 123
        self.array = [1,2,3]
        self.matrix = np.array([[1,2],[3,4]])
        self.tensor = np.array([ [[1,2],[3,4]] , [[5,6],[7,8]] ])
        self.dictionary = dict(a=2,b=3)

    def call(self):
        return 'ok'

    def arg_call(self, arg1, arg2):
        return arg1+arg2

    def throwing_call(self):
        raise ValueError('')

class MaybeTests(unittest.TestCase):
    def test_field_access(self):
        self.assertEqual(123,maybe(TestClass(),'number'))

    def test_array_access(self):
        self.assertEqual(2,maybe(TestClass(), 'array', [1]))

    def test_matrix_access(self):
        self.assertEqual(3,maybe(TestClass(), 'matrix', [1,0]))

    def test_3dmatrix_access(self):
        self.assertEqual(8,maybe(TestClass(), 'tensor', [1,1,1]))

    def test_dict_access(self):
        self.assertEqual(3,maybe(TestClass(), 'dictionary', ['b']))

    def test_none(self):
        self.assertIsNone(maybe(None,'a'))

    def test_call_1(self):
        self.assertEqual('ok',maybe(TestClass(),TestClass.call))

    def test_call_2(self):
        self.assertEqual('ok',maybe(TestClass(),'call',mb_call()))

    def test_call_with_args(self):
        self.assertEqual(5,maybe(TestClass(),'arg_call',mb_call(2,3)))

    def test_throwing(self):
        self.assertRaises(ValueError,lambda: maybe(TestClass(),'throwing_call',mb_call()))


    def test_throwing_with_try_catch(self):
        self.assertEqual(None,maybe(TestClass(), 'throwing_call', mb_call().try_catch()))

    def test_default(self):
        self.assertEqual('default',maybe(TestClass(),'non_existing', default='default'))
