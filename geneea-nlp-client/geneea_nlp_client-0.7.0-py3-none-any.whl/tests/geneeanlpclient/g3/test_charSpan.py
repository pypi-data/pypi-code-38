
from unittest import TestCase

from geneeanlpclient.g3.model import CharSpan


class TestCharSpan(TestCase):
    def test_withLen(self):
        self.assertEqual(CharSpan(0, 8), CharSpan.withLen(0, 8))
        self.assertEqual(CharSpan(4, 8), CharSpan.withLen(4, 4))
        self.assertEqual(CharSpan(10, 11), CharSpan.withLen(10, 1))

    def test_len(self):
        self.assertEqual(len(CharSpan(4, 8)), 4)
        self.assertEqual(len(CharSpan(10, 11)), 1)
        self.assertEqual(len(CharSpan(10, 10)), 0)

    def test_isValid(self):
        self.assertTrue(CharSpan(4, 8).isValid())
        self.assertTrue(CharSpan(4, 5).isValid())
        self.assertTrue(CharSpan(0, 1).isValid())

        self.assertFalse(CharSpan(4, 4).isValid())
        self.assertFalse(CharSpan(4, 3).isValid())
        self.assertFalse(CharSpan(4, -1).isValid())
        self.assertFalse(CharSpan(-1, 3).isValid())
        self.assertFalse(CharSpan(-1, -1).isValid())

    def test_checks(self):
        with self.assertRaises(ValueError):
            CharSpan.withLen(-1, 2)
        with self.assertRaises(ValueError):
            CharSpan.withLen(1, -2)
        with self.assertRaises(ValueError):
            CharSpan.withLen(-1, -2)
        with self.assertRaises(ValueError):
            CharSpan.withLen(4, 0)

    def test_extractText(self):
        self.assertEqual(CharSpan(2, 5).extractText('abcdefgh'), 'cde')
        self.assertEqual(CharSpan(2, 3).extractText('abcdefgh'), 'c')
        self.assertEqual(CharSpan(2, 2).extractText('abcdefgh'), '')
        self.assertEqual(CharSpan(0, 3).extractText('abcdefgh'), 'abc')
        self.assertEqual(CharSpan(0, 1).extractText('abcdefgh'), 'a')
        self.assertEqual(CharSpan(0, 0).extractText('abcdefgh'), '')
        self.assertEqual(CharSpan(2, 4).extractText('abcd'), 'cd')
        self.assertEqual(CharSpan(3, 4).extractText('abcd'), 'd')
        self.assertEqual(CharSpan(4, 4).extractText('abcd'), '')

        # span is outside of the text
        with self.assertRaises(ValueError):
            self.assertEqual(CharSpan(3, 6).extractText('abcd'), '')
