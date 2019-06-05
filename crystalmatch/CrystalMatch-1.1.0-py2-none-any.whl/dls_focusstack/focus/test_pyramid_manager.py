from pkg_resources import require
require("pygelf>=0.3.1")
require("numpy>=1.11.1")
require("scipy>=0.19.1")
require("mock>=1.0.1")

from unittest import TestCase

import numpy as np

from CrystalMatch.dls_focusstack.focus.pyramid_manager import PyramidManager

from mock import MagicMock


class TestPyramidManager(TestCase):

    def setUp(self):
        #case1
        self._config = MagicMock()
        self._array = np.array([[10, 20, 30, 40], [10, 20, 30, 40], [11, 21, 31, 41], [12, 22, 32, 42]],
                               dtype=np.float64)
        self._depth = 2
        self._images = np.array([self._array, self._array / 10])
        #case2
        self._array1 = np.array([[10, 20, 30], [10, 20, 30], [11, 21, 31], [12, 22, 32]],
                               dtype=np.float64)
        self._images1 = np.array([self._array1, self._array1 / 10])


    def test_gaussian_pyramid_colletion_has_correct_size(self):
        #gaussian pyramid
        p_collection = PyramidManager(self._images, self._config)._gaussian_pyramid(self._depth)
        # number of layers in the collection
        self.assertEquals(p_collection.get_number_of_layers(), 2)
        collection_layer_0 = p_collection.get_pyramid(0)
        # high of the pyramid in the collection
        self.assertEquals(collection_layer_0.get_depth(), self._depth)
        # zero level of the pyramid is made out of input images
        self.assertIn(collection_layer_0.get_level(0).get_array(), self._images[0])
        # sieze of first level is half of level zero
        self.assertEquals(collection_layer_0.get_level(1).get_array().shape, (2,2))

    def test_laplacian_has_correct_size(self):
        # gaussian pyramid
        p_collection = PyramidManager(self._images, self._config).laplacian_pyramid(self._depth)
        # number of layers in the collection
        self.assertEquals(p_collection.get_number_of_layers(), 2)
        collection_layer_0 = p_collection.get_pyramid(0)
        # high of the pyramid in the collection
        self.assertEquals(collection_layer_0.get_depth(), self._depth)
        # sieze of first level is half of level zero
        self.assertEquals(collection_layer_0.get_level(1).get_array().shape, (2, 2))

    def test_top_level_of_laplacian_and_gaussian_pyramids_are_the_same(self):
        l = PyramidManager(self._images, self._config).laplacian_pyramid(self._depth).get_pyramid(0)
        p = PyramidManager(self._images, self._config)._gaussian_pyramid(self._depth).get_pyramid(0)
        #top level
        self.assertIn(l.get_top_level().get_array(), p.get_top_level().get_array())

    def test_that_the_top_of_pyramids_has_the_lowest_resolution(self):
        l = PyramidManager(self._images, self._config).laplacian_pyramid(self._depth).get_pyramid(0)
        p = PyramidManager(self._images, self._config)._gaussian_pyramid(self._depth).get_pyramid(0)
        # top level has lowest resolution
        self.assertLess(l.get_top_level().array.shape[0], l.get_level(0).array.shape[0])
        # top level has lowest resolution
        self.assertLess(p.get_top_level().array.shape[0], p.get_level(0).array.shape[0])

    def test_get_pyramid_fusion_calls_laplacian_pyramid_once(self):
        self._config.pyramid_min_size.value.return_value = 1
        p = PyramidManager(self._images, self._config)
        p.laplacian_pyramid = MagicMock(return_value = MagicMock())
        p.get_pyramid_fusion()
        p.laplacian_pyramid.assert_called_once()

