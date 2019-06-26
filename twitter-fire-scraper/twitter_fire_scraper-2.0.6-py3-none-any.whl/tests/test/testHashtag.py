# coding=utf-8
import unittest

# noinspection PyUnresolvedReferences
import __init__
from hashtags import contains_hashtag, extract_hashtags


class TestHashtags(unittest.TestCase):

    def test_extract(self):
        self.assertEqual(extract_hashtags("I love the #beach and #sand!"), {"#beach", "#sand"})

        self.assertEqual(extract_hashtags(u"Pizza is so good! #~# 🍕"), set())

        self.assertEqual(extract_hashtags("Man, Hashtags (#) are # nice # to # use # as # list # columns!"), set())

    def _disabled_test_unicode(self):  # Expect to fail this.
        # TODO add RTL unicode support to hashtag detection.
        self.assertEqual(extract_hashtags(u"مرحبا# to the #world!"), {u'مرحبا#', '#world'})

    def test_simple_contains(self):
        self.assertTrue(contains_hashtag('I enjoy #swimming!', 'swimming'))
        self.assertTrue(contains_hashtag('I enjoy #swimming so much!', 'swimming'))

        self.assertFalse((contains_hashtag("I dislike #coldswimming.", "#swimming")))
        self.assertFalse((contains_hashtag("I dislike #coldswimming.", "#cold")))
        self.assertTrue(contains_hashtag("I dislike #coldswimming.", "#coldswimming"))
