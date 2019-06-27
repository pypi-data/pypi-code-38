# standard libraries
import logging
import unittest

# local libraries
from nion.utils import Converter


class TestConverter(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_float_to_scaled_integer_with_negative_min(self):
        converter = Converter.FloatToScaledIntegerConverter(1000, -100, 100)
        self.assertAlmostEqual(converter.convert(0), 500)
        self.assertAlmostEqual(converter.convert(-100), 0)
        self.assertAlmostEqual(converter.convert(100), 1000)
        self.assertAlmostEqual(converter.convert_back(converter.convert(0)), 0)
        self.assertAlmostEqual(converter.convert_back(converter.convert(-100)), -100)
        self.assertAlmostEqual(converter.convert_back(converter.convert(100)), 100)



if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
