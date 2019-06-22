import locale
import os

from ctypes import POINTER, cast, c_char_p, c_int
from random import randint
from unittest.mock import patch, call

from PIL import Image

from pyocr import builders
from pyocr import libtesseract
from pyocr.error import TesseractError
from pyocr.libtesseract import tesseract_raw

from .tests_base import BaseTest


class TestLibTesseract(BaseTest):
    """
    These tests make sure the requirements for the tests are met.
    """
    def setUp(self):
        self.handle = randint(0, 2**32-1)
        self.image = Image.new(mode="RGB", size=(1, 1))

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_available(self, libtess):
        libtess.TessVersion.return_value = b"4.0.0"
        self.assertTrue(libtesseract.is_available())
        libtess.TessVersion.assert_called_once_with()

    @patch("pyocr.libtesseract.tesseract_raw")
    def test_not_available(self, raw):
        raw.is_available.return_value = False
        self.assertFalse(libtesseract.is_available())
        raw.is_available.assert_called_once_with()

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_not_available_tesseract3(self, libtess):
        libtess.TessVersion.return_value = b"3.3.0"
        self.assertFalse(libtesseract.is_available())
        libtess.TessVersion.assert_called_once_with()

    @patch("pyocr.libtesseract.get_available_languages")
    def test_can_detect_orientation(self, get_available_languages):
        get_available_languages.return_value = ['eng', 'fra', 'jpn', 'osd']
        self.assertTrue(libtesseract.can_detect_orientation())
        get_available_languages.return_value = ['eng', 'fra', 'jpn']
        self.assertFalse(libtesseract.can_detect_orientation())

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_version(self, libtess):
        libtess.TessVersion.return_value = b"3.05"
        self.assertEqual(libtesseract.get_version(), (3, 5, 0))
        libtess.TessVersion.return_value = b"3.2.1"
        self.assertEqual(libtesseract.get_version(), (3, 2, 1))
        libtess.TessVersion.return_value = b"4.0.0"
        self.assertEqual(libtesseract.get_version(), (4, 0, 0))
        libtess.TessVersion.return_value = b"4.0.0aplha"
        self.assertEqual(libtesseract.get_version(), (4, 0, 0))
        libtess.TessVersion.return_value = b"3.5.1dev1"
        self.assertEqual(libtesseract.get_version(), (3, 5, 1))
        libtess.TessVersion.assert_called_with()
        self.assertEqual(libtess.TessVersion.call_count, 5)

    def test_name(self):
        self.assertEqual(libtesseract.get_name(), "Tesseract (C-API)")

    def test_available_builders(self):
        self.assertEqual(
            libtesseract.get_available_builders(),
            [
                builders.TextBuilder,
                builders.WordBoxBuilder,
                builders.DigitBuilder,
                builders.LineBoxBuilder,
                builders.DigitLineBoxBuilder,
            ]
        )

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_langs(self, libtess):
        libtess.TessBaseAPICreate.return_value = self.handle
        libtess.TessBaseAPIGetAvailableLanguagesAsVector.return_value = [
            b"eng",
            b"fra",
            b"jpn",
            b"osd",
            b""
        ]
        self.assertListEqual(
            libtesseract.get_available_languages(),
            ["eng", "fra", "jpn", "osd"]
        )
        libtess.TessBaseAPICreate.assert_called_once_with()
        self.assertEqual(
            libtess.TessBaseAPIGetAvailableLanguagesAsVector.call_count,
            1
        )
        args = libtess.TessBaseAPIGetAvailableLanguagesAsVector.call_args[0]
        self.assertEqual(len(args), 1)
        self.assertEqual(args[0].value, self.handle)

    def test_tess_box_to_pyocr_box(self):
        box = (0, 1, 2, 3)
        self.assertSequenceEqual(
            libtesseract._tess_box_to_pyocr_box(box),
            ((0, 1), (2, 3))
        )

    @patch("pyocr.libtesseract.tesseract_raw")
    def test_detect_orientation(self, raw):
        raw.init.return_value = self.handle
        expected = {
            "orientation": raw.Orientation.PAGE_RIGHT,
            "confidence": 87,
        }
        raw.detect_os.return_value = expected
        self.assertEqual(
            libtesseract.detect_orientation(self.image),
            {
                "angle": 90,
                "confidence": 87,
            }
        )
        raw.init.assert_called_once_with(lang="osd")
        raw.set_page_seg_mode.assert_called_once_with(
            self.handle, raw.PageSegMode.OSD_ONLY
        )
        raw.set_image.assert_called_once_with(self.handle, self.image)
        raw.detect_os.assert_called_once_with(self.handle)

    @patch("pyocr.libtesseract.tesseract_raw")
    def test_detect_orientation_error(self, raw):
        raw.init.return_value = self.handle
        raw.detect_os.return_value = {"confidence": 0}
        with self.assertRaises(TesseractError) as te:
            libtesseract.detect_orientation(self.image)
        self.assertEqual(te.exception.status, "no script")
        self.assertEqual(te.exception.message, "no script detected")


class TestLibTesseractRaw(BaseTest):

    def setUp(self):
        self.handle = randint(0, 2**32-1)
        self.iterator = randint(0, 2**32-1)
        self.image = Image.new("RGB", size=(1, 1))

    @patch("locale.setlocale")
    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_init_tesseract4(self, libtess, setlocale):
        libtess.TessVersion.return_value = b"4.0.0"
        libtess.TessBaseAPICreate.return_value = self.handle
        for lang in (None, "eng", "fra", "jpn", "osd"):
            api = tesseract_raw.init(lang)
            self.assertEqual(api, self.handle)

            libtess.TessBaseAPICreate.assert_called_once_with()

            self.assertEqual(
                libtess.TessBaseAPIInit3.call_count,
                1
            )
            args = libtess.TessBaseAPIInit3.call_args[0]
            self.assertEqual(len(args), 3)
            self.assertEqual(args[0].value, self.handle)
            self.assertEqual(args[1].value, None)
            self.assertEqual(args[2].value, lang.encode() if lang else None)

            self.assertEqual(
                libtess.TessBaseAPISetVariable.call_count,
                1
            )
            args = libtess.TessBaseAPISetVariable.call_args[0]
            self.assertEqual(len(args), 3)
            self.assertEqual(args[0].value, self.handle)
            self.assertEqual(args[1], b"tessedit_zero_rejection")
            self.assertEqual(args[2], b"F")

            setlocale.assert_called_once_with(locale.LC_ALL, "C")

            libtess.reset_mock()
            setlocale.reset_mock()

    @patch("locale.setlocale")
    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_init_tesseract3(self, libtess, setlocale):
        libtess.TessVersion.return_value = b"3.5.0"
        libtess.TessBaseAPICreate.return_value = self.handle
        for lang in (None, "eng", "fra", "jpn", "osd"):
            api = tesseract_raw.init(lang)
            self.assertEqual(api, self.handle)

            libtess.TessBaseAPICreate.assert_called_once_with()

            self.assertEqual(
                libtess.TessBaseAPIInit3.call_count,
                1
            )
            args = libtess.TessBaseAPIInit3.call_args[0]
            self.assertEqual(len(args), 3)
            self.assertEqual(args[0].value, self.handle)
            self.assertEqual(args[1].value, None)
            self.assertEqual(args[2].value, lang.encode() if lang else None)

            self.assertEqual(
                libtess.TessBaseAPISetVariable.call_count,
                1
            )
            args = libtess.TessBaseAPISetVariable.call_args[0]
            self.assertEqual(len(args), 3)
            self.assertEqual(args[0].value, self.handle)
            self.assertEqual(args[1], b"tessedit_zero_rejection")
            self.assertEqual(args[2], b"F")
            self.assertFalse(setlocale.called)

            libtess.reset_mock()
            setlocale.reset_mock()

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_init_error(self, libtess):
        libtess.TessBaseAPICreate.return_value = self.handle
        libtess.TessBaseAPIInit3.side_effect = Exception(
            "Could not initialize"
        )
        with self.assertRaises(Exception):
            tesseract_raw.init()
        self.assertEqual(
            libtess.TessBaseAPICreate.call_count,
            1
        )
        self.assertEqual(
            libtess.TessBaseAPIDelete.call_count,
            1
        )
        args = libtess.TessBaseAPIDelete.call_args[0]
        self.assertEqual(len(args), 1)
        self.assertEqual(args[0].value, self.handle)

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_cleanup(self, libtess):
        tesseract_raw.cleanup(self.handle)
        self.assertEqual(
            libtess.TessBaseAPIDelete.call_count,
            1
        )
        args = libtess.TessBaseAPIDelete.call_args[0]
        self.assertEqual(len(args), 1)
        self.assertEqual(args[0].value, self.handle)

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_set_is_numeric(self, libtess):
        for mode in (True, False):
            wl = b"0123456789." if mode else b""
            tesseract_raw.set_is_numeric(self.handle, mode)
            self.assertEqual(
                libtess.TessBaseAPISetVariable.call_count,
                1
            )
            args = libtess.TessBaseAPISetVariable.call_args[0]
            self.assertEqual(len(args), 3)
            self.assertEqual(args[0].value, self.handle)
            self.assertEqual(args[1], b"tessedit_char_whitelist")
            self.assertEqual(args[2], wl)
            libtess.reset_mock()

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_set_debug_file(self, libtess):
        for filename in ("file", b"file"):
            tesseract_raw.set_debug_file(self.handle, filename)
            self.assertEqual(
                libtess.TessBaseAPISetVariable.call_count,
                1
            )
            args = libtess.TessBaseAPISetVariable.call_args[0]
            self.assertEqual(len(args), 3)
            self.assertEqual(args[0].value, self.handle)
            self.assertEqual(args[1], b"debug_file")
            self.assertEqual(args[2], b"file")
            libtess.reset_mock()

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_set_page_seg_mode(self, libtess):
        tesseract_raw.set_page_seg_mode(self.handle, 3)
        self.assertEqual(
            libtess.TessBaseAPISetPageSegMode.call_count,
            1
        )
        args = libtess.TessBaseAPISetPageSegMode.call_args[0]
        self.assertEqual(len(args), 2)
        self.assertEqual(args[0].value, self.handle)
        self.assertEqual(args[1].value, 3)

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_init_for_analyse_page(self, libtess):
        tesseract_raw.init_for_analyse_page(self.handle)
        self.assertEqual(
            libtess.TessBaseAPIInitForAnalysePage.call_count,
            1
        )
        args = libtess.TessBaseAPIInitForAnalysePage.call_args[0]
        self.assertEqual(len(args), 1)
        self.assertEqual(args[0].value, self.handle)

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_set_image(self, libtess):
        tesseract_raw.set_image(self.handle, self.image)
        self.assertEqual(libtess.TessBaseAPISetImage.call_count, 1)
        args = libtess.TessBaseAPISetImage.call_args[0]
        self.assertEqual(len(args), 6)
        self.assertEqual(args[0].value, self.handle)
        self.assertEqual(args[1], self.image.tobytes("raw", "RGB"))
        self.assertEqual(args[2].value, self.image.width)
        self.assertEqual(args[3].value, self.image.height)
        self.assertEqual(args[4].value, 3)
        self.assertEqual(args[5].value, self.image.width * 3)

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_recognize(self, libtess):
        libtess.TessBaseAPIRecognize.return_value = 0
        self.assertEqual(tesseract_raw.recognize(self.handle), 0)
        self.assertEqual(
            libtess.TessBaseAPIRecognize.call_count,
            1
        )
        args = libtess.TessBaseAPIRecognize.call_args[0]
        self.assertEqual(len(args), 2)
        self.assertEqual(args[0].value, self.handle)
        self.assertIsNone(args[1].value)

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_analyse_layout(self, libtess):
        layout = randint(0, 2**32-1)
        libtess.TessBaseAPIAnalyseLayout.return_value = layout
        self.assertEqual(tesseract_raw.analyse_layout(self.handle), layout)
        self.assertEqual(
            libtess.TessBaseAPIAnalyseLayout.call_count,
            1
        )
        args = libtess.TessBaseAPIAnalyseLayout.call_args[0]
        self.assertEqual(len(args), 1)
        self.assertEqual(args[0].value, self.handle)

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_get_utf8_text(self, libtess):
        text = "Test text for get utf8"
        ptr = c_char_p(text.encode())
        libtess.TessBaseAPIGetUTF8Text.return_value = ptr
        self.assertEqual(tesseract_raw.get_utf8_text(self.handle), text)
        self.assertEqual(
            libtess.TessBaseAPIGetUTF8Text.call_count,
            1
        )
        args = libtess.TessBaseAPIGetUTF8Text.call_args[0]
        self.assertEqual(len(args), 1)
        self.assertEqual(args[0].value, self.handle)

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_page_iterator_delete(self, libtess):
        tesseract_raw.page_iterator_delete(self.iterator)
        self.assertEqual(
            libtess.TessPageIteratorDelete.call_count,
            1
        )
        args = libtess.TessPageIteratorDelete.call_args[0]
        self.assertEqual(len(args), 1)
        self.assertEqual(args[0].value, self.iterator)

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_page_iterator_next(self, libtess):
        libtess.TessPageIteratorNext.return_value = self.iterator + 1
        self.assertEqual(tesseract_raw.page_iterator_next(
            self.iterator,
            tesseract_raw.PageIteratorLevel.WORD
        ), self.iterator + 1)
        self.assertEqual(
            libtess.TessPageIteratorNext.call_count,
            1
        )
        args = libtess.TessPageIteratorNext.call_args[0]
        self.assertEqual(len(args), 2)
        self.assertEqual(args[0].value, self.iterator)
        self.assertEqual(args[1], tesseract_raw.PageIteratorLevel.WORD)

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_page_iterator_beginning(self, libtess):
        libtess.TessPageIteratorIsAtBeginningOf.return_value = True
        self.assertTrue(tesseract_raw.page_iterator_is_at_beginning_of(
            self.iterator,
            tesseract_raw.PageIteratorLevel.WORD
        ))
        self.assertEqual(
            libtess.TessPageIteratorIsAtBeginningOf.call_count,
            1
        )
        args = libtess.TessPageIteratorIsAtBeginningOf.call_args[0]
        self.assertEqual(len(args), 2)
        self.assertEqual(args[0].value, self.iterator)
        self.assertEqual(args[1], tesseract_raw.PageIteratorLevel.WORD)

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_page_iterator_final(self, libtess):
        element = randint(0, 2**32-1)
        libtess.TessPageIteratorIsAtFinalElement.return_value = True
        self.assertTrue(tesseract_raw.page_iterator_is_at_final_element(
            self.iterator,
            tesseract_raw.PageIteratorLevel.WORD,
            element
        ))
        self.assertEqual(
            libtess.TessPageIteratorIsAtFinalElement.call_count,
            1
        )
        args = libtess.TessPageIteratorIsAtFinalElement.call_args[0]
        self.assertEqual(len(args), 3)
        self.assertEqual(args[0].value, self.iterator)
        self.assertEqual(args[1], tesseract_raw.PageIteratorLevel.WORD)
        self.assertEqual(args[2], element)

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_page_iterator_block_type(self, libtess):
        flowing = tesseract_raw.PolyBlockType.FLOWING_TEXT
        libtess.TessPageIteratorBlockType.return_value = flowing
        self.assertEqual(tesseract_raw.page_iterator_block_type(self.iterator),
                         tesseract_raw.PolyBlockType.FLOWING_TEXT)
        self.assertEqual(
            libtess.TessPageIteratorBlockType.call_count,
            1
        )
        args = libtess.TessPageIteratorBlockType.call_args[0]
        self.assertEqual(len(args), 1)
        self.assertEqual(args[0].value, self.iterator)

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_page_iterator_box(self, libtess):
        for res in (True, False):
            libtess.TessPageIteratorBoundingBox.return_value = res
            level = tesseract_raw.PageIteratorLevel.WORD
            result, box = tesseract_raw.page_iterator_bounding_box(
                self.iterator, level
            )
            self.assertEqual(result, res)
            self.assertSequenceEqual(box, (0, 0, 0, 0))
            self.assertEqual(
                libtess.TessPageIteratorBoundingBox.call_count,
                1
            )
            args = libtess.TessPageIteratorBoundingBox.call_args[0]
            self.assertEqual(len(args), 6)
            self.assertEqual(args[0].value, self.iterator)
            self.assertEqual(args[1], level)
            self.assertEqual(cast(args[2], POINTER(c_int)).contents.value, 0)
            self.assertEqual(cast(args[3], POINTER(c_int)).contents.value, 0)
            self.assertEqual(cast(args[4], POINTER(c_int)).contents.value, 0)
            self.assertEqual(cast(args[5], POINTER(c_int)).contents.value, 0)

            libtess.reset_mock()

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_page_iterator_orientation(self, libtess):
        expected = {
            "orientation": 0,
            "writing_direction": 0,
            "textline_order": 0,
            "deskew_angle": 0,
        }
        self.assertEqual(
            tesseract_raw.page_iterator_orientation(self.iterator),
            expected
        )
        self.assertEqual(
            libtess.TessPageIteratorOrientation.call_count,
            1
        )
        args = libtess.TessPageIteratorOrientation.call_args[0]
        self.assertEqual(len(args), 5)
        self.assertEqual(args[0].value, self.iterator)
        self.assertEqual(cast(args[1], POINTER(c_int)).contents.value, 0)
        self.assertEqual(cast(args[2], POINTER(c_int)).contents.value, 0)
        self.assertEqual(cast(args[3], POINTER(c_int)).contents.value, 0)
        self.assertEqual(cast(args[4], POINTER(c_int)).contents.value, 0)

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_get_iterator(self, libtess):
        libtess.TessBaseAPIGetIterator.return_value = self.iterator
        self.assertEqual(tesseract_raw.get_iterator(self.handle),
                         self.iterator)
        self.assertEqual(
            libtess.TessBaseAPIGetIterator.call_count,
            1
        )
        args = libtess.TessBaseAPIGetIterator.call_args[0]
        self.assertEqual(len(args), 1)
        self.assertEqual(args[0].value, self.handle)

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_result_iterator_page(self, libtess):
        libtess.TessResultIteratorGetPageIterator.return_value = self.iterator
        self.assertEqual(
            tesseract_raw.result_iterator_get_page_iterator(self.iterator),
            self.iterator
        )
        self.assertEqual(
            libtess.TessResultIteratorGetPageIterator.call_count,
            1
        )
        args = libtess.TessResultIteratorGetPageIterator.call_args[0]
        self.assertEqual(len(args), 1)
        self.assertEqual(args[0].value, self.iterator)

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_result_iterator_text(self, libtess):
        level = tesseract_raw.PageIteratorLevel.WORD
        text = "Test text for get utf8"
        ptr = c_char_p(text.encode())
        libtess.TessResultIteratorGetUTF8Text.return_value = ptr
        self.assertEqual(
            tesseract_raw.result_iterator_get_utf8_text(self.iterator, level),
            text
        )
        self.assertEqual(
            libtess.TessResultIteratorGetUTF8Text.call_count,
            1
        )
        args = libtess.TessResultIteratorGetUTF8Text.call_args[0]
        self.assertEqual(len(args), 2)
        self.assertEqual(args[0].value, self.iterator)
        self.assertEqual(args[1], level)
        libtess.TessDeleteText.assert_called_once_with(ptr)

        libtess.reset_mock()

        libtess.TessResultIteratorGetUTF8Text.return_value = None
        self.assertIsNone(
            tesseract_raw.result_iterator_get_utf8_text(self.iterator, level)
        )
        self.assertEqual(
            libtess.TessResultIteratorGetUTF8Text.call_count,
            1
        )
        args = libtess.TessResultIteratorGetUTF8Text.call_args[0]
        self.assertEqual(len(args), 2)
        self.assertEqual(args[0].value, self.iterator)
        self.assertEqual(args[1], level)
        self.assertFalse(libtess.TessDeleteText.called)

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_result_iterator_confidence(self, libtess):
        level = tesseract_raw.PageIteratorLevel.WORD
        libtess.TessResultIteratorConfidence.return_value = 95
        self.assertEqual(
            tesseract_raw.result_iterator_get_confidence(self.iterator, level),
            95
        )
        self.assertEqual(
            libtess.TessResultIteratorConfidence.call_count,
            1
        )
        args = libtess.TessResultIteratorConfidence.call_args[0]
        self.assertEqual(len(args), 2)
        self.assertEqual(args[0].value, self.iterator)
        self.assertEqual(args[1], level)

        libtess.reset_mock()

        libtess.TessResultIteratorConfidence.return_value = None
        self.assertIsNone(
            tesseract_raw.result_iterator_get_confidence(self.iterator, level)
        )
        self.assertEqual(
            libtess.TessResultIteratorConfidence.call_count,
            1
        )
        args = libtess.TessResultIteratorConfidence.call_args[0]
        self.assertEqual(len(args), 2)
        self.assertEqual(args[0].value, self.iterator)
        self.assertEqual(args[1], level)

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_detect_os(self, libtess):
        libtess.TessBaseAPIDetectOrientationScript.return_value = True
        self.assertEqual(
            tesseract_raw.detect_os(self.handle),
            {
                "orientation": 0,
                "confidence": 0,
            }
        )
        self.assertEqual(
            libtess.TessBaseAPIDetectOrientationScript.call_count,
            1
        )
        args = libtess.TessBaseAPIDetectOrientationScript.call_args[0]
        self.assertEqual(len(args), 5)
        self.assertEqual(args[0].value, self.handle)
        self.assertEqual(cast(args[1], POINTER(c_int)).contents.value, 0)
        self.assertEqual(cast(args[2], POINTER(c_int)).contents.value, 0)
        self.assertIsNone(args[3])
        self.assertIsNone(args[4])

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_detect_os_error(self, libtess):
        libtess.TessBaseAPIDetectOrientationScript.return_value = False
        with self.assertRaises(TesseractError) as te:
            tesseract_raw.detect_os(self.handle)
        self.assertEqual(te.exception.status, "detect_orientation failed")
        self.assertEqual(te.exception.message,
                         "TessBaseAPIDetectOrientationScript() failed")
        self.assertEqual(
            libtess.TessBaseAPIDetectOrientationScript.call_count,
            1
        )
        args = libtess.TessBaseAPIDetectOrientationScript.call_args[0]
        self.assertEqual(len(args), 5)
        self.assertEqual(args[0].value, self.handle)
        self.assertEqual(cast(args[1], POINTER(c_int)).contents.value, 0)
        self.assertEqual(cast(args[2], POINTER(c_int)).contents.value, 0)
        self.assertIsNone(args[3])
        self.assertIsNone(args[4])

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_detect_os_old(self, libtess):
        del libtess.TessBaseAPIDetectOrientationScript
        libtess.TessBaseAPIDetectOS.return_value = True
        self.assertEqual(
            tesseract_raw.detect_os(self.handle),
            {
                "orientation": 0,
                "confidence": 0,
            }
        )
        self.assertEqual(
            libtess.TessBaseAPIDetectOS.call_count,
            1
        )
        args = libtess.TessBaseAPIDetectOS.call_args[0]
        self.assertEqual(len(args), 2)
        self.assertEqual(args[0].value, self.handle)
        self.assertIsInstance(
            cast(args[1], POINTER(tesseract_raw.OSResults)).contents,
            tesseract_raw.OSResults
        )

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_detect_os_old_error(self, libtess):
        del libtess.TessBaseAPIDetectOrientationScript
        libtess.TessBaseAPIDetectOS.return_value = False
        with self.assertRaises(TesseractError) as te:
            tesseract_raw.detect_os(self.handle)
        self.assertEqual(te.exception.status, "detect_orientation failed")
        self.assertEqual(te.exception.message,
                         "TessBaseAPIDetectOS() failed")
        self.assertEqual(
            libtess.TessBaseAPIDetectOS.call_count,
            1
        )
        args = libtess.TessBaseAPIDetectOS.call_args[0]
        self.assertEqual(len(args), 2)
        self.assertEqual(args[0].value, self.handle)
        self.assertIsInstance(
            cast(args[1], POINTER(tesseract_raw.OSResults)).contents,
            tesseract_raw.OSResults
        )

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_set_input_name(self, libtess):
        input_file = "file"
        tesseract_raw.set_input_name(self.handle, input_file)
        self.assertEqual(
            libtess.TessBaseAPISetInputName.call_count,
            1
        )
        args = libtess.TessBaseAPISetInputName.call_args[0]
        self.assertEqual(len(args), 2)
        self.assertEqual(args[0].value, self.handle)
        self.assertEqual(args[1], input_file.encode())

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_init_pdf(self, libtess):
        output_file = "file"
        renderer = randint(0, 2**32-1)
        tessdata_dir = "/path/to/tess/data"
        libtess.TessBaseAPIGetDatapath.return_value = tessdata_dir
        libtess.TessPDFRendererCreate.return_value = renderer
        self.assertEqual(
            tesseract_raw.init_pdf_renderer(self.handle, output_file, True),
            renderer
        )
        libtess.TessBaseAPIGetDatapath.assert_called_once_with(self.handle)
        self.assertEqual(
            libtess.TessPDFRendererCreate.call_count,
            1
        )
        args = libtess.TessPDFRendererCreate.call_args[0]
        self.assertEqual(len(args), 3)
        self.assertEqual(args[0], output_file.encode())
        self.assertEqual(args[1], tessdata_dir)
        self.assertEqual(args[2].value, True)

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_begin_doc(self, libtess):
        renderer = randint(0, 2**32-1)
        doc_name = "doc"
        tesseract_raw.begin_document(renderer, doc_name)
        self.assertEqual(
            libtess.TessResultRendererBeginDocument.call_count,
            1
        )
        args = libtess.TessResultRendererBeginDocument.call_args[0]
        self.assertEqual(len(args), 2)
        self.assertEqual(args[0].value, renderer)
        self.assertEqual(args[1], doc_name.encode())

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_add_renderer_image(self, libtess):
        renderer = randint(0, 2**32-1)
        tesseract_raw.add_renderer_image(self.handle, renderer)
        self.assertEqual(
            libtess.TessResultRendererAddImage.call_count,
            1
        )
        args = libtess.TessResultRendererAddImage.call_args[0]
        self.assertEqual(len(args), 2)
        self.assertEqual(args[0].value, renderer)
        self.assertEqual(args[1].value, self.handle)

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    def test_end_doc(self, libtess):
        renderer = randint(0, 2**32-1)
        tesseract_raw.end_document(renderer)
        self.assertEqual(
            libtess.TessResultRendererEndDocument.call_count,
            1
        )
        args = libtess.TessResultRendererEndDocument.call_args[0]
        self.assertEqual(len(args), 1)
        self.assertEqual(args[0].value, renderer)


class TestLibTesseractText(BaseTest):

    @patch("pyocr.tesseract.get_version")
    def setUp(self, get_version):
        get_version.return_value = (4, 0, 0)
        self.image = Image.new(mode="RGB", size=(1, 1))
        self.builder = builders.TextBuilder()
        self.handle = randint(0, 2**32-1)
        self.iterator = randint(0, 2**32-1)

    @patch("pyocr.tesseract.get_version")
    @patch("pyocr.libtesseract.tesseract_raw")
    def test_image_to_string_defaults_to_text_buidler(self, raw, get_version):
        get_version.return_value = (4, 0, 0)
        raw.init.return_value = self.handle
        raw.get_iterator.return_value = self.iterator
        raw.result_iterator_get_page_iterator.return_value = self.iterator
        raw.get_available_languages.return_value = ["eng", "fra", "jpn", "osd"]
        raw.page_iterator_next.side_effect = (True, True, False)
        raw.page_iterator_bounding_box.return_value = (True, (0, 0, 0, 0))
        raw.result_iterator_get_utf8_text.side_effect = ("word1", "word2",
                                                         "word3")
        raw.page_iterator_is_at_beginning_of.side_effect = (True, False, False)
        raw.page_iterator_is_at_final_element.side_effect = (False, False,
                                                             True)

        self.assertEqual(
            libtesseract.image_to_string(self.image),
            "word1 word2 word3"
        )

        raw.init.assert_called_once_with(lang=None)
        raw.get_available_languages.assert_called_once_with(self.handle)
        raw.set_page_seg_mode.assert_called_once_with(
            self.handle, self.builder.tesseract_layout)
        raw.set_debug_file.assert_called_once_with(self.handle, os.devnull)
        raw.set_image.assert_called_once_with(self.handle, self.image)
        self.assertFalse(raw.set_is_numeric.called)
        raw.recognize.assert_called_once_with(self.handle)
        raw.get_iterator.assert_called_once_with(self.handle)
        raw.result_iterator_get_page_iterator.assert_called_once_with(
            self.iterator
        )
        self.assertEqual(raw.page_iterator_is_at_beginning_of.call_count, 3)
        raw.page_iterator_is_at_beginning_of.assert_called_with(
            self.iterator, raw.PageIteratorLevel.TEXTLINE)

        # called first at beginning and three times for each word
        self.assertEqual(raw.page_iterator_bounding_box.call_count, 4)
        self.assertListEqual(
            raw.page_iterator_bounding_box.call_args_list,
            [
                call(self.iterator, raw.PageIteratorLevel.TEXTLINE),
                call(self.iterator, raw.PageIteratorLevel.WORD),
                call(self.iterator, raw.PageIteratorLevel.WORD),
                call(self.iterator, raw.PageIteratorLevel.WORD),
            ]
        )
        self.assertEqual(raw.page_iterator_is_at_final_element.call_count, 3)
        raw.page_iterator_is_at_final_element.assert_called_with(
            self.iterator, raw.PageIteratorLevel.TEXTLINE,
            raw.PageIteratorLevel.WORD
        )
        self.assertEqual(raw.result_iterator_get_utf8_text.call_count, 3)
        raw.result_iterator_get_utf8_text.assert_called_with(
            self.iterator, raw.PageIteratorLevel.WORD)
        self.assertEqual(raw.result_iterator_get_confidence.call_count, 3)
        raw.result_iterator_get_confidence.assert_called_with(
            self.iterator, raw.PageIteratorLevel.WORD)
        self.assertEqual(raw.page_iterator_next.call_count, 3)
        raw.page_iterator_next.assert_called_with(
            self.iterator, raw.PageIteratorLevel.WORD)
        raw.cleanup.assert_called_once_with(self.handle)

    @patch("pyocr.libtesseract.tesseract_raw")
    def test_lang(self, raw):
        raw.init.return_value = self.handle
        raw.get_iterator.return_value = self.iterator
        raw.result_iterator_get_page_iterator.return_value = self.iterator
        raw.get_available_languages.return_value = ["eng", "fra", "jpn", "osd"]
        raw.page_iterator_next.side_effect = (True, True, False)
        raw.page_iterator_bounding_box.return_value = (True, (0, 0, 0, 0))
        raw.result_iterator_get_utf8_text.side_effect = ("word1", "word2",
                                                         "word3")
        raw.page_iterator_is_at_beginning_of.side_effect = (True, False, False)
        raw.page_iterator_is_at_final_element.side_effect = (False, False,
                                                             True)

        self.assertEqual(
            libtesseract.image_to_string(self.image, lang="eng",
                                         builder=self.builder),
            "word1 word2 word3"
        )

        raw.init.assert_called_once_with(lang="eng")
        raw.get_available_languages.assert_called_once_with(self.handle)
        raw.set_page_seg_mode.assert_called_once_with(
            self.handle, self.builder.tesseract_layout)
        raw.set_debug_file.assert_called_once_with(self.handle, os.devnull)
        raw.set_image.assert_called_once_with(self.handle, self.image)
        self.assertFalse(raw.set_is_numeric.called)
        raw.recognize.assert_called_once_with(self.handle)
        raw.get_iterator.assert_called_once_with(self.handle)
        raw.result_iterator_get_page_iterator.assert_called_once_with(
            self.iterator
        )
        self.assertEqual(raw.page_iterator_is_at_beginning_of.call_count, 3)
        raw.page_iterator_is_at_beginning_of.assert_called_with(
            self.iterator, raw.PageIteratorLevel.TEXTLINE)

        # called first at beginning and three times for each word
        self.assertEqual(raw.page_iterator_bounding_box.call_count, 4)
        self.assertListEqual(
            raw.page_iterator_bounding_box.call_args_list,
            [
                call(self.iterator, raw.PageIteratorLevel.TEXTLINE),
                call(self.iterator, raw.PageIteratorLevel.WORD),
                call(self.iterator, raw.PageIteratorLevel.WORD),
                call(self.iterator, raw.PageIteratorLevel.WORD),
            ]
        )
        self.assertEqual(raw.page_iterator_is_at_final_element.call_count, 3)
        raw.page_iterator_is_at_final_element.assert_called_with(
            self.iterator, raw.PageIteratorLevel.TEXTLINE,
            raw.PageIteratorLevel.WORD
        )
        self.assertEqual(raw.result_iterator_get_utf8_text.call_count, 3)
        raw.result_iterator_get_utf8_text.assert_called_with(
            self.iterator, raw.PageIteratorLevel.WORD)
        self.assertEqual(raw.result_iterator_get_confidence.call_count, 3)
        raw.result_iterator_get_confidence.assert_called_with(
            self.iterator, raw.PageIteratorLevel.WORD)
        self.assertEqual(raw.page_iterator_next.call_count, 3)
        raw.page_iterator_next.assert_called_with(
            self.iterator, raw.PageIteratorLevel.WORD)
        raw.cleanup.assert_called_once_with(self.handle)

    @patch("pyocr.libtesseract.tesseract_raw")
    def test_lang_error(self, raw):
        raw.init.return_value = self.handle
        raw.get_available_languages.return_value = ["eng", "jpn", "osd"]

        with self.assertRaises(TesseractError) as te:
            libtesseract.image_to_string(self.image, lang="fra",
                                         builder=self.builder)
        self.assertEqual(te.exception.status, "no lang")
        self.assertEqual(te.exception.message, "language fra is not available")

        raw.init.assert_called_once_with(lang="fra")
        raw.get_available_languages.assert_called_once_with(self.handle)
        raw.cleanup.assert_called_once_with(self.handle)

    @patch("pyocr.libtesseract.tesseract_raw")
    def test_text(self, raw):
        raw.init.return_value = self.handle
        raw.get_iterator.return_value = self.iterator
        raw.result_iterator_get_page_iterator.return_value = self.iterator
        raw.get_available_languages.return_value = ["eng", "fra", "jpn", "osd"]
        raw.page_iterator_next.side_effect = (True, True, True, False)
        raw.page_iterator_bounding_box.return_value = (True, (0, 0, 0, 0))
        raw.result_iterator_get_utf8_text.side_effect = ("word1", "word2",
                                                         None, "word3")
        raw.page_iterator_is_at_beginning_of.side_effect = (True, False,
                                                            False, False)
        raw.page_iterator_is_at_final_element.side_effect = (False, False,
                                                             False, True)

        self.assertEqual(
            libtesseract.image_to_string(self.image, builder=self.builder),
            "word1 word2 word3"
        )

        raw.init.assert_called_once_with(lang=None)
        raw.get_available_languages.assert_called_once_with(self.handle)
        raw.set_page_seg_mode.assert_called_once_with(
            self.handle, self.builder.tesseract_layout)
        raw.set_debug_file.assert_called_once_with(self.handle, os.devnull)
        raw.set_image.assert_called_once_with(self.handle, self.image)
        self.assertFalse(raw.set_is_numeric.called)
        raw.recognize.assert_called_once_with(self.handle)
        raw.get_iterator.assert_called_once_with(self.handle)
        raw.result_iterator_get_page_iterator.assert_called_once_with(
            self.iterator
        )
        self.assertEqual(raw.page_iterator_is_at_beginning_of.call_count, 4)
        raw.page_iterator_is_at_beginning_of.assert_called_with(
            self.iterator, raw.PageIteratorLevel.TEXTLINE)

        # called first at beginning and three times for each word
        self.assertEqual(raw.page_iterator_bounding_box.call_count, 4)
        self.assertListEqual(
            raw.page_iterator_bounding_box.call_args_list,
            [
                call(self.iterator, raw.PageIteratorLevel.TEXTLINE),
                call(self.iterator, raw.PageIteratorLevel.WORD),
                call(self.iterator, raw.PageIteratorLevel.WORD),
                call(self.iterator, raw.PageIteratorLevel.WORD),
            ]
        )
        self.assertEqual(raw.page_iterator_is_at_final_element.call_count, 4)
        raw.page_iterator_is_at_final_element.assert_called_with(
            self.iterator, raw.PageIteratorLevel.TEXTLINE,
            raw.PageIteratorLevel.WORD
        )
        self.assertEqual(raw.result_iterator_get_utf8_text.call_count, 4)
        raw.result_iterator_get_utf8_text.assert_called_with(
            self.iterator, raw.PageIteratorLevel.WORD)
        self.assertEqual(raw.result_iterator_get_confidence.call_count, 4)
        raw.result_iterator_get_confidence.assert_called_with(
            self.iterator, raw.PageIteratorLevel.WORD)
        self.assertEqual(raw.page_iterator_next.call_count, 4)
        raw.page_iterator_next.assert_called_with(
            self.iterator, raw.PageIteratorLevel.WORD)
        raw.cleanup.assert_called_once_with(self.handle)

    @patch("pyocr.libtesseract.tesseract_raw")
    def test_text_error(self, raw):
        raw.init.return_value = self.handle
        raw.get_iterator.return_value = None
        raw.result_iterator_get_page_iterator.return_value = self.iterator
        raw.get_available_languages.return_value = ["eng", "fra", "jpn", "osd"]
        raw.page_iterator_next.side_effect = (True, True, False)
        raw.page_iterator_bounding_box.return_value = (True, (0, 0, 0, 0))
        raw.result_iterator_get_utf8_text.side_effect = ("word1", "word2",
                                                         "word3")
        raw.page_iterator_is_at_beginning_of.side_effect = (True, False, False)
        raw.page_iterator_is_at_final_element.side_effect = (False, False,
                                                             True)

        with self.assertRaises(TesseractError) as te:
            libtesseract.image_to_string(self.image, builder=self.builder)
        self.assertEqual(te.exception.status, "no script")
        self.assertEqual(te.exception.message, "no script detected")

        raw.init.assert_called_once_with(lang=None)
        raw.get_available_languages.assert_called_once_with(self.handle)
        raw.set_page_seg_mode.assert_called_once_with(
            self.handle, self.builder.tesseract_layout)
        raw.set_debug_file.assert_called_once_with(self.handle, os.devnull)
        raw.set_image.assert_called_once_with(self.handle, self.image)
        self.assertFalse(raw.set_is_numeric.called)
        raw.recognize.assert_called_once_with(self.handle)
        raw.get_iterator.assert_called_once_with(self.handle)


class TestLibTesseractDigits(BaseTest):

    @patch("pyocr.tesseract.get_version")
    def setUp(self, get_version):
        get_version.return_value = (4, 0, 0)
        self.builder = builders.DigitBuilder()
        self.image = Image.new(mode="RGB", size=(1, 1))
        self.handle = randint(0, 2**32-1)
        self.iterator = randint(0, 2**32-1)

    @patch("pyocr.libtesseract.tesseract_raw")
    def test_digits(self, raw):
        raw.init.return_value = self.handle
        raw.get_iterator.return_value = self.iterator
        raw.result_iterator_get_page_iterator.return_value = self.iterator
        raw.get_available_languages.return_value = ["eng", "fra", "jpn", "osd"]
        raw.page_iterator_next.side_effect = (True, True, False)
        raw.page_iterator_bounding_box.return_value = (True, (0, 0, 0, 0))
        raw.result_iterator_get_utf8_text.side_effect = ("1", "2", "42")
        raw.page_iterator_is_at_beginning_of.side_effect = (True, False, False)
        raw.page_iterator_is_at_final_element.side_effect = (False, False,
                                                             True)

        self.assertEqual(
            libtesseract.image_to_string(self.image, builder=self.builder),
            "1 2 42"
        )

        raw.init.assert_called_once_with(lang=None)
        raw.get_available_languages.assert_called_once_with(self.handle)
        raw.set_page_seg_mode.assert_called_once_with(
            self.handle, self.builder.tesseract_layout)
        raw.set_debug_file.assert_called_once_with(self.handle, os.devnull)
        raw.set_image.assert_called_once_with(self.handle, self.image)
        raw.set_is_numeric.assert_called_once_with(self.handle, True)
        raw.recognize.assert_called_once_with(self.handle)
        raw.get_iterator.assert_called_once_with(self.handle)
        raw.result_iterator_get_page_iterator.assert_called_once_with(
            self.iterator
        )
        self.assertEqual(raw.page_iterator_is_at_beginning_of.call_count, 3)
        raw.page_iterator_is_at_beginning_of.assert_called_with(
            self.iterator, raw.PageIteratorLevel.TEXTLINE)

        # called first at beginning and three times for each word
        self.assertEqual(raw.page_iterator_bounding_box.call_count, 4)
        self.assertListEqual(
            raw.page_iterator_bounding_box.call_args_list,
            [
                call(self.iterator, raw.PageIteratorLevel.TEXTLINE),
                call(self.iterator, raw.PageIteratorLevel.WORD),
                call(self.iterator, raw.PageIteratorLevel.WORD),
                call(self.iterator, raw.PageIteratorLevel.WORD),
            ]
        )
        self.assertEqual(raw.page_iterator_is_at_final_element.call_count, 3)
        raw.page_iterator_is_at_final_element.assert_called_with(
            self.iterator, raw.PageIteratorLevel.TEXTLINE,
            raw.PageIteratorLevel.WORD
        )
        self.assertEqual(raw.result_iterator_get_utf8_text.call_count, 3)
        raw.result_iterator_get_utf8_text.assert_called_with(
            self.iterator, raw.PageIteratorLevel.WORD)
        self.assertEqual(raw.result_iterator_get_confidence.call_count, 3)
        raw.result_iterator_get_confidence.assert_called_with(
            self.iterator, raw.PageIteratorLevel.WORD)
        self.assertEqual(raw.page_iterator_next.call_count, 3)
        raw.page_iterator_next.assert_called_with(
            self.iterator, raw.PageIteratorLevel.WORD)
        raw.cleanup.assert_called_once_with(self.handle)


class TestLibTesseractWordBox(BaseTest):

    @patch("pyocr.tesseract.get_version")
    def setUp(self, get_version):
        get_version.return_value = (4, 0, 0)
        self.builder = builders.WordBoxBuilder()
        self.image = Image.new("RGB", size=(1, 1))
        self.handle = randint(0, 2**32-1)
        self.iterator = randint(0, 2**32-1)

    @patch("pyocr.libtesseract.tesseract_raw")
    def test_word(self, raw):
        raw.init.return_value = self.handle
        raw.get_iterator.return_value = self.iterator
        raw.result_iterator_get_page_iterator.return_value = self.iterator
        raw.get_available_languages.return_value = ["eng", "fra", "jpn", "osd"]
        raw.page_iterator_next.side_effect = (True, True, False)
        raw.page_iterator_bounding_box.return_value = (True, (0, 0, 0, 0))
        raw.result_iterator_get_utf8_text.side_effect = ("word1", "word2",
                                                         "word3")
        raw.page_iterator_is_at_beginning_of.side_effect = (True, False, False)
        raw.page_iterator_is_at_final_element.side_effect = (False, False,
                                                             True)

        self.assertListEqual(
            libtesseract.image_to_string(self.image, builder=self.builder),
            [
                builders.Box("word1", ((0, 0), (0, 0))),
                builders.Box("word2", ((0, 0), (0, 0))),
                builders.Box("word3", ((0, 0), (0, 0))),
            ]
        )

        raw.init.assert_called_once_with(lang=None)
        raw.get_available_languages.assert_called_once_with(self.handle)
        raw.set_page_seg_mode.assert_called_once_with(
            self.handle, self.builder.tesseract_layout)
        raw.set_debug_file.assert_called_once_with(self.handle, os.devnull)
        raw.set_image.assert_called_once_with(self.handle, self.image)
        self.assertFalse(raw.set_is_numeric.called)
        raw.recognize.assert_called_once_with(self.handle)
        raw.get_iterator.assert_called_once_with(self.handle)
        raw.result_iterator_get_page_iterator.assert_called_once_with(
            self.iterator
        )
        self.assertEqual(raw.page_iterator_is_at_beginning_of.call_count, 3)
        raw.page_iterator_is_at_beginning_of.assert_called_with(
            self.iterator, raw.PageIteratorLevel.TEXTLINE)

        # called first at beginning and three times for each word
        self.assertEqual(raw.page_iterator_bounding_box.call_count, 4)
        self.assertListEqual(
            raw.page_iterator_bounding_box.call_args_list,
            [
                call(self.iterator, raw.PageIteratorLevel.TEXTLINE),
                call(self.iterator, raw.PageIteratorLevel.WORD),
                call(self.iterator, raw.PageIteratorLevel.WORD),
                call(self.iterator, raw.PageIteratorLevel.WORD),
            ]
        )
        self.assertEqual(raw.page_iterator_is_at_final_element.call_count, 3)
        raw.page_iterator_is_at_final_element.assert_called_with(
            self.iterator, raw.PageIteratorLevel.TEXTLINE,
            raw.PageIteratorLevel.WORD
        )
        self.assertEqual(raw.result_iterator_get_utf8_text.call_count, 3)
        raw.result_iterator_get_utf8_text.assert_called_with(
            self.iterator, raw.PageIteratorLevel.WORD)
        self.assertEqual(raw.result_iterator_get_confidence.call_count, 3)
        raw.result_iterator_get_confidence.assert_called_with(
            self.iterator, raw.PageIteratorLevel.WORD)
        self.assertEqual(raw.page_iterator_next.call_count, 3)
        raw.page_iterator_next.assert_called_with(
            self.iterator, raw.PageIteratorLevel.WORD)
        raw.cleanup.assert_called_once_with(self.handle)

    @patch("pyocr.libtesseract.tesseract_raw")
    def test_word_error(self, raw):
        raw.init.return_value = self.handle
        raw.get_iterator.return_value = None
        raw.result_iterator_get_page_iterator.return_value = self.iterator
        raw.get_available_languages.return_value = ["eng", "fra", "jpn", "osd"]
        raw.page_iterator_next.side_effect = (True, True, False)
        raw.page_iterator_bounding_box.return_value = (True, (0, 0, 0, 0))
        raw.result_iterator_get_utf8_text.side_effect = ("word1", "word2",
                                                         "word3")
        raw.page_iterator_is_at_beginning_of.side_effect = (True, False, False)
        raw.page_iterator_is_at_final_element.side_effect = (False, False,
                                                             True)

        with self.assertRaises(TesseractError) as te:
            libtesseract.image_to_string(self.image, builder=self.builder)
        self.assertEqual(te.exception.status, "no script")
        self.assertEqual(te.exception.message, "no script detected")

        raw.init.assert_called_once_with(lang=None)
        raw.get_available_languages.assert_called_once_with(self.handle)
        raw.set_page_seg_mode.assert_called_once_with(
            self.handle, self.builder.tesseract_layout)
        raw.set_debug_file.assert_called_once_with(self.handle, os.devnull)
        raw.set_image.assert_called_once_with(self.handle, self.image)
        self.assertFalse(raw.set_is_numeric.called)
        raw.recognize.assert_called_once_with(self.handle)
        raw.get_iterator.assert_called_once_with(self.handle)


class TestLibTesseractLineBox(BaseTest):

    @patch("pyocr.tesseract.get_version")
    def setUp(self, get_version):
        get_version.return_value = (4, 0, 0)
        self.image = Image.new(mode="RGB", size=(1, 1))
        self.builder = builders.LineBoxBuilder()
        self.handle = randint(0, 2**32-1)
        self.iterator = randint(0, 2**32-1)

    @patch("pyocr.libtesseract.tesseract_raw")
    def test_line(self, raw):
        raw.init.return_value = self.handle
        raw.get_iterator.return_value = self.iterator
        raw.result_iterator_get_page_iterator.return_value = self.iterator
        raw.get_available_languages.return_value = ["eng", "fra", "jpn", "osd"]
        raw.page_iterator_next.side_effect = (True, True, False)
        raw.page_iterator_bounding_box.return_value = (True, (0, 0, 0, 0))
        raw.result_iterator_get_utf8_text.side_effect = ("word1", "word2",
                                                         "word3")
        raw.page_iterator_is_at_beginning_of.side_effect = (True, False, False)
        raw.page_iterator_is_at_final_element.side_effect = (False, False,
                                                             True)

        self.assertListEqual(
            libtesseract.image_to_string(self.image, builder=self.builder),
            [
                builders.LineBox([
                    builders.Box("word1", ((0, 0), (0, 0))),
                    builders.Box("word2", ((0, 0), (0, 0))),
                    builders.Box("word3", ((0, 0), (0, 0))),
                ], ((0, 0), (0, 0)))
            ]
        )

        raw.init.assert_called_once_with(lang=None)
        raw.get_available_languages.assert_called_once_with(self.handle)
        raw.set_page_seg_mode.assert_called_once_with(
            self.handle, self.builder.tesseract_layout)
        raw.set_debug_file.assert_called_once_with(self.handle, os.devnull)
        raw.set_image.assert_called_once_with(self.handle, self.image)
        self.assertFalse(raw.set_is_numeric.called)
        raw.recognize.assert_called_once_with(self.handle)
        raw.get_iterator.assert_called_once_with(self.handle)
        raw.result_iterator_get_page_iterator.assert_called_once_with(
            self.iterator
        )
        self.assertEqual(raw.page_iterator_is_at_beginning_of.call_count, 3)
        raw.page_iterator_is_at_beginning_of.assert_called_with(
            self.iterator, raw.PageIteratorLevel.TEXTLINE)

        # called first at beginning and three times for each word
        self.assertEqual(raw.page_iterator_bounding_box.call_count, 4)
        self.assertListEqual(
            raw.page_iterator_bounding_box.call_args_list,
            [
                call(self.iterator, raw.PageIteratorLevel.TEXTLINE),
                call(self.iterator, raw.PageIteratorLevel.WORD),
                call(self.iterator, raw.PageIteratorLevel.WORD),
                call(self.iterator, raw.PageIteratorLevel.WORD),
            ]
        )
        self.assertEqual(raw.page_iterator_is_at_final_element.call_count, 3)
        raw.page_iterator_is_at_final_element.assert_called_with(
            self.iterator, raw.PageIteratorLevel.TEXTLINE,
            raw.PageIteratorLevel.WORD
        )
        self.assertEqual(raw.result_iterator_get_utf8_text.call_count, 3)
        raw.result_iterator_get_utf8_text.assert_called_with(
            self.iterator, raw.PageIteratorLevel.WORD)
        self.assertEqual(raw.result_iterator_get_confidence.call_count, 3)
        raw.result_iterator_get_confidence.assert_called_with(
            self.iterator, raw.PageIteratorLevel.WORD)
        self.assertEqual(raw.page_iterator_next.call_count, 3)
        raw.page_iterator_next.assert_called_with(
            self.iterator, raw.PageIteratorLevel.WORD)
        raw.cleanup.assert_called_once_with(self.handle)

    @patch("pyocr.libtesseract.tesseract_raw")
    def test_line_error(self, raw):
        raw.init.return_value = self.handle
        raw.get_iterator.return_value = None
        raw.result_iterator_get_page_iterator.return_value = self.iterator
        raw.get_available_languages.return_value = ["eng", "fra", "jpn", "osd"]
        raw.page_iterator_next.side_effect = (True, True, False)
        raw.page_iterator_bounding_box.return_value = (True, (0, 0, 0, 0))
        raw.result_iterator_get_utf8_text.side_effect = ("word1", "word2",
                                                         "word3")
        raw.page_iterator_is_at_beginning_of.side_effect = (True, False, False)
        raw.page_iterator_is_at_final_element.side_effect = (False, False,
                                                             True)

        with self.assertRaises(TesseractError) as te:
            libtesseract.image_to_string(self.image, builder=self.builder)
        self.assertEqual(te.exception.status, "no script")
        self.assertEqual(te.exception.message, "no script detected")

        raw.init.assert_called_once_with(lang=None)
        raw.get_available_languages.assert_called_once_with(self.handle)
        raw.set_page_seg_mode.assert_called_once_with(
            self.handle, self.builder.tesseract_layout)
        raw.set_debug_file.assert_called_once_with(self.handle, os.devnull)
        raw.set_image.assert_called_once_with(self.handle, self.image)
        self.assertFalse(raw.set_is_numeric.called)
        raw.recognize.assert_called_once_with(self.handle)
        raw.get_iterator.assert_called_once_with(self.handle)


class TestLibTesseractDigitsLineBox(BaseTest):

    @patch("pyocr.tesseract.get_version")
    def setUp(self, get_version):
        get_version.return_value = (4, 0, 0)
        self.image = Image.new(mode="RGB", size=(1, 1))
        self.builder = builders.DigitLineBoxBuilder()
        self.handle = randint(0, 2**32-1)
        self.iterator = randint(0, 2**32-1)

    @patch("pyocr.libtesseract.tesseract_raw")
    def test_line(self, raw):
        raw.init.return_value = self.handle
        raw.get_iterator.return_value = self.iterator
        raw.result_iterator_get_page_iterator.return_value = self.iterator
        raw.get_available_languages.return_value = ["eng", "fra", "jpn", "osd"]
        raw.page_iterator_next.side_effect = (True, True, False)
        raw.page_iterator_bounding_box.return_value = (True, (0, 0, 0, 0))
        raw.result_iterator_get_utf8_text.side_effect = ("1", "2", "42")
        raw.page_iterator_is_at_beginning_of.side_effect = (True, False, False)
        raw.page_iterator_is_at_final_element.side_effect = (False, False,
                                                             True)

        self.assertListEqual(
            libtesseract.image_to_string(self.image, builder=self.builder),
            [
                builders.LineBox([
                    builders.Box("1", ((0, 0), (0, 0))),
                    builders.Box("2", ((0, 0), (0, 0))),
                    builders.Box("42", ((0, 0), (0, 0))),
                ], ((0, 0), (0, 0)))
            ]
        )

        raw.init.assert_called_once_with(lang=None)
        raw.get_available_languages.assert_called_once_with(self.handle)
        raw.set_page_seg_mode.assert_called_once_with(
            self.handle, self.builder.tesseract_layout)
        raw.set_debug_file.assert_called_once_with(self.handle, os.devnull)
        raw.set_image.assert_called_once_with(self.handle, self.image)
        raw.set_is_numeric.assert_called_once_with(self.handle, True)
        raw.recognize.assert_called_once_with(self.handle)
        raw.get_iterator.assert_called_once_with(self.handle)
        raw.result_iterator_get_page_iterator.assert_called_once_with(
            self.iterator
        )
        self.assertEqual(raw.page_iterator_is_at_beginning_of.call_count, 3)
        raw.page_iterator_is_at_beginning_of.assert_called_with(
            self.iterator, raw.PageIteratorLevel.TEXTLINE)

        # called first at beginning and three times for each word
        self.assertEqual(raw.page_iterator_bounding_box.call_count, 4)
        self.assertListEqual(
            raw.page_iterator_bounding_box.call_args_list,
            [
                call(self.iterator, raw.PageIteratorLevel.TEXTLINE),
                call(self.iterator, raw.PageIteratorLevel.WORD),
                call(self.iterator, raw.PageIteratorLevel.WORD),
                call(self.iterator, raw.PageIteratorLevel.WORD),
            ]
        )
        self.assertEqual(raw.page_iterator_is_at_final_element.call_count, 3)
        raw.page_iterator_is_at_final_element.assert_called_with(
            self.iterator, raw.PageIteratorLevel.TEXTLINE,
            raw.PageIteratorLevel.WORD
        )
        self.assertEqual(raw.result_iterator_get_utf8_text.call_count, 3)
        raw.result_iterator_get_utf8_text.assert_called_with(
            self.iterator, raw.PageIteratorLevel.WORD)
        self.assertEqual(raw.result_iterator_get_confidence.call_count, 3)
        raw.result_iterator_get_confidence.assert_called_with(
            self.iterator, raw.PageIteratorLevel.WORD)
        self.assertEqual(raw.page_iterator_next.call_count, 3)
        raw.page_iterator_next.assert_called_with(
            self.iterator, raw.PageIteratorLevel.WORD)
        raw.cleanup.assert_called_once_with(self.handle)

    @patch("pyocr.libtesseract.tesseract_raw")
    def test_line_error(self, raw):
        raw.init.return_value = self.handle
        raw.get_iterator.return_value = None
        raw.result_iterator_get_page_iterator.return_value = self.iterator
        raw.get_available_languages.return_value = ["eng", "fra", "jpn", "osd"]
        raw.page_iterator_next.side_effect = (True, True, False)
        raw.page_iterator_bounding_box.return_value = (True, (0, 0, 0, 0))
        raw.result_iterator_get_utf8_text.side_effect = ("1", "2", "42")
        raw.page_iterator_is_at_beginning_of.side_effect = (True, False, False)
        raw.page_iterator_is_at_final_element.side_effect = (False, False,
                                                             True)

        with self.assertRaises(TesseractError) as te:
            libtesseract.image_to_string(self.image, builder=self.builder)
        self.assertEqual(te.exception.status, "no script")
        self.assertEqual(te.exception.message, "no script detected")

        raw.init.assert_called_once_with(lang=None)
        raw.get_available_languages.assert_called_once_with(self.handle)
        raw.set_page_seg_mode.assert_called_once_with(
            self.handle, self.builder.tesseract_layout)
        raw.set_debug_file.assert_called_once_with(self.handle, os.devnull)
        raw.set_image.assert_called_once_with(self.handle, self.image)
        raw.set_is_numeric.assert_called_once_with(self.handle, True)
        raw.recognize.assert_called_once_with(self.handle)
        raw.get_iterator.assert_called_once_with(self.handle)


class TestLibTesseractPDF(BaseTest):

    def setUp(self):
        self.image = Image.new(mode="RGB", size=(1, 1))
        self.handle = randint(0, 2**32-1)

    @patch("pyocr.libtesseract.tesseract_raw")
    def test_pdf(self, raw):
        renderer = randint(0, 2**32-1)
        raw.init.return_value = self.handle
        raw.init_pdf_renderer.return_value = renderer
        libtesseract.image_to_pdf(self.image, "output")

        raw.init.assert_called_once_with(lang=None)
        raw.set_image.assert_called_once_with(self.handle, self.image)
        raw.set_page_seg_mode.assert_called_once_with(
            self.handle, raw.PageSegMode.AUTO_OSD
        )
        raw.set_input_name.assert_called_once_with(self.handle, "stdin")
        raw.recognize.assert_called_once_with(self.handle)
        raw.init_pdf_renderer.assert_called_once_with(
            self.handle, "output", False
        )
        raw.begin_document.assert_called_once_with(renderer, "")
        raw.add_renderer_image.assert_called_once_with(self.handle,
                                                       renderer)
        raw.end_document.assert_called_once_with(renderer)
        self.assertListEqual(
            raw.cleanup.call_args_list,
            [call(self.handle), call(renderer)]
        )

    @patch("pyocr.libtesseract.tesseract_raw")
    def test_pdf_renderer_error(self, raw):
        renderer = None
        raw.init.return_value = self.handle
        raw.init_pdf_renderer.return_value = renderer

        with self.assertRaises(AssertionError):
            libtesseract.image_to_pdf(self.image, "output")

        raw.init.assert_called_once_with(lang=None)
        raw.set_image.assert_called_once_with(self.handle, self.image)
        raw.set_page_seg_mode.assert_called_once_with(
            self.handle, raw.PageSegMode.AUTO_OSD
        )
        raw.set_input_name.assert_called_once_with(self.handle, "stdin")
        raw.recognize.assert_called_once_with(self.handle)
        raw.init_pdf_renderer.assert_called_once_with(
            self.handle, "output", False
        )
        self.assertFalse(raw.begin_document.called)
        self.assertFalse(raw.add_renderer_image.called)
        self.assertFalse(raw.end_document.called)
        raw.cleanup.assert_called_once_with(self.handle)
