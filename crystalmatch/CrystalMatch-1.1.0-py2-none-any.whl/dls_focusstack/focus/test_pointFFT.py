from pkg_resources import require
require("mock>=1.0.1")
from unittest import TestCase

import numpy as np

from mock import Mock

from CrystalMatch.dls_focusstack.focus.pointfft import PointFFT
from CrystalMatch.dls_util.shape import Point


class TestPointFFT(TestCase):

    def setUp(self):
        self.pointfft = PointFFT(Mock(), Mock(), Mock())

    def test_set_fft_sets_the_fft_value_correctly(self):
        self.assertIsNone(self.pointfft.fft_level)
        self.pointfft.setFFT(10)
        self.assertEquals(self.pointfft.fft_level, 10)

    def test_getFFT_returns_the_fft_value_correctly(self):
        self.pointfft.setFFT(10)
        self.assertEquals(self.pointfft.getFFT(), 10)

    def test_crop_region_from_image_cuts_square_region_of_given_size(self):
        image = np.zeros((10, 10), dtype=np.float64)
        pointfft = PointFFT(Point(5,5), image, 2)
        region = pointfft.crop_region_from_image()
        self.assertEquals(region.size, 4)

    def test_set_get_image_number_works_fine(self):
        image_number = 100
        self.pointfft.set_image_number(image_number)
        self.assertEquals(self.pointfft.image_number, image_number)
        self.assertEquals(self.pointfft.get_image_number(), image_number)

    def test_set_get_image_name_works_fine(self):
        image_name = 'test_name'
        self.pointfft.set_image_name(image_name)
        self.assertEquals(self.pointfft.image_name, image_name)
        self.assertEquals(self.pointfft.get_image_name(), image_name)