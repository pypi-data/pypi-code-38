from copy import deepcopy

from pkg_resources import require
require("numpy>=1.11.1")
require("scipy>=0.19.1")
require("mock>=1.0.1")

from unittest import TestCase

from CrystalMatch.dls_focusstack.focus.pyramid_collection import fused_laplacian, entropy_diviation, PyramidCollection

from CrystalMatch.dls_focusstack.focus.pyramid import Pyramid
from CrystalMatch.dls_focusstack.focus.pyramid_level import PyramidLevel

import numpy as np
from mock import MagicMock


class TestPyramid(TestCase):

    def setUp(self):

        pyr = Pyramid(12, 3)
        level_0 = PyramidLevel(np.array([[10, 10, 10, 10], [2, 2, 2, 2], [4, 4, 4, 4], [4, 4, 4, 4]], dtype=np.float64), 2, 2)
        level_1 = PyramidLevel(np.array([[2, 2], [3, 3]], dtype=np.float64), 2, 1)
        level_2 = PyramidLevel(np.array([[0]], dtype=np.float64), 2, 0)
        pyr.add_lower_resolution_level(level_0)
        pyr.add_lower_resolution_level(level_1)
        pyr.add_lower_resolution_level(level_2)

        pyr1 = deepcopy(pyr)
        self._kernel_size = 5
        self._pyramid_collection = PyramidCollection()
        self._pyramid_collection.add_pyramid(pyr)
        self._pyramid_collection.add_pyramid(pyr1)

    def test_fuse_does_not_change_the_depth_of_the_pyramid(self):
        collection_layer_0 = self._pyramid_collection.get_pyramid(0)
        fused = self._pyramid_collection.fuse(self._kernel_size)
        self.assertEquals(collection_layer_0.get_depth(), fused.get_depth())

    def test_fused_laplacian_of_level0_has_size_of_input_level0(self):
        laplacians_level0 = np.zeros((2, 4, 4), dtype=np.float64)
        laplacians_level0[0] = self._pyramid_collection.get_pyramid(0).get_level(0).get_array()
        laplacians_level0[1] = self._pyramid_collection.get_pyramid(1).get_level(0).get_array()
        param = (laplacians_level0, self._pyramid_collection.get_region_kernel(), 2)
        fused_level = fused_laplacian(param)
        self.assertEquals(fused_level.get_array().shape, laplacians_level0[0].shape)

    def test_entropy_deviation_calls_entropy_and_deviation_once(self):
        layer = MagicMock()
        param = (layer, self._pyramid_collection.get_region_kernel())
        entropy_diviation(param)
        layer.entropy.assert_called_once()
        layer.deviation.assert_called_once()
