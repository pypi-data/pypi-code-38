from ftw.contacts.testing import FTW_CONTACTS_FUNCTIONAL_TESTING
from ftw.contacts.utils import make_sortable
from unittest2 import TestCase


class TestMakeSortable(TestCase):

    layer = FTW_CONTACTS_FUNCTIONAL_TESTING

    def test_text_is_lowercased(self):
        self.assertEquals('foo',
                          make_sortable('FoO'))

    def test_umlauts_are_normalized(self):
        self.assertEquals('loffel',
                          make_sortable('L\xc3\xb6ffel'))

    def test_cedillas_are_removed(self):
        self.assertEquals('francais',
                          make_sortable('fran\xc3\xa7ais'))
