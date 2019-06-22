import unittest

from io import StringIO
from itertools import product
from random import randint
from unittest.mock import patch

from pyocr import builders

from .tests_base import BaseTest


class TestTextBuilder(unittest.TestCase):
    @patch("pyocr.tesseract.get_version")
    def setUp(self, get_version):
        get_version.return_value = (4, 0, 0)
        self.builder = builders.TextBuilder()

    def test_init(self):
        self.assertListEqual(self.builder.file_extensions, ["txt"])
        self.assertListEqual(self.builder.tesseract_flags, ["--psm", "3"])
        self.assertListEqual(self.builder.tesseract_configs, [])
        self.assertEqual(self.builder.tesseract_layout, 3)
        self.assertListEqual(self.builder.cuneiform_args, ["-f", "text"])

    @patch("pyocr.tesseract.get_version")
    def test_init_cuneiform_params(self, get_version):
        get_version.return_value = (4, 0, 0)
        # XXX Maybe overkill?
        # this check all combinations of parameters
        for cun_dotmat, cun_fax, cun_sglcol in product(*((False, True),) * 3):
            builder = builders.TextBuilder(
                cuneiform_dotmatrix=cun_dotmat,
                cuneiform_fax=cun_fax,
                cuneiform_singlecolumn=cun_sglcol
            )
            if cun_dotmat:
                self.assertIn("--dotmatrix", builder.cuneiform_args)
            else:
                self.assertNotIn("--dotmatrix", builder.cuneiform_args)
            if cun_fax:
                self.assertIn("--fax", builder.cuneiform_args)
            else:
                self.assertNotIn("--fax", builder.cuneiform_args)
            if cun_sglcol:
                self.assertIn("--singlecolumn", builder.cuneiform_args)
            else:
                self.assertNotIn("--singlecolumn", builder.cuneiform_args)

    def test_read_file(self):
        txt = "first line\nsecond line\n0123456789\n🖨  "
        input_fh = StringIO(txt)
        output = self.builder.read_file(input_fh)
        self.assertEqual(output, txt.strip())

    def test_write_file(self):
        output = StringIO()
        txt = "first line\nsecond line\n0123456789\n🖨  "
        self.builder.write_file(output, txt)
        output.seek(0)
        self.assertEqual(output.read(), txt)

    def test_start_line(self):
        box = builders.Box("word", ((10, 11), (12, 13)))
        self.builder.start_line(box)
        self.assertListEqual(self.builder.built_text, [""])

    def test_add_word_no_line(self):
        box = builders.Box("word", ((10, 11), (12, 13)))
        with self.assertRaises(IndexError):
            self.builder.add_word(box.content, box)

    def test_add_word(self):
        box = builders.Box("word", ((10, 11), (12, 13)))
        self.builder.start_line(box)
        self.builder.add_word(box.content, box)
        self.assertEqual(self.builder.built_text[0], box.content)
        self.builder.add_word(box.content, box)
        self.assertEqual(self.builder.built_text[0],
                         box.content + " " + box.content)

    def test_end_line(self):
        before = list(self.builder.built_text)
        self.builder.end_line()
        self.assertEqual(self.builder.built_text, before)

    def test_get_output(self):
        box = builders.Box("word", ((10, 11), (12, 13)))
        self.builder.start_line(box)
        self.builder.add_word("word1", box)
        self.builder.add_word("word2", box)
        self.builder.start_line(box)
        self.builder.add_word("word3", box)
        self.builder.add_word("word4", box)
        self.assertEqual(self.builder.get_output(), "word1 word2\nword3 word4")

    def test_str_method(self):
        self.assertEqual(str(self.builder), "Raw text")


class TestWordBoxBuilder(BaseTest):

    @patch("pyocr.tesseract.get_version")
    def setUp(self, get_version):
        get_version.return_value = (4, 0, 0)
        self.builder = builders.WordBoxBuilder()

    @patch("pyocr.tesseract.get_version")
    def test_init_tesseract_version_3(self, get_version):
        for version in range(6):
            get_version.return_value = (3, version, 0)
            builder = builders.WordBoxBuilder()
            self.assertListEqual(builder.tesseract_flags, ["-psm", "1"])
            self.assertListEqual(builder.file_extensions, ["html", "hocr"])
            self.assertListEqual(builder.tesseract_configs, ["hocr"])
            self.assertListEqual(builder.cuneiform_args, ["-f", "hocr"])
            self.assertListEqual(builder.word_boxes, [])
            self.assertEqual(builder.tesseract_layout, 1)

    @patch("pyocr.tesseract.get_version")
    def test_init_tesseract_version_4(self, get_version):
        get_version.return_value = (4, 0, 0)
        builder = builders.WordBoxBuilder()
        self.assertListEqual(builder.tesseract_flags, ["--psm", "1"])
        self.assertListEqual(builder.file_extensions, ["html", "hocr"])
        self.assertListEqual(builder.tesseract_configs, ["hocr"])
        self.assertListEqual(builder.cuneiform_args, ["-f", "hocr"])
        self.assertListEqual(builder.word_boxes, [])
        self.assertEqual(builder.tesseract_layout, 1)

    def test_read_file(self):
        words = self.builder.read_file(self._get_file_handle("words"))
        for word in words:
            self.assertIsInstance(word, builders.Box)

    def test_empty_read_file(self):
        output = StringIO()
        self.assertListEqual(self.builder.read_file(output), [])

    def test_read_file_bbox(self):
        words = self.builder.read_file(self._get_file_handle("words_bbox"))
        for word in words:
            self.assertIsInstance(word, builders.Box)
        self.assertNotEqual(words[-1].content, "preguieoso.")

    def test_write_file(self):
        output = StringIO()
        boxes = [
            builders.Box("word1", ((10, 11), (12, 13)), 95),
            builders.Box("word2", ((11, 12), (13, 14))),
            builders.Box("word3", ((12, 13), (14, 15))),
            builders.Box("word4", ((13, 14), (15, 16)), 87),
        ]
        self.builder.write_file(output, boxes)
        output.seek(0)
        output = output.read()
        for box in boxes:
            self.assertIn(box.content, output)
            self.assertIn("{} {} {} {}".format(
                box.position[0][0], box.position[0][1],
                box.position[1][0], box.position[1][1],
            ), output)
            self.assertIn(str(box.confidence), output)

    def test_start_line(self):
        box = builders.Box("word", ((1, 2), (3, 4)))
        before = list(self.builder.word_boxes)
        self.builder.start_line(box)
        self.assertEqual(self.builder.word_boxes, before)

    def test_add_word(self):
        box = builders.Box("word", ((1, 2), (3, 4)), 42)
        self.builder.add_word(box.content, box.position, box.confidence)
        for box in self.builder.word_boxes:
            self.assertIsInstance(box, builders.Box)
        self.assertEqual(self.builder.word_boxes[0], box)

    def test_end_line(self):
        before = list(self.builder.word_boxes)
        self.builder.end_line()
        self.assertEqual(self.builder.word_boxes, before)

    def test_get_output(self):
        boxes = [
            builders.Box("word1", ((10, 11), (12, 13)), 95),
            builders.Box("word2", ((11, 12), (13, 14))),
            builders.Box("word3", ((12, 13), (14, 15))),
            builders.Box("word4", ((13, 14), (15, 16)), 87),
        ]
        for box in boxes:
            self.builder.add_word(box.content, box.position, box.confidence)
        output = self.builder.get_output()
        for box, box_expected in zip(output, boxes):
            self.assertIsInstance(box, builders.Box)
            self.assertEqual(box, box_expected)
            self.assertEqual(box.content, box_expected.content)

    def test_str_method(self):
        self.assertEqual(str(self.builder), "Word boxes")


class TestLineBoxBuilder(BaseTest):

    @patch("pyocr.tesseract.get_version")
    def setUp(self, get_version):
        get_version.return_value = (4, 0, 0)
        self.builder = builders.LineBoxBuilder()

    @patch("pyocr.tesseract.get_version")
    def test_init_tesseract_version_3(self, get_version):
        for version in range(6):
            get_version.return_value = (3, version, 0)
            builder = builders.LineBoxBuilder()
            self.assertListEqual(builder.tesseract_flags, ["-psm", "1"])
            self.assertListEqual(builder.file_extensions, ["html", "hocr"])
            self.assertListEqual(builder.tesseract_configs, ["hocr"])
            self.assertListEqual(builder.cuneiform_args, ["-f", "hocr"])
            self.assertListEqual(builder.lines, [])
            self.assertEqual(builder.tesseract_layout, 1)

    @patch("pyocr.tesseract.get_version")
    def test_init_tesseract_version_4(self, get_version):
        get_version.return_value = (4, 0, 0)
        builder = builders.LineBoxBuilder()
        self.assertListEqual(builder.tesseract_flags, ["--psm", "1"])
        self.assertListEqual(builder.file_extensions, ["html", "hocr"])
        self.assertListEqual(builder.tesseract_configs, ["hocr"])
        self.assertListEqual(builder.cuneiform_args, ["-f", "hocr"])
        self.assertListEqual(builder.lines, [])
        self.assertEqual(builder.tesseract_layout, 1)

    def test_read_file(self):
        for input_fh in (self._get_file_handle("tesseract.lines"),
                         self._get_file_handle("cuneiform.lines")):
            lines = self.builder.read_file(input_fh)
            for line in lines:
                self.assertIsInstance(line, builders.LineBox)

    def test_empty_read_file(self):
        empty = StringIO()
        self.assertListEqual(self.builder.read_file(empty), [])

    def test_write_file(self):
        output_fh = StringIO()
        lines = []
        for l in range(4):
            boxes = []
            for b in range(4):
                word = "word" + str(4*l+b)
                position = ((4*l+b, 4*l+b+1), (4*l+b+2, 4*l+b+3))
                boxes.append(builders.Box(word, position, randint(0, 100)))
            line_position = ((4*l, 4*(l+1)), (4*l+2, 4*(l+1)+2))
            lines.append(builders.LineBox(boxes, line_position))
        self.builder.write_file(output_fh, lines)
        output_fh.seek(0)
        output = output_fh.read()
        for line in lines:
            for box in line.word_boxes:
                self.assertIn(box.content, output)
                self.assertIn("{} {} {} {}".format(
                    box.position[0][0], box.position[0][1],
                    box.position[1][0], box.position[1][1],
                ), output)
                self.assertIn(str(box.confidence), output)

    def test_start_line(self):
        position = ((1, 2), (3, 4))
        self.builder.start_line(position)
        self.assertEqual(len(self.builder.lines), 1)
        self.assertListEqual(self.builder.lines,
                             [builders.LineBox([], position)])
        self.builder.start_line(position)
        self.assertEqual(len(self.builder.lines), 1)
        self.assertListEqual(self.builder.lines,
                             [builders.LineBox([], position)])

    def test_add_word_no_line(self):
        box = builders.Box("word", ((1, 2), (3, 4)), 42)
        with self.assertRaises(IndexError):
            self.builder.add_word(box.content, box.position, box.confidence)
        self.assertListEqual(self.builder.lines, [])

    def test_end_line(self):
        before = list(self.builder.lines)
        self.builder.end_line()
        self.assertEqual(self.builder.lines, before)

    def test_get_output(self):
        lines = []
        for l in range(4):
            boxes = []
            for b in range(4):
                word = "word" + str(4*l+b)
                position = ((4*l+b, 0), (0, 0))
                boxes.append(builders.Box(word, position, randint(0, 100)))
            line_position = ((4*l, 4*(l+1)), (4*l+2, 4*(l+1)+2))
            lines.append(builders.LineBox(boxes, line_position))

        for line in lines:
            self.builder.start_line(line.position)
            for word in line.word_boxes:
                self.builder.add_word(word.content, word.position,
                                      word.confidence)
            self.builder.end_line()  # could be useful in future
        output = self.builder.get_output()
        for line, line_expected in zip(output, lines):
            self.assertIsInstance(line, builders.LineBox)
            self.assertEqual(line, line_expected)

    def test_str_method(self):
        self.assertEqual(str(self.builder), "Line boxes")


class TestDigitBuilder(unittest.TestCase):
    @patch("pyocr.tesseract.get_version")
    def setUp(self, get_version):
        get_version.return_value = (4, 0, 0)
        self.builder = builders.DigitBuilder()

    def test_init(self):
        self.assertIn("digits", self.builder.tesseract_configs)

    def test_str_method(self):
        self.assertEqual(str(self.builder), "Digits raw text")


class TestDigitLineBoxBuilder(unittest.TestCase):
    @patch("pyocr.tesseract.get_version")
    def setUp(self, get_version):
        get_version.return_value = (4, 0, 0)
        self.builder = builders.DigitLineBoxBuilder()

    def test_init(self):
        self.assertIn("digits", self.builder.tesseract_configs)

    def test_str_method(self):
        self.assertEqual(str(self.builder), "Digit line boxes")
