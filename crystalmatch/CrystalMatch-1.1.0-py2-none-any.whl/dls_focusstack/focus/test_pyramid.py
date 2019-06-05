from pkg_resources import require
require("numpy>=1.11.1")
require("scipy>=0.19.1")
require("mock>=1.0.1")
from unittest import TestCase

from CrystalMatch.dls_focusstack.focus.pyramid_level import PyramidLevel
from CrystalMatch.dls_focusstack.focus.pyramid import Pyramid

import numpy as np

class TestPyramidLayer(TestCase):

    def test_get_layer_number_returns_correct_value(self):
        layer_number = 10
        pyr = Pyramid(layer_number,10)
        self.assertEquals(pyr.get_layer_number(), layer_number)

    def test_get_depth_returns_correct_value(self):
        depth = 12
        pyr = Pyramid(10, depth)
        self.assertEquals(pyr.get_depth(),depth)

    def test_add_lower_resolution_level_adds_new_element_on_the_end_of_level_list(self):
        pyr = Pyramid(10, 2)
        pyr.add_lower_resolution_level(10)
        self.assertEquals(len(pyr.levels), 1)
        pyr.add_lower_resolution_level(12)
        self.assertEquals(len(pyr.levels),2)
        self.assertEquals(pyr.levels[0], 10)
        self.assertEquals(pyr.levels[1], 12)

    def test_add_higher_resolution_level_adds_new_element_in_front_of_the_level_list(self):
        pyr = Pyramid(10, 2)
        pyr.add_higher_resolution_level(10)
        self.assertEquals(len(pyr.levels), 1)
        pyr.add_higher_resolution_level(12)
        self.assertEquals(len(pyr.levels),2)
        self.assertEquals(pyr.levels[1], 10)
        self.assertEquals(pyr.levels[0], 12)

    def test_get_level_returns_the_correct_list_element(self):
        pyr = Pyramid(10,3)
        pyr.levels = [12,13,14]
        self.assertEquals(pyr.get_level(1), 13)
        self.assertEquals(pyr.get_level(0), 12)

    def test_get_top_level_returns_the_last_element_form_the_level_list(self):
        pyr = Pyramid(10, 3)
        pyr.levels = [12, 13, 14]
        self.assertEquals(pyr.get_top_level(), 14)

    def test_sort_levels_sorts_levels_according_to_size_larger_first(self):
        pyr = Pyramid(12,3)
        level_0 = PyramidLevel(np.array([[10, 10, 10], [2, 2, 2], [4, 4, 4] ],dtype=np.float64),2,2)
        level_1 = PyramidLevel(np.array([[2, 2], [3, 3]], dtype=np.float64),2,2)
        level_2 = PyramidLevel(np.array([0],dtype=np.float64 ),1,1)
        pyr.add_lower_resolution_level(level_1)
        pyr.add_lower_resolution_level(level_0)
        pyr.add_lower_resolution_level(level_2)
        self.assertEquals(pyr.get_level(0).get_array().shape, level_1.get_array().shape)
        pyr.sort_levels()
        self.assertEquals(pyr.get_level(0).get_array().shape, level_0.get_array().shape)

    def test_collapse_returns_an_array_of_the_same_size_as_the_bottom_level(self):
        pyr = Pyramid(12, 3)
        level_0 = PyramidLevel(np.array([[10, 10, 10], [2, 2, 2], [4, 4, 4]], dtype=np.float64), 2, 2)
        level_1 = PyramidLevel(np.array([[2, 2], [3, 3]], dtype=np.float64), 2, 2)
        level_2 = PyramidLevel(np.array([0], dtype=np.float64), 1, 1)
        pyr.add_lower_resolution_level(level_1)
        pyr.add_lower_resolution_level(level_0)
        pyr.add_lower_resolution_level(level_2)
        pyr.sort_levels()
        result = pyr.collapse()
        self.assertEquals(result.shape, level_0.get_array().shape)

    def test_collapse_returns_sum_of_a_level_and_extended_upper_level(self):
        pyr = Pyramid(12, 3)
        level_0 = PyramidLevel(np.array([[2, 2], [3, 3]], dtype=np.float64), 2, 2)
        level_1 = PyramidLevel(np.array([[0]], dtype=np.float64), 1, 1)
        pyr.add_lower_resolution_level(level_0)
        pyr.add_lower_resolution_level(level_1)
        result = pyr.collapse()
        self.assertIn(result, level_0.get_array())






























