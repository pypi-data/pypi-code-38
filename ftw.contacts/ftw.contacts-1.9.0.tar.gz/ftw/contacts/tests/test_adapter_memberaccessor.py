from ftw.builder import Builder
from ftw.builder import create
from ftw.contacts.interfaces import IMemberAccessor
from ftw.contacts.testing import FTW_CONTACTS_FUNCTIONAL_TESTING
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase


class TestMemberAccessor(TestCase):

    layer = FTW_CONTACTS_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.catalog = getToolByName(self.portal, 'portal_catalog')
        self.contactfolder = create(
            Builder('contact folder').titled(u'Contact folder'))

    def test_get_attr_on_member_if_not_aquire_address(self):
        contact = create(Builder('contact')
                         .with_minimal_info(u'Chuck', u'4\xf6rris')
                         .having(address='Bundesplatz 1')
                         .within(self.contactfolder))

        member_block = create(Builder('member block')
                              .within(self.contactfolder)
                              .contact(contact)
                              .having(address='Frankenstrasse 53'))

        self.assertEqual(u'Frankenstrasse 53', IMemberAccessor(member_block).address)

    def test_get_attr_on_contact_if_aquire_address(self):
        contact = create(Builder('contact')
                         .with_minimal_info(u'Chuck', u'4\xf6rris')
                         .having(address='Bundesplatz 1')
                         .within(self.contactfolder))

        member_block = create(Builder('member block')
                              .within(self.contactfolder)
                              .contact(contact)
                              .having(address='Frankenstrasse 53',
                                      acquire_address=True))

        self.assertEqual(u'Bundesplatz 1', IMemberAccessor(member_block).address)

    def test_get_attr_on_member_if_aquire_address_but_attr_not_exist(self):
        contact = create(Builder('contact')
                         .with_minimal_info(u'Chuck', u'4\xf6rris')
                         .within(self.contactfolder))

        member_block = create(Builder('member block')
                              .within(self.contactfolder)
                              .contact(contact)
                              .having(
                                  acquire_address=True,
                                  show_title=True))

        self.assertEqual(False, hasattr(contact, 'show_title'))
        self.assertEqual(True, IMemberAccessor(member_block).show_title)

    def test_get_not_existing_attr_returns_none(self):
        contact = create(Builder('contact')
                         .with_minimal_info(u'Chuck', u'4\xf6rris')
                         .within(self.contactfolder))

        member_block = create(Builder('member block')
                              .within(self.contactfolder)
                              .contact(contact))

        self.assertEqual(None, IMemberAccessor(member_block).not_existing_attr)
