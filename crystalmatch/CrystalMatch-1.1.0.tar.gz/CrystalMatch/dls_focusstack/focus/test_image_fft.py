from pkg_resources import require
require("pygelf>=0.3.1")
require("numpy>=1.11.1")
require("scipy>=0.19.1")

from unittest import TestCase

import numpy as np

from CrystalMatch.dls_focusstack.focus.imagefft import ImageFFT


class TestImageFFT(TestCase):

    def setUp(self):
        self._img = np.array([(0, 2, 3, 4),
                        (1, 3, 4, 5),
                        (1, 0, 2, 5)])


    def test_getFFT_returns_none_before_furrier_is_run(self):
        sh = ImageFFT(self._img, 1, 'test')
        self.assertIsNone(sh.getFFT())

    def test_getFFT_returns_furrier_when_its_set(self):
        sh = ImageFFT(self._img, 1, 'test')
        fft = 10
        sh.setFFT(fft)
        self.assertEquals(sh.getFFT(), fft)

    def test_get_image_number_returns_correct_value(self):
        img_num = 3
        sh = ImageFFT(self._img, img_num, 'test')
        self.assertEqual(sh.get_image_number(), img_num)

    def test_get_image_returns_correct_value(self):
        sh = ImageFFT(self._img, 1, 'test')
        self.assertIn(sh.get_image(), self._img)

    def test_get_image_name_returns_name_correctly(self):
        img_name = 'test'
        sh = ImageFFT(self._img, 1, img_name)
        self.assertEquals(sh.get_image_name(), img_name)








