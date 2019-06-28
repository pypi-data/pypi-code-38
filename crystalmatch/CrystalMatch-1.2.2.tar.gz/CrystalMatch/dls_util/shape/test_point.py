import sys
from unittest import TestCase

from CrystalMatch.dls_util.shape.point import Point


class TestPoint(TestCase):

    def test_length_calculation_from_point_to_origin(self):
        a = Point(3, 0)
        b = Point(3, 4)
        c = Point(6, 12)
        self.assertAlmostEqual(a.length(), 3, places=3)
        self.assertAlmostEqual(b.length(), 5, places=3)
        self.assertAlmostEqual(c.length(), 13.416, places=3)

    def test_distance_calculation_between_two_points(self):
        a = Point(3, 4)
        b = Point(7, 13)
        self.assertAlmostEqual(a.distance_to(b), 9.849, places=3)

    def test_scaled_point_calculation(self):
        a = Point(35, 27)
        b = a.scale(0.2)
        c = a.scale(5)
        self.assertEqual(a.x, 35)
        self.assertEqual(a.y, 27)
        self.assertEqual(b.x, 7)
        self.assertEqual(b.y, 5.4)
        self.assertEqual(c.x, 175)
        self.assertEqual(c.y, 135)

    def test_clone_and_round_point_using_intify(self):
        a = Point(35.3, 88.6)
        b = a.intify()
        self.assertNotEqual(a, b)
        self.assertEqual(b.x, 35)
        self.assertEqual(b.y, 89)
        a = Point(35.6, 88.5)
        b = a.intify()
        self.assertNotEqual(a, b)
        self.assertEqual(b.x, 36)
        # Note: the rouding convetion has been changed in Python3 - half are rounded down!!
        # 0.5 becomes 0 not one
        # see: https://stackoverflow.com/questions/10825926/python-3-x-rounding-behavior
        if sys.version_info[0] < 3:
            self.assertEqual(b.y, 89)
        else:
            self.assertEqual(b.y, 88)

    def test_clone_and_convert_to_float_using_floatify(self):
        a = Point(int(35), int(44))
        b = a.floatify()
        self.assertTrue(isinstance(a.x, int))
        self.assertEqual(b.x, float(35))
        self.assertTrue(isinstance(b.x, float))
        self.assertEqual(b.y, float(44))
        self.assertTrue(isinstance(b.y, float))

    def test_report_point_as_tuple(self):
        a = Point(3, 4)
        self.assertEqual(a.tuple(), (3, 4))

    def test_serialize_point(self):
        self.assertEqual(Point(3.4, 5.7).serialize(), "3.4;5.7")
        self.assertEqual(Point(3, 5.0).serialize(sep="test"), "3test5.0")

    def test_generate_point_from_2d_array(self):
        self.assertEqual(Point.from_array([3.4, 5]).serialize(), Point(3.4, 5).serialize())

    def test_deserialize_point(self):
        a = Point.deserialize("3.4;5.7")
        b = Point.deserialize("3test5.0", sep="test")
        self.assertEqual(a.x, 3.4)
        self.assertEqual(a.y, 5.7)
        self.assertEqual(b.x, 3)
        self.assertEqual(b.y, 5.0)

    def test_deserialize_with_invalid_syntax_throws_exception(self):
        self.assertRaises(ValueError, Point.deserialize, "3.4;")
        self.assertRaises(ValueError, Point.deserialize, ";5.7")
        self.assertRaises(ValueError, Point.deserialize, "Some text")
        self.assertRaises(ValueError, Point.deserialize, "3.4.3;5.7")

    def test_operator_methods(self):
        a = Point(3, 4)
        self.assertEqual(Point(23.0, 12.0), Point(23, 12))      # Equals
        self.assertEqual(-a, Point(-3, -4))                     # Negation
        self.assertEqual(a - Point(1, 1.5), Point(2.0, 2.5))    # Subtraction
        self.assertEqual(a + Point(1, 1.5), Point(4, 5.5))      # Addition
        self.assertEqual(a * 2, Point(6, 8))                    # Multiplication
        self.assertEqual(a / 2, Point(1.5, 2.0))                # Division
        self.assertEqual((a // int(2)), Point(1, 2))            # Floor division
        self.assertEqual((a / float(2)), Point(1.5, 2))         # True division
        self.assertEqual(str(a), "(3.00, 4.00)")                # Print to string
        self.assertEqual(repr(a), "Point(3, 4)")                # Represent to string

    def test_operator_method_with_invalid_type_returns_false(self):
        self.validate_code_throws_type_error_exception("Point(3, 4) + 3.0")
        self.validate_code_throws_type_error_exception("Point(3, 4) - 3.0")

    def test_equal_comparison_with_invalid_type_returns_false(self):
        self.assertFalse(Point(3, 4) == 3.0)

    def validate_code_throws_type_error_exception(self, code_with_exception):
        with self.assertRaises(TypeError):
            eval(code_with_exception)
