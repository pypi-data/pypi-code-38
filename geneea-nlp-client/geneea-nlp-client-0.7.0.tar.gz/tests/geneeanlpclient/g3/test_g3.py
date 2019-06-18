from unittest import TestCase

from geneeanlpclient.g3 import Paragraph
from tests.geneeanlpclient.g3.examples import example_obj


class TestG3(TestCase):
    def test_token_offsetToken(self):
        obj = example_obj()

        self.assertEqual(obj.paragraphs[0].sentences[0].tokens[0], obj.paragraphs[0].sentences[0].tokens[0].offsetToken(0))

        # non-existing offset yields None
        self.assertEqual(None, obj.paragraphs[0].sentences[0].tokens[0].offsetToken(-1))
        self.assertEqual(None, obj.paragraphs[0].sentences[0].tokens[0].offsetToken(-10))
        self.assertEqual(None, obj.paragraphs[0].sentences[0].tokens[1].offsetToken(-2))
        self.assertEqual(None, obj.paragraphs[0].sentences[0].tokens[1].offsetToken(-10))

        self.assertEqual(obj.paragraphs[0].sentences[0].tokens[0], obj.paragraphs[0].sentences[0].tokens[1].offsetToken(-1))
        self.assertEqual(obj.paragraphs[0].sentences[0].tokens[1], obj.paragraphs[0].sentences[0].tokens[2].offsetToken(-1))
        self.assertEqual(obj.paragraphs[0].sentences[0].tokens[0], obj.paragraphs[0].sentences[0].tokens[2].offsetToken(-2))

        # non-existing offset yields None
        self.assertEqual(None, obj.paragraphs[0].sentences[0].tokens[-1].offsetToken(1))
        self.assertEqual(None, obj.paragraphs[0].sentences[0].tokens[-1].offsetToken(10))
        self.assertEqual(None, obj.paragraphs[0].sentences[0].tokens[-2].offsetToken(2))
        self.assertEqual(None, obj.paragraphs[0].sentences[0].tokens[-2].offsetToken(10))

        self.assertEqual(obj.paragraphs[0].sentences[0].tokens[1], obj.paragraphs[0].sentences[0].tokens[0].offsetToken(1))
        self.assertEqual(obj.paragraphs[0].sentences[0].tokens[2], obj.paragraphs[0].sentences[0].tokens[0].offsetToken(2))
        self.assertEqual(obj.paragraphs[0].sentences[0].tokens[2], obj.paragraphs[0].sentences[0].tokens[1].offsetToken(1))

    def test_token_charSpan_extractText(self):
        obj = example_obj()

        para0 = obj.paragraphs[0]
        para1 = obj.paragraphs[1]

        self.assertEqual('Angela', para0.sentences[0].tokens[0].charSpan.extractText(para0.text))
        self.assertEqual('New', para0.sentences[0].tokens[3].charSpan.extractText(para0.text))
        self.assertEqual('Angela', para1.sentences[0].tokens[0].charSpan.extractText(para1.text))
        self.assertEqual('Germany', para1.sentences[0].tokens[3].charSpan.extractText(para1.text))
        self.assertEqual('That', para1.sentences[2].tokens[0].charSpan.extractText(para1.text))
        self.assertEqual('amazing', para1.sentences[2].tokens[2].charSpan.extractText(para1.text))

    def test_getParaByType(self):
        obj = example_obj()
        self.assertEqual(obj.paragraphs[0], obj.getParaByType(Paragraph.TYPE_TITLE))
        self.assertEqual(obj.paragraphs[1], obj.getParaByType(Paragraph.TYPE_BODY))
