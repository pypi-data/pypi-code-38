from ftw.contacts.testing import FTW_CONTACTS_FUNCTIONAL_TESTING
from ftw.contacts.utils import encode
from unittest2 import TestCase


class TestContactTitle(TestCase):

    layer = FTW_CONTACTS_FUNCTIONAL_TESTING

    def test_encode_unicode_to_utf8(self):
        self.assertEqual("\xc3\xbcber", encode(u"\xfcber"))

    def test_return_utf8_strings(self):
        self.assertEqual("\xc3\xbcber", encode("\xc3\xbcber"))

    def test_return_empty_string_if_text_is_none(self):
        self.assertEqual("", encode(None))
