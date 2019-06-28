from unittest import TestCase

from CrystalMatch.dls_util.shape.point import Point
from CrystalMatch.dls_util.shape.polygon import Polygon
from CrystalMatch.dls_util.shape.rectangle import Rectangle


class TestPolygon(TestCase):

    def setUp(self):
        self.point_a = Point(2, 3)
        self.point_b = Point(4, 5)
        self.point_c = Point(6, 7)
        self.valid_vertex_array = [self.point_a, self.point_b, self.point_c]

    def test_polygon_must_have_3_or_more_vertices(self):
        self.assertTrue(Polygon(self.valid_vertex_array))
        self.assertRaises(ValueError, Polygon, [])
        self.assertRaises(ValueError, Polygon, [self.point_a, self.point_b])

    def test_polygon_vertices_must_be_points(self):
        self.assertRaises(TypeError, Polygon, [(3, 4), (4, 5), (6, 7)])
        self.assertRaises(TypeError, Polygon, [Point(3, 4), (4, 5), (6, 7)])

    def test_retrieve_list_of_vertices(self):
        polygon = self.basic_polygon()
        self.assertEqual(self.valid_vertex_array, polygon.vertices())

    def basic_polygon(self):
        polygon = Polygon(self.valid_vertex_array)
        return polygon

    def test_count_vertices(self):
        polygon = self.basic_polygon()
        self.assertEqual(3, polygon.num_vertices())

    def test_offset_transform_of_polygon(self):
        self.validate_offset_for_polygon(Point(3, 4))
        self.validate_offset_for_polygon(Point(3.2, -5.3))
        self.validate_offset_for_polygon(Point(300, -234))

    def validate_offset_for_polygon(self, offset):
        polygon = Polygon(self.valid_vertex_array).offset(offset)
        expected = Polygon([self.point_a + offset, self.point_b + offset, self.point_c + offset])
        self.assertEqual(expected, polygon)

    def test_attempt_to_offset_with_non_point_value_throws_exception(self):
        self.assertRaises(TypeError, self.basic_polygon() .offset, 5)
        self.assertRaises(TypeError, self.basic_polygon().offset, -5)

    def test_attempt_to_compare_polygon_with_invalid_type_returns_false(self):
        self.assertFalse(self.basic_polygon() == 4.0)

    def test_scale_transform(self):
        self.validate_scale_for_polygon(0.5)
        self.validate_scale_for_polygon(100)
        self.validate_scale_for_polygon(-3)

    def validate_scale_for_polygon(self, scale_factor):
        polygon = Polygon(self.valid_vertex_array).scale(scale_factor)
        expected = Polygon([self.point_a.scale(scale_factor),
                            self.point_b.scale(scale_factor),
                            self.point_c.scale(scale_factor)])
        self.assertEqual(expected, polygon)

    def test_ordered_return_list_of_edges_in_polygon(self):
        polygon = self.basic_polygon()
        edges = polygon.edges()
        expected = [[self.point_a, self.point_b],
                    [self.point_b, self.point_c],
                    [self.point_c, self.point_a]]
        self.assertEqual(expected, edges)

    def test_create_polygon_from_rectangle(self):
        rectangle = Rectangle(Point(1, 1), Point(4, 4))
        expected = Polygon([Point(1, 1), Point(4, 1), Point(4, 4), Point(1, 4)])
        self.assertEqual(expected, Polygon.from_rectangle(rectangle))
