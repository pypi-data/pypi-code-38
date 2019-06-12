from ftw.builder import Builder
from ftw.builder import create
from ftw.contacts.testing import FTW_CONTACTS_FUNCTIONAL_TESTING
from ftw.contacts.utils import get_organization
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase


class TestGetOrganization(TestCase):

    layer = FTW_CONTACTS_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.contactfolder = create(
            Builder('contact folder').titled(u'Contact folder'))

    def test_return_empty_if_no_portal_types_are_defined(self):

        self.assertEqual("", get_organization(self.contactfolder))

    def test_return_empty_if_portal_type_not_found(self):
        self.assertEqual(
            "", get_organization(self.contactfolder, ['ftw.contacts.Contact']))

    def test_return_title_of_found_portal_type(self):
        contact = create(Builder('contact')
                         .with_minimal_info(u'Ch\xf6ck', u'4orris')
                         .within(self.contactfolder))

        self.assertEqual(
            "Contact folder",
            get_organization(contact, ['ftw.contacts.ContactFolder']))
