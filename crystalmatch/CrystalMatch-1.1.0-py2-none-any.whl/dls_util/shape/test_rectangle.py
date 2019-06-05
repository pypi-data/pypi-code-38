from unittest import TestCase

from CrystalMatch.dls_util.shape.point import Point
from CrystalMatch.dls_util.shape.rectangle import Rectangle


class TestRectangle(TestCase):
    def setUp(self):
        self.RECT_CORNER_TEST_CASES = [(Point(0, 0), Point(0, 0)),
                                       (Point(0, 0), Point(1, 1)),
                                       (Point(0, 0), Point(50, 20)),
                                       (Point(-22.4, -57.98), Point(-10, 154.3)),
                                       (Point(10, -11), Point(15, -20))]

        self.POINT_TEST_CASES = [Point(0, 0),
                                 Point(1, 1),
                                 Point()]
        self.basic_rectangle = Rectangle(Point(2, 3), Point(12, 16))

    def test_init_with_negative_floats(self):
        rec = Rectangle(Point(-3, -0.54), Point(45, -26.78))
        self.failUnlessEqual([rec.x1, rec.x2, rec.y1, rec.y2], [-3, 45, -26.78, -0.54])

    def test_create_rectangle_from_array(self):
        expected = Rectangle(Point(1, 2), Point(3, 4))
        actual = Rectangle.from_array([1, 2, 3, 4])
        self.failUnlessEqual(expected, actual)

    def test_creating_rectangle_from_array_with_incorrect_number_of_values_raises_exception(self):
        self.failUnlessRaises(ValueError, Rectangle.from_array, [1, 2, 3])
        self.failUnlessRaises(ValueError, Rectangle.from_array, [1, 2, 3, 4, 5])
        self.failUnlessRaises(ValueError, Rectangle.from_array, [])

    def test_corners_always_sorted_in_ascending_order(self):
        rec = Rectangle(Point(45, -0.54), Point(-3, 26.78))
        self.failUnlessEqual([rec.x1, rec.x2, rec.y1, rec.y2], [-3, 45, -0.54, 26.78])

    def test_zero_area_square_can_exist(self):
        rec = Rectangle(Point(0, 0), Point(0, 0))
        self.failUnlessEqual(0.0, rec.area())

    def test_string_representation_of_rectangle(self):
        self.failUnlessEqual("Rectangle - (x1: 2.00, y1: 3.00); (x2: 12.00, y2: 16.00)", str(self.basic_rectangle))

    def test_corners_and_dimensions_correctly_calculated(self):
        for corner1, corner2 in self.RECT_CORNER_TEST_CASES:
            # Arrange
            rect = Rectangle(corner1, corner2)

            x1 = min(corner1.x, corner2.x)
            x2 = max(corner1.x, corner2.x)
            y1 = min(corner1.y, corner2.y)
            y2 = max(corner1.y, corner2.y)
            width = x2 - x1
            height = y2 - y1

            # Check dimensions
            self.assertEquals(rect.width(), width)
            self.assertEquals(rect.height(), height)
            self.assertEquals(rect.area(), width * height)

            # Test that all corners are correct
            self.assertEqual(rect.top_left().x, x1)
            self.assertEquals(rect.top_left().y, y1)
            self.assertEquals(rect.bottom_left().x, x1)
            self.assertEquals(rect.bottom_left().y, y2)
            self.assertEquals(rect.top_right().x, x2)
            self.assertEquals(rect.top_right().y, y1)
            self.assertEquals(rect.bottom_right().x, x2)
            self.assertEquals(rect.bottom_right().y, y2)

    def test_center_point_correctly_calculated(self):
        for corner1, corner2 in self.RECT_CORNER_TEST_CASES:
            # Arrange
            rect = Rectangle(corner1, corner2)

            center_x = (corner1.x + corner2.x) / 2.0
            center_y = (corner1.y + corner2.y) / 2.0

            self.assertAlmostEquals(rect.center().x, center_x)
            self.assertAlmostEquals(rect.center().y, center_y)

    def test_offset_transform_returns_correct_result(self):
        rectangle = Rectangle(Point(-1, -1), Point(1, 1))
        self.failUnlessEqual(Rectangle(Point(2, 3), Point(4, 5)), rectangle.offset(Point(3, 4)))
        self.failUnlessEqual(Rectangle(Point(-3, -4), Point(-1, -2)), rectangle.offset(Point(-2, -3)))

    def test_offset_transform_without_non_point_value_throws_exception(self):
        self.failUnlessRaises(TypeError, self.basic_rectangle.offset, (3, 5))

    def test_equality(self):
        self.failUnless(Rectangle(Point(2, 3), Point(12, 16)) == self.basic_rectangle)
        self.failIf(Rectangle(Point(1, 3), Point(12, 16)) == self.basic_rectangle)
        self.failIf(Rectangle(Point(2, 1), Point(12, 16)) == self.basic_rectangle)
        self.failIf(Rectangle(Point(2, 3), Point(1, 16)) == self.basic_rectangle)
        self.failIf(Rectangle(Point(2, 3), Point(12, 1)) == self.basic_rectangle)

    def test_equality_comparison_with_non_rectangle_value_returns_false(self):
        self.failIf(self.basic_rectangle.__eq__(4.5))
        self.failIf(self.basic_rectangle.__eq__(Point(3, 4)))
        self.failIf(self.basic_rectangle.__eq__("Hello world"))

    def test_scale_transform_returns_correct_result(self):
        rectangle = Rectangle(Point(-1, -1), Point(1, 1))
        self.failUnlessEqual(Rectangle(Point(-0.5, -0.5), Point(0.5, 0.5)), rectangle.scale(0.5))
        self.failUnlessEqual(Rectangle(Point(-3, -3), Point(3, 3)), rectangle.scale(3))
        self.failUnlessEqual(Rectangle(Point(3.5, 3.5), Point(-3.5, -3.5)), rectangle.scale(-3.5))

    def test_intersect_test_returns_true_for_intersecting_rectangles(self):
        self.failUnless(Rectangle(Point(-1, -1), Point(2, 2))
                        .intersects(Rectangle(Point(-2, -2), Point(1, 1))))
        self.failUnless(Rectangle(Point(-0.99, -0.99), Point(-2, -2))
                        .intersects(Rectangle(Point(-1.01, -1.01), Point(1, 1))))

    def test_intersect_test_returns_true_for_rectangles_which_share_a_side(self):
        self.failUnless(Rectangle(Point(-1, -1), Point(-2, 1))
                        .intersects(Rectangle(Point(-1, -1), Point(1, 1))))

    def test_intersect_test_returns_false_for_non_intersecting_rectangles(self):
        self.failIf(Rectangle(Point(-1.01, -1.01), Point(-2, -2))
                    .intersects(Rectangle(Point(-0.99, -0.99), Point(1, 1))))

    def test_intersect_test_with_non_rectangle_object_throws_exception(self):
        self.failUnlessRaises(TypeError, Rectangle(Point(-1, -1), Point(-2, 1)).intersects, 5.6)
        self.failUnlessRaises(TypeError, Rectangle(Point(-1, -1), Point(-2, 1)).intersects, "Hello World")
        self.failUnlessRaises(TypeError, Rectangle(Point(-1, -1), Point(-2, 1)).intersects, Point(3, 4))

    def test_intersection_creates_new_rectangle_with_correct_corners(self):
        expected = Rectangle.from_array([-1, -1, 2, 2])
        actual = Rectangle.from_array([-1, -1, 13, 8]).intersection(Rectangle.from_array([2, 2, -13, -7]))
        self.failUnlessEqual(expected, actual)
        actual = Rectangle.from_array([-1, 8, 13, -1]).intersection(Rectangle.from_array([2, -7, -13, 2]))
        self.failUnlessEqual(expected, actual)

    def test_intersection_returns_zero_area_rectangle_when_rectangles_do_not_intersect(self):
        expected = Rectangle.from_array([0, 0, 0, 0])
        actual = Rectangle.from_array([1, 1, 2, 2]).intersection(Rectangle.from_array([5, 5, 6, 6]))
        self.failUnlessEqual(expected, actual)
        self.failUnlessEqual(actual.area(), 0)

    def test_intersection_with_non_rectangle_object_throws_exception(self):
        self.failUnlessRaises(TypeError, Rectangle(Point(-1, -1), Point(-2, 1)).intersection, 5.6)
        self.failUnlessRaises(TypeError, Rectangle(Point(-1, -1), Point(-2, 1)).intersection, "Hello World")
        self.failUnlessRaises(TypeError, Rectangle(Point(-1, -1), Point(-2, 1)).intersection, Point(3, 4))

    def test_corners_returns_a_list_of_valid_point_objects(self):
        corners = self.basic_rectangle.corners()
        # Test by creating using alternating corners to reconstruct the original Rectangle.
        self.failUnlessEqual(len(corners), 4)
        self.failUnlessEqual(self.basic_rectangle, Rectangle(corners[0], corners[2]))
        self.failUnlessEqual(self.basic_rectangle, Rectangle(corners[1], corners[3]))

    def test_conversion_to_integer(self):
        expected = Rectangle.from_array([1, 3, 4, 5])
        actual = Rectangle.from_array([1.4, 2.5, 3.7, 4.99]).intify()
        self.failUnlessEqual(expected, actual)
        self.failUnless(isinstance(actual.x1, int))
        self.failUnless(isinstance(actual.x2, int))
        self.failUnless(isinstance(actual.y1, int))
        self.failUnless(isinstance(actual.y2, int))

    def test_conversion_to_float(self):
        actual = Rectangle.from_array([1, 2, 3, 4]).floatify()
        self.failUnless(isinstance(actual.x1, float))
        self.failUnless(isinstance(actual.x2, float))
        self.failUnless(isinstance(actual.y1, float))
        self.failUnless(isinstance(actual.y2, float))

    def test_create_rectangle_from_centre(self):
        expected = Rectangle.from_array([-1, -1, 1, 1])
        actual = Rectangle.from_center(Point(0, 0), 2, 2)
        self.failUnlessEqual(expected, actual)

    def test_create_rectangle_from_corner(self):
        expected = Rectangle.from_array([-15, 22, 35, 95])
        actual = Rectangle.from_corner(Point(-15, 22), 50, 73)
        self.failUnlessEqual(expected, actual)

    def test_creating_rectangle_from_centre_with_invalid_type_raises_exception(self):
        self.failUnlessRaises(ValueError, Rectangle.from_center, "not_a_Point", 2, 2)
        self.failUnlessRaises(ValueError, Rectangle.from_center, 0.5, 2, 2)
        self.failUnlessRaises(ValueError, Rectangle.from_center, None, 2, 2)

    def test_creating_rectangle_from_corner_with_invalid_type_raises_exception(self):
        self.failUnlessRaises(ValueError, Rectangle.from_corner, "not_a_Point", 50, 73)
        self.failUnlessRaises(ValueError, Rectangle.from_corner, 0.5, 50, 73)
        self.failUnlessRaises(ValueError, Rectangle.from_corner, None, 50, 73)
