import unittest
from .intparamrange import IntParamRange
from .paramrange import ParamRange

class TestFloatParamRange(unittest.TestCase):
    def setUp(self):
        pass

    def test_generates_correct_index_values(self):
        p: ParamRange = IntParamRange("max_depth", [2, 4, 5, 6, 11])

        self.assertRaises(IndexError, p.value, 99)
        self.assertRaises(IndexError, p.value, -1)
        
        counted_vals = {}

        for _ in range(100):
            val = p.value(0)
            counted_vals[val] = True

        self.assertEqual(len(counted_vals), 2)

        for val in counted_vals.keys():
            self.assertIsInstance(val, int)
            self.assertGreaterEqual(val, 2)
            self.assertGreaterEqual(3, val)

        counted_vals = {}

        for _ in range(100):
            val = p.value(4)
            counted_vals[val] = True

        self.assertEqual(len(counted_vals), 3)

        for val in counted_vals.keys():
            self.assertIsInstance(val, int)
            self.assertGreaterEqual(val, 7)
            self.assertGreaterEqual(11, val)

        
        counted_vals = {}

        for _ in range(100):
            val = p.value(2)
            counted_vals[val] = True

        self.assertEqual(len(counted_vals), 1)

        for val in counted_vals.keys():
            self.assertIsInstance(val, int)
            self.assertEqual(val, 5)