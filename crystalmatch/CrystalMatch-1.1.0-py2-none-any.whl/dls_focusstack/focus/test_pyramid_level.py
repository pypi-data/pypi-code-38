from pkg_resources import require

require("numpy>=1.11.1")
require("scipy>=0.19.1")
require("mock>=1.0.1")
from unittest import TestCase

from CrystalMatch.dls_focusstack.focus.pyramid_level import PyramidLevel

import numpy as np


class TestPyramidLayer(TestCase):

    def setUp(self):
        #case1
        self._array = np.array([[10, 20, 30, 40], [10, 20, 30, 40], [11, 21, 31, 41], [12, 22, 32, 42]],
                               dtype=np.float64)

    def test_something(self):
        lap_layer0 = PyramidLevel(self._array, 0, 0)
        self.assertEquals(lap_layer0.get_layer_number(),0)

    def test_get_probabilities_has_always_size_of_256(self):
        probablities = PyramidLevel(self._array, 0, 0).get_probabilities()
        self.assertEquals(len(probablities),256)

    def test_get_probablities_returns_correct_value_for_chosen_grey_levels(self):
        probablities = PyramidLevel(self._array, 0, 0).get_probabilities()
        self.assertEquals(probablities[10], 0.125)  #two tens and 16 elements of an array 2/16
        self.assertEquals(probablities[20], 0.125)
        self.assertEquals(probablities[11], 0.0625) #1/16

    def test_get_entropies_dont_change_array_size(self):
        layer = PyramidLevel(self._array, 0, 0)
        layer.entropy(5)
        entropies = layer.get_entropies()
        self.assertEquals(entropies.shape, self._array.shape)

    def test_entropies_calculated_locally_in_a_kernel_match_value_returned_by_get_entropies(self):
        layer = PyramidLevel(self._array, 0, 0)
        pro = layer.get_probabilities()
        layer.entropy(3)
        entropies = layer.get_entropies()
        entropy = entropies[1][1] #
        local_area = np.array([[10, 20, 30], [10, 20, 30], [11, 21, 31]],
                               dtype=np.float64) #local area corresponding to point point 1,1 in entropies
        local_entropy = layer._area_entropy(local_area,pro)
        self.assertEquals(entropy, local_entropy)
        #check the value  as well
        self.assertEquals(round(local_entropy), 424)

        entropy1 = entropies[2][1]  #
        local_area1 = np.array([[10, 20, 30], [11, 21, 31], [12, 22, 32]],
                              dtype=np.float64)  # local area corresponding to point point 1,1 in entropies
        local_entropy1 = layer._area_entropy(local_area1, pro)
        self.assertEquals(entropy1, local_entropy1)
        # check the value  as well
        self.assertEquals(round(local_entropy1), 482)


    def test_get_deviation_dont_change_array_size(self):
        layer = PyramidLevel(self._array, 0, 0)
        layer.deviation(5)
        dev = layer.get_deviations()
        self.assertEquals(dev.shape, self._array.shape)

    def test_deviations_calculated_locally_in_a_kernel_match_value_returned_by_get_deviations(self):
        layer = PyramidLevel(self._array, 0, 0)
        layer.deviation(3)
        dev = layer.get_deviations()
        deviation = dev[1][1] #
        local_area = np.array([[10, 20, 30], [10, 20, 30], [11, 21, 31]],
                               dtype=np.float64) #local area corresponding to point point 1,1 in entropies
        local_deviation = layer._area_deviation(local_area)
        self.assertEquals(deviation, local_deviation)
        #check the value  as well
        self.assertEquals(round(local_deviation,3), 66.889)

        deviation1 = dev[2][1]  #
        local_area1 = np.array([[10, 20, 30], [11, 21, 31], [12, 22, 32]],
                              dtype=np.float64)  # local area corresponding to point point 1,1 in entropies
        local_deviation1 = layer._area_deviation(local_area1)
        self.assertEquals(deviation1, local_deviation1)
        # check the value  as well
        self.assertEquals(round(local_deviation1,3), 67.333)

    def test_padding_adds_padding_of_expected_size(self):
        layer = PyramidLevel(self._array, 0, 0)
        kernel_size = 3
        pad_am, pad_img, offset = layer.padding(kernel_size)
        self.assertEquals(pad_img.shape[0], self._array.shape[0] + 2) # one pixel each side
        self.assertEquals(pad_img.shape[1], self._array.shape[1] + 2)
        #the elements added are  mirrored
        pad_column = np.array(pad_img[:][0])
        column_org = pad_column[1:-1]
        self.assertIn(self._array[:][1], column_org)
        pad_row = np.array(pad_img[0][:])
        row_org = pad_row[1:-1]
        self.assertIn(self._array[1][:], row_org)
        #the padding and mirroring is applied to columns first
        #the corner values are mirrored from the new column when rows are processed
        bottom_corner = np.array(pad_img[-1][0])
        source_of_the_bottom_corner_value = np.array(pad_img[-3][0])
        self.assertEquals(bottom_corner,source_of_the_bottom_corner_value)
































