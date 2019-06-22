import unittest
import xml.dom.minidom

from pyocr import builders


class TestBox(unittest.TestCase):
    """
    These tests ensure the Box features are what they should.
    """
    def setUp(self):
        self.box1 = builders.Box("word1", ((15, 22), (23, 42)))
        self.box1_bis = builders.Box("word1_bis", ((15, 22), (23, 42)))
        self.box2 = builders.Box("word2", ((30, 5), (40, 15)), 95)
        self.box_unicode = builders.Box("\xe9", ((1, 2), (3, 4)))

    def test_init(self):
        self.assertEqual(self.box1.content, "word1")
        self.assertSequenceEqual(self.box1.position, ((15, 22), (23, 42)))
        self.assertEqual(self.box1.confidence, 0)
        self.assertEqual(self.box2.confidence, 95)

    def test_get_xml_tag(self):
        impl = xml.dom.minidom.getDOMImplementation()
        doc = impl.createDocument(None, "root", None)
        tag = self.box1.get_xml_tag(doc)
        self.assertEqual(len(tag.childNodes), 1)
        self.assertEqual(tag.getAttribute("class"), "ocrx_word")
        self.assertEqual(tag.getAttribute("title"),
                         "bbox 15 22 23 42; x_wconf 0")
        self.assertEqual(tag.firstChild.data, "word1")

    def test_str_method(self):
        self.assertEqual(str(self.box1), "word1 15 22 23 42")

    def test_str_unicode(self):
        self.assertEqual(str(self.box_unicode), "\xe9 1 2 3 4")

    def test_box_not_equal_none(self):
        self.assertNotEqual(self.box1, None)

    def test_box_equal(self):
        self.assertEqual(self.box1, self.box1_bis)

    def test_box_not_equal(self):
        self.assertNotEqual(self.box1, self.box2)

    def test_box_lower(self):
        self.assertLess(self.box2, self.box1)
        self.assertLessEqual(self.box2, self.box1)

    def test_box_greater(self):
        self.assertGreater(self.box1, self.box2)
        self.assertGreaterEqual(self.box1, self.box2)

    def test_box_equal_not_box(self):
        self.assertNotEqual(self.box1, 0)
        self.assertNotEqual(self.box1, [])

    def test_hash(self):
        self.assertEqual(hash(self.box1), hash(self.box1_bis))
        self.assertNotEqual(hash(self.box1), hash(self.box2))


class TestLineBox(unittest.TestCase):

    def setUp(self):
        box1 = builders.Box("word1", ((15, 22), (23, 30)))
        box2 = builders.Box("word2", ((25, 23), (30, 32)))
        box3 = builders.Box("word3", ((32, 25), (40, 32)), 95)
        box4 = builders.Box("word4", ((41, 18), (44, 33)), 98)
        box_unicode = builders.Box("\xe9", ((1, 2), (3, 4)), 98)
        self.line1 = builders.LineBox(
            [box1, box2, box3, box4],
            ((14, 15), (45, 33))
        )
        self.line1_bis = builders.LineBox(
            [box1, box2],
            ((14, 15), (45, 33))
        )
        self.line2 = builders.LineBox(
            [box3, box4],
            ((30, 5), (53, 20))
        )
        self.line1_dupl = builders.LineBox(
            [box1, box2, box3, box4],
            ((14, 15), (45, 33))
        )
        self.line_unicode = builders.LineBox(
            [box1, box_unicode],
            ((1, 2), (3, 4))
        )

    def test_init(self):
        self.assertEqual(len(self.line1.word_boxes), 4)
        self.assertSequenceEqual(self.line1.position, ((14, 15), (45, 33)))
        self.assertEqual(self.line1.content, "word1 word2 word3 word4")

    def test_get_xml_tag(self):
        impl = xml.dom.minidom.getDOMImplementation()
        doc = impl.createDocument(None, "root", None)
        tag = self.line1.get_xml_tag(doc)
        self.assertEqual(len(tag.childNodes),
                         2 * len(self.line1.word_boxes) - 1)
        self.assertEqual(tag.getAttribute("class"), "ocr_line")
        self.assertEqual(tag.getAttribute("title"), "bbox 14 15 45 33")
        self.assertEqual(tag.firstChild.firstChild.data, "word1")
        self.assertEqual(tag.lastChild.firstChild.data, "word4")

    def test_line_str(self):
        expected = "[\n"
        for box in self.line1.word_boxes:
            expected += "  " + box.__str__() + "\n"
        expected += "] 14 15 45 33"
        self.assertEqual(str(self.line1), expected)

    def test_str_unicode(self):
        self.assertEqual(
            str(self.line_unicode),
            "[\n  word1 15 22 23 30\n  \xe9 1 2 3 4\n] 1 2 3 4"
        )

    def test_line_not_equal_none(self):
        self.assertNotEqual(self.line1, None)

    def test_box_equal(self):
        self.assertEqual(self.line1, self.line1_bis)

    def test_box_not_equal(self):
        self.assertNotEqual(self.line1, self.line2)

    def test_line_lower(self):
        self.assertLess(self.line2, self.line1)
        self.assertLessEqual(self.line2, self.line1)

    def test_line_greater(self):
        self.assertGreater(self.line1, self.line2)
        self.assertGreaterEqual(self.line1, self.line2)

    def test_hash(self):
        self.assertIsNotNone(hash(self.line1))
        self.assertNotEqual(hash(self.line1), hash(self.line1_bis))
        self.assertNotEqual(hash(self.line1), hash(self.line2))
        self.assertEqual(hash(self.line1), hash(self.line1_dupl))
