import unittest
from typing import List
from .floatparamrange import FloatParamRange
from .paramrange import ParamRange

class TestFloatParamRange(unittest.TestCase):
    def setUp(self):
        pass

    def test_generates_correct_index_values(self):
        p: ParamRange = FloatParamRange("max_depth", [2.0, 4.0, 5.0, 9.0])

        self.assertRaises(IndexError, p.value, 99)
        self.assertRaises(IndexError, p.value, -1)
        
        counted_vals = {}

        for _ in range(100):
            val = p.value(0)
            counted_vals[val] = True

        self.assertEqual(len(counted_vals), 9)

        for val in counted_vals.keys():
            self.assertGreaterEqual(val, 2.0)
            self.assertGreaterEqual(3.5, val)

        counted_vals = {}

        for _ in range(100):
            val = p.value(3)
            counted_vals[val] = True

        self.assertEqual(len(counted_vals), 9)

        for val in counted_vals.keys():
            self.assertGreaterEqual(val, 7.0)
            self.assertGreaterEqual(9.0, val)