from django import test

from ievv_opensource.utils import text_utils


class TestNormalizeWhitespace(test.TestCase):
    def test_spaces(self):
        self.assertEqual(text_utils.normalize_whitespace('Hello    cruel   world'),
                         'Hello cruel world')

    def test_newlines(self):
        self.assertEqual(text_utils.normalize_whitespace('Hello\ncruel\nworld'),
                         'Hello cruel world')

    def test_tabs(self):
        self.assertEqual(text_utils.normalize_whitespace('Hello\tcruel\tworld'),
                         'Hello cruel world')
