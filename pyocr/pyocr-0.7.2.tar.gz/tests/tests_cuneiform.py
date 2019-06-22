import subprocess

from io import StringIO
from unittest.mock import patch, MagicMock

from PIL import Image

from pyocr import builders
from pyocr import cuneiform

from .tests_base import BaseTest


class TestCuneiform(BaseTest):
    """
    These tests make sure the requirements for the tests are met.
    """

    @patch("shutil.which")
    def test_available(self, which):
        # XXX is it useful?
        which.return_value = True
        self.assertTrue(cuneiform.is_available())
        which.assert_called_once_with("cuneiform")

    @patch("subprocess.Popen")
    def test_version(self, popen):
        stdout = MagicMock()
        stdout.stdout.read.return_value = (
            b"Cuneiform for Linux 1.1.0\n"
            b"Usage: cuneiform [-l languagename -f format --dotmatrix --fax"
            b" --singlecolumn -o result_file] imagefile"
        )
        popen.return_value = stdout
        self.assertSequenceEqual(cuneiform.get_version(), (1, 1, 0))

    @patch("subprocess.Popen")
    def test_version_error(self, popen):
        stdout = MagicMock()
        stdout.stdout.read.return_value = b"\n"
        popen.return_value = stdout
        self.assertIsNone(cuneiform.get_version())

    @patch("subprocess.Popen")
    def test_langs(self, popen):
        stdout = MagicMock()
        stdout.stdout.read.return_value = (
            b"Cuneiform for Linux 1.1.0\n"
            b"Supported languages: eng ger fra rus swe spa ita ruseng ukr srp "
            b"hrv pol dan por dut cze rum hun bul slv lav lit est tur."
        )
        popen.return_value = stdout
        langs = cuneiform.get_available_languages()
        self.assertIn("eng", langs)
        self.assertIn("fra", langs)
        popen.assert_called_once_with(
            ["cuneiform", "-l"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )

    def test_name(self):
        self.assertEqual(cuneiform.get_name(), "Cuneiform (sh)")

    def test_can_detect_orientation(self):
        self.assertFalse(cuneiform.can_detect_orientation())

    def test_available_builders(self):
        self.assertListEqual(
            cuneiform.get_available_builders(),
            [
                builders.TextBuilder,
                builders.WordBoxBuilder,
                builders.LineBoxBuilder,
            ]
        )


class TestCuneiformTxt(BaseTest):
    """
    These tests make sure the "usual" OCR works fine. (the one generating
    a .txt file)
    """
    @patch("pyocr.tesseract.get_version")
    def setUp(self, get_version):
        get_version.return_value = (4, 0, 0)
        self.builder = builders.TextBuilder()
        self.image = Image.new(mode="RGB", size=(1, 1))
        self.text_file = StringIO(self._get_file_content("text"))
        self.stdout = MagicMock()
        self.stdout.stdout.read.return_value = b"Cuneiform for Linux 1.1.0\n"
        self.stdout.wait.return_value = 0
        self.tmp_filename = "/tmp/cuneiform_n0qfk87otxt"
        self.enter = MagicMock()
        self.enter.__enter__.return_value = MagicMock()
        self.enter.__enter__.return_value.configure_mock(
            name=self.tmp_filename
        )

    @patch("pyocr.tesseract.get_version")
    @patch("pyocr.cuneiform.temp_file")
    @patch("codecs.open")
    @patch("subprocess.Popen")
    def test_image_to_string_defaults_to_text_buidler(self, popen, copen,
                                                      temp_file, get_version):
        get_version.return_value = (4, 0, 0)
        popen.return_value = self.stdout
        copen.return_value = self.text_file
        temp_file.return_value = self.enter
        output = cuneiform.image_to_string(self.image)
        self.assertEqual(output, self._get_file_content("text").strip())
        popen.assert_called_once_with(
            ["cuneiform", "-f", "text", "-o", self.tmp_filename, "-"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

    @patch("pyocr.cuneiform.temp_file")
    @patch("codecs.open")
    @patch("subprocess.Popen")
    def test_lang(self, popen, copen, temp_file):
        popen.return_value = self.stdout
        copen.return_value = self.text_file
        temp_file.return_value = self.enter
        output = cuneiform.image_to_string(self.image, lang="fra",
                                           builder=self.builder)
        self.assertEqual(output, self._get_file_content("text").strip())
        popen.assert_called_once_with(
            ["cuneiform", "-l", "fra", "-f", "text", "-o", self.tmp_filename,
             "-"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

    @patch("pyocr.cuneiform.temp_file")
    @patch("codecs.open")
    @patch("subprocess.Popen")
    def test_text(self, popen, copen, temp_file):
        popen.return_value = self.stdout
        copen.return_value = self.text_file
        temp_file.return_value = self.enter
        output = cuneiform.image_to_string(self.image,
                                           builder=self.builder)
        self.assertEqual(output, self._get_file_content("text").strip())
        popen.assert_called_once_with(
            ["cuneiform", "-f", "text", "-o", self.tmp_filename, "-"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

    @patch("subprocess.Popen")
    def test_text_error(self, popen):
        message = ("Cuneiform for Linux 1.1.0\n"
                   "Magick: Improper image header (example.png) reported by "
                   "coders/png.c:2932 (ReadPNGImage)\n")
        self.stdout.stdout.read.return_value = message.encode()
        self.stdout.wait.return_value = 1
        popen.return_value = self.stdout
        with self.assertRaises(cuneiform.CuneiformError) as ce:
            cuneiform.image_to_string(self.image, builder=self.builder)
        self.assertEqual(ce.exception.status, 1)
        self.assertEqual(ce.exception.message, message)

    @patch("pyocr.cuneiform.temp_file")
    @patch("codecs.open")
    @patch("subprocess.Popen")
    def test_text_non_rgb_image(self, popen, copen, temp_file):
        """This tests that image_to_string works with non RGB mode images and
        that image is converted in function."""
        image = self.image.convert("L")
        popen.return_value = self.stdout
        copen.return_value = self.text_file
        temp_file.return_value = self.enter
        output = cuneiform.image_to_string(image, builder=self.builder)
        self.assertEqual(output, self._get_file_content("text").strip())
        popen.assert_called_once_with(
            ["cuneiform", "-f", "text", "-o", self.tmp_filename, "-"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )


class TestCuneiformDigits(BaseTest):

    @patch("pyocr.tesseract.get_version")
    def setUp(self, get_version):
        get_version.return_value = (4, 0, 0)
        self.builder = builders.DigitBuilder()
        self.image = Image.new(mode="RGB", size=(1, 1))

    def test_digits_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            cuneiform.image_to_string(self.image, builder=self.builder)

    def test_digits_box_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            cuneiform.image_to_string(self.image,
                                      builder=self.builder)


class TestCuneiformWordBox(BaseTest):
    """
    These tests make sure that cuneiform box handling works fine.
    """
    @patch("pyocr.tesseract.get_version")
    def setUp(self, get_version):
        get_version.return_value = (4, 0, 0)
        self.builder = builders.WordBoxBuilder()
        self.image = Image.new(mode="RGB", size=(1, 1))
        self.text_file = StringIO(self._get_file_content("cuneiform.words"))
        self.stdout = MagicMock()
        self.stdout.stdout.read.return_value = b"Cuneiform for Linux 1.1.0\n"
        self.stdout.wait.return_value = 0
        self.tmp_filename = "/tmp/cuneiform_n0qfk87otxt"
        self.enter = MagicMock()
        self.enter.__enter__.return_value = MagicMock()
        self.enter.__enter__.return_value.configure_mock(
            name=self.tmp_filename
        )

    @patch("pyocr.cuneiform.temp_file")
    @patch("codecs.open")
    @patch("subprocess.Popen")
    def test_word(self, popen, copen, temp_file):
        popen.return_value = self.stdout
        copen.return_value = self.text_file
        temp_file.return_value = self.enter
        output = cuneiform.image_to_string(self.image,
                                           builder=self.builder)
        popen.assert_called_once_with(
            ["cuneiform", "-f", "hocr", "-o", self.tmp_filename, "-"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        for box in output:
            self.assertIsInstance(box, builders.Box)

    @patch("subprocess.Popen")
    def test_word_error(self, popen):
        stdout = MagicMock()
        message = ("Cuneiform for Linux 1.1.0\n"
                   "Magick: Improper image header (example.png) reported by "
                   "coders/png.c:2932 (ReadPNGImage)\n")
        stdout.stdout.read.return_value = message.encode()
        stdout.wait.return_value = 1
        popen.return_value = stdout
        with self.assertRaises(cuneiform.CuneiformError) as ce:
            cuneiform.image_to_string(self.image,
                                      builder=self.builder)
        self.assertEqual(ce.exception.status, 1)
        self.assertEqual(ce.exception.message, message)


class TestCuneiformLineBox(BaseTest):
    """
    These tests make sure that cuneiform box handling works fine.
    """
    @patch("pyocr.tesseract.get_version")
    def setUp(self, get_version):
        get_version.return_value = (4, 0, 0)
        self.builder = builders.LineBoxBuilder()
        self.image = Image.new(mode="RGB", size=(1, 1))
        self.text_file = StringIO(self._get_file_content("cuneiform.lines"))
        self.stdout = MagicMock()
        self.stdout.stdout.read.return_value = b"Cuneiform for Linux 1.1.0\n"
        self.stdout.wait.return_value = 0
        self.tmp_filename = "/tmp/cuneiform_n0qfk87otxt"
        self.enter = MagicMock()
        self.enter.__enter__.return_value = MagicMock()
        self.enter.__enter__.return_value.configure_mock(
            name=self.tmp_filename
        )

    @patch("pyocr.cuneiform.temp_file")
    @patch("codecs.open")
    @patch("subprocess.Popen")
    def test_line(self, popen, copen, temp_file):
        popen.return_value = self.stdout
        copen.return_value = self.text_file
        temp_file.return_value = self.enter
        output = cuneiform.image_to_string(self.image,
                                           builder=self.builder)
        popen.assert_called_once_with(
            ["cuneiform", "-f", "hocr", "-o", self.tmp_filename, "-"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        for box in output:
            self.assertIsInstance(box, builders.LineBox)

    @patch("subprocess.Popen")
    def test_line_error(self, popen):
        message = ("Cuneiform for Linux 1.1.0\n"
                   "Magick: Improper image header (example.png) reported by "
                   "coders/png.c:2932 (ReadPNGImage)\n")
        self.stdout.stdout.read.return_value = message.encode()
        self.stdout.wait.return_value = 1
        popen.return_value = self.stdout
        with self.assertRaises(cuneiform.CuneiformError) as ce:
            cuneiform.image_to_string(self.image,
                                      builder=self.builder)
        self.assertEqual(ce.exception.status, 1)
        self.assertEqual(ce.exception.message, message)
