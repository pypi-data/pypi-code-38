# coding=utf-8
import unittest

from tcell_agent.utils.compat import to_bytes, a_string


class CompatTest(unittest.TestCase):

    # use u"hí".encode("utf-8") as a replacement for bytes("hí", "utf-8")
    # because bytes() in python2 does not take an encoding
    def test_to_bytes(self):
        self.assertEqual(to_bytes("hí"), u"hí".encode("utf-8"))
        self.assertEqual(to_bytes(u"hí"), u"hí".encode("utf-8"))
        # test that an encoded string doesn't get encoded twice
        self.assertEqual(to_bytes(u"hí".encode("utf-8")), u"hí".encode("utf-8"))

    def test_a_string(self):
        self.assertFalse(a_string([]))
        self.assertFalse(a_string(None))
        self.assertFalse(a_string(1))
        self.assertTrue(a_string("hi"))
        self.assertTrue(a_string(u"hi"))
        self.assertTrue(a_string(b"hi"))
        self.assertTrue(a_string("hí"))
        self.assertTrue(a_string(u"hí"))
        self.assertTrue(a_string(u"hí".encode("utf-8")))
