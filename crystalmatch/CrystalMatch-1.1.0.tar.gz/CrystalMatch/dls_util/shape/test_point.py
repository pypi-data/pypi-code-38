from unittest import TestCase

from CrystalMatch.dls_util.shape.point import Point


class TestPoint(TestCase):

    def test_length_calculation_from_point_to_origin(self):
        a = Point(3, 0)
        b = Point(3, 4)
        c = Point(6, 12)
        self.failUnlessAlmostEqual(a.length(), 3, places=3)
        self.failUnlessAlmostEqual(b.length(), 5, places=3)
        self.failUnlessAlmostEqual(c.length(), 13.416, places=3)

    def test_distance_calculation_between_two_points(self):
        a = Point(3, 4)
        b = Point(7, 13)
        self.failUnlessAlmostEqual(a.distance_to(b), 9.849, places=3)

    def test_scaled_point_calculation(self):
        a = Point(35, 27)
        b = a.scale(0.2)
        c = a.scale(5)
        self.failUnlessEqual(a.x, 35)
        self.failUnlessEqual(a.y, 27)
        self.failUnlessEqual(b.x, 7)
        self.failUnlessEqual(b.y, 5.4)
        self.failUnlessEqual(c.x, 175)
        self.failUnlessEqual(c.y, 135)

    def test_clone_and_round_point_using_intify(self):
        a = Point(35.3, 88.6)
        b = a.intify()
        self.failIfEqual(a, b)
        self.failUnlessEqual(b.x, 35)
        self.failUnlessEqual(b.y, 89)
        a = Point(35.6, 88.5)
        b = a.intify()
        self.failIfEqual(a, b)
        self.failUnlessEqual(b.x, 36)
        self.failUnlessEqual(b.y, 89)

    def test_clone_and_convert_to_float_using_floatify(self):
        a = Point(int(35), int(44))
        b = a.floatify()
        self.failUnless(isinstance(a.x, int))
        self.failUnlessEqual(b.x, float(35))
        self.failUnless(isinstance(b.x, float))
        self.failUnlessEqual(b.y, float(44))
        self.failUnless(isinstance(b.y, float))

    def test_report_point_as_tuple(self):
        a = Point(3, 4)
        self.failUnlessEqual(a.tuple(), (3, 4))

    def test_serialize_point(self):
        self.failUnlessEqual(Point(3.4, 5.7).serialize(), "3.4;5.7")
        self.failUnlessEqual(Point(3, 5.0).serialize(sep="test"), "3test5.0")

    def test_generate_point_from_2d_array(self):
        self.failUnlessEqual(Point.from_array([3.4, 5]).serialize(), Point(3.4, 5).serialize())

    def test_deserialize_point(self):
        a = Point.deserialize("3.4;5.7")
        b = Point.deserialize("3test5.0", sep="test")
        self.failUnlessEqual(a.x, 3.4)
        self.failUnlessEqual(a.y, 5.7)
        self.failUnlessEqual(b.x, 3)
        self.failUnlessEqual(b.y, 5.0)

    def test_deserialize_with_invalid_syntax_throws_exception(self):
        self.failUnlessRaises(ValueError, Point.deserialize, "3.4;")
        self.failUnlessRaises(ValueError, Point.deserialize, ";5.7")
        self.failUnlessRaises(ValueError, Point.deserialize, "Some text")
        self.failUnlessRaises(ValueError, Point.deserialize, "3.4.3;5.7")

    def test_operator_methods(self):
        a = Point(3, 4)
        self.failUnlessEqual(Point(23.0, 12.0), Point(23, 12))      # Equals
        self.failUnlessEqual(-a, Point(-3, -4))                     # Negation
        self.failUnlessEqual(a - Point(1, 1.5), Point(2.0, 2.5))    # Subtraction
        self.failUnlessEqual(a + Point(1, 1.5), Point(4, 5.5))      # Addition
        self.failUnlessEqual(a * 2, Point(6, 8))                    # Multiplication
        self.failUnlessEqual(a / 2, Point(1.5, 2.0))                # Division
        self.failUnlessEqual((a // int(2)), Point(1, 2))            # Floor division
        self.failUnlessEqual((a / float(2)), Point(1.5, 2))         # True division
        self.failUnlessEqual(str(a), "(3.00, 4.00)")                # Print to string
        self.failUnlessEqual(repr(a), "Point(3, 4)")                # Represent to string

    def test_operator_method_with_invalid_type_returns_false(self):
        self.validate_code_throws_type_error_exception("Point(3, 4) + 3.0")
        self.validate_code_throws_type_error_exception("Point(3, 4) - 3.0")

    def test_equal_comparison_with_invalid_type_returns_false(self):
        self.failIf(Point(3, 4) == 3.0)

    def validate_code_throws_type_error_exception(self, code_with_exception):
        with self.failUnlessRaises(TypeError):
            eval(code_with_exception)
