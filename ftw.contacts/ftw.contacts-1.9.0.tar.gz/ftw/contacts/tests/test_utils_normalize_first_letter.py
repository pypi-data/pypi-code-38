from ftw.contacts.testing import FTW_CONTACTS_FUNCTIONAL_TESTING
from ftw.contacts.utils import normalized_first_letter
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase


class TestNormalizedFirstLetter(TestCase):

    layer = FTW_CONTACTS_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_returns_uppercase_letter(self):
        self.assertEquals('T', normalized_first_letter('test'))

    def test_normalizes_umlauts(self):
        self.assertEquals('A', normalized_first_letter('\xc3\xa4bc'))
