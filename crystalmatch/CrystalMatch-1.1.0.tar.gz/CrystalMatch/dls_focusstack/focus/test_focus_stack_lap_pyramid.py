from pkg_resources import require
require("pygelf>=0.3.1")
require("numpy>=1.11.1")
require("scipy>=0.19.1")
require("mock>=1.0.1")

import cv2
import os
from unittest import TestCase

from mock import MagicMock, Mock
from CrystalMatch.dls_focusstack.focus.focus_stack_lap_pyramid import FocusStack


class TestFocusStackLapPyramid(TestCase):

    def test_focus_stack_results_in_one_rgb_image_of_input_image_size(self):
        self._file1 = MagicMock()
        self._file2 = MagicMock()
        CONFIG_DIR = os.path.join("config")
        dict = os.path.join(".", "system-tests", "resources")
        self._file1.name = os.path.join(dict, "A02.jpg")
        self._file2.name = os.path.join(dict, "A03.jpg")
        file_list = [self._file1, self._file2]
        fs = FocusStack(file_list, CONFIG_DIR)
        result_img = fs.composite()

        self.assertIsNotNone(result_img)
        img = cv2.imread(self._file1.name)
        self.assertEqual(result_img.channels(), 3) #rgb
        self.assertEqual(result_img.size(), (img.shape[1],img.shape[0]))

