import unittest

from unittest.mock import patch

import pyocr

from pyocr.util import (
    digits_only,
)


class TestPyOCR(unittest.TestCase):

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    @patch("pyocr.libtesseract.tesseract_raw.is_available")
    @patch("shutil.which")
    def test_available_tools_tesseract4(self, which, is_available, libtess):
        which.return_value = True
        is_available.return_value = True
        libtess.TessVersion.return_value = b"4.0.0"
        self.assertListEqual(
            pyocr.get_available_tools(),
            [
                pyocr.tesseract,
                pyocr.libtesseract,
                pyocr.cuneiform,
            ]
        )

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    @patch("pyocr.libtesseract.tesseract_raw.is_available")
    @patch("shutil.which")
    def test_available_tools_tesseract3(self, which, is_available, libtess):
        which.return_value = True
        is_available.return_value = True
        libtess.TessVersion.return_value = b"3.5.0"
        self.assertListEqual(
            pyocr.get_available_tools(),
            [
                pyocr.tesseract,
                pyocr.libtesseract,
                pyocr.cuneiform,
            ]
        )

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    @patch("pyocr.libtesseract.tesseract_raw.is_available")
    @patch("shutil.which")
    def test_available_tools_tesseract3_0(self, which, is_available, libtess):
        which.return_value = True
        is_available.return_value = True
        libtess.TessVersion.return_value = b"3.0.0"
        self.assertListEqual(
            pyocr.get_available_tools(),
            [
                pyocr.tesseract,
                pyocr.cuneiform,
            ]
        )

    def test_digits_only(self):
        self.assertEqual(digits_only("azer"), 0)
        self.assertEqual(digits_only("10.0.1"), 10)
        self.assertEqual(digits_only("42azer"), 42)
        self.assertEqual(digits_only("qsdf42azer"), 42)
        self.assertEqual(digits_only("v42"), 42)
        self.assertEqual(digits_only("v42x35"), 42)
        self.assertEqual(digits_only("v42x35qsdf"), 42)
