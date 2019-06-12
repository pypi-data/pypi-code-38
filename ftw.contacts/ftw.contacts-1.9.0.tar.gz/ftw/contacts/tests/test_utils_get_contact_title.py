from ftw.builder import Builder
from ftw.builder import create
from ftw.contacts.testing import FTW_CONTACTS_FUNCTIONAL_TESTING
from ftw.contacts.utils import get_contact_title
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase


class TestContactTitle(TestCase):

    layer = FTW_CONTACTS_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_returns_placeholder_if_no_first_last_and_org(self):
        contact = create(Builder('contact'))
        self.assertEqual(u"...", get_contact_title(contact))

    def test_returns_org_if_no_first_name(self):
        contact = create(Builder('contact').having(
            organization=u"CIA",
            lastname=u"Norris"))
        self.assertEqual(u"CIA", get_contact_title(contact))

    def test_returns_org_if_no_last_name(self):
        contact = create(Builder('contact').having(
            organization=u"CIA",
            firstname=u"Chuck"))
        self.assertEqual(u"CIA", get_contact_title(contact))

    def test_returns_org_if_no_first_and_last_name(self):
        contact = create(Builder('contact').having(
            organization=u"CIA"))
        self.assertEqual("CIA", get_contact_title(contact))

    def test_returns_last_and_first_name_if_exists_without_org(self):
        contact = create(Builder('contact').having(
            firstname=u"Chuck",
            lastname=u"Norris"))
        self.assertEqual("Norris Chuck", get_contact_title(contact))

    def test_returns_last_and_first_name_if_exists_with_org(self):
        contact = create(Builder('contact').having(
            firstname=u"Chuck",
            lastname=u"N\xf6rris",
            organization=u"CIA"))
        self.assertEqual(u"N\xf6rris Chuck", get_contact_title(contact))

    def test_returns_first_and_last_name_if_exists_with_format_natural(self):
        contact = create(Builder('contact').having(
            firstname=u"Chuck",
            lastname=u"N\xf6rris"))
        self.assertEqual(
            u"Chuck N\xf6rris",
            get_contact_title(contact, display="natural"))
