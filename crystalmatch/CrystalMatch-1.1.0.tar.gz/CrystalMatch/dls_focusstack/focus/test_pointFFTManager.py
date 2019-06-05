from pkg_resources import require
require("mock>=1.0.1")
from unittest import TestCase

import numpy as np
from mock import Mock, MagicMock

from CrystalMatch.dls_focusstack.focus.point_fft_manager import PointFFTManager
from CrystalMatch.dls_util.shape import Point


class TestPointFFTManager(TestCase):

    def test_find_z_level_for_point_returns_img_number(self):
        img =MagicMock(get_image = Mock(return_value = np.ones((30,30),dtype=np.float64)),
                       get_image_number = Mock(return_value = 1),
                       get_image_name = Mock(return_value = 'test1')
                       )
        fft_images = [img]
        poi =  Point(15,15)
        region_size = 10
        number = PointFFTManager(fft_images, poi, region_size).find_z_level_for_point()
        self.assertEquals(number, 1)

    def test_find_z_level_for_point_returns_number_of_img_with_higier_fft(self):
        img =MagicMock(get_image=Mock(return_value=np.ones((30,30),dtype=np.float64)),
                       get_image_number=Mock(return_value=10),
                       get_image_name=Mock(return_value='test1')
                       )

        img1 = MagicMock(get_image=Mock(return_value=np.zeros((30,30),dtype=np.float64)),
                        get_image_number=Mock(return_value=0),
                        get_image_name=Mock(return_value='test2')
                        )

        fft_images = [img, img1]
        poi =  Point(15,15)
        region_size = 10
        number = PointFFTManager(fft_images, poi, region_size).find_z_level_for_point()
        self.assertEquals(number, 10)

    def test_find_z_level_for_point_very_close_to_image_edge(self):
        img = MagicMock(get_image=Mock(return_value=np.ones((30, 30), dtype=np.float64)),
                        get_image_number=Mock(return_value=1),
                        get_image_name=Mock(return_value='test1')
                        )
        fft_images = [img]
        poi = Point(1, 1)
        region_size = 10
        number = PointFFTManager(fft_images, poi, region_size).find_z_level_for_point()
        self.assertEquals(number, 1)
