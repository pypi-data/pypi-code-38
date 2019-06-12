from ftw.builder import Builder
from ftw.builder import create
from ftw.contacts.interfaces import IMemberBlock
from ftw.contacts.testing import FTW_CONTACTS_FUNCTIONAL_TESTING
from ftw.contacts.utils import get_backreferences
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase


class TestBackReferences(TestCase):

    layer = FTW_CONTACTS_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Site Administrator'])

        self.contactfolder = create(
            Builder('contact folder').titled(u'Contact folder'))

    def test_references_in_a_list(self):
        contact = create(Builder('contact')
                         .with_minimal_info(u'Ch\xf6ck', u'4orris')
                         .within(self.contactfolder))

        member_block = create(Builder('member block')
                              .within(self.contactfolder)
                              .contact(contact)
                              .having(
                                  firstname=u"J\xf6mes"))

        self.assertEqual(
            [member_block], get_backreferences(contact, IMemberBlock))

    def test_empty_list_if_no_references_found(self):
        contact = create(Builder('contact')
                         .with_minimal_info(u'Ch\xf6ck', u'4orris')
                         .within(self.contactfolder))

        self.assertEqual([], get_backreferences(contact, IMemberBlock))

    def test_do_not_append_objs_with_no_permission(self):
        contact = create(Builder('contact')
                         .with_minimal_info(u'Ch\xf6ck', u'4orris')
                         .within(self.contactfolder))

        member_block = create(Builder('member block')
                              .within(self.contactfolder)
                              .contact(contact)
                              .having(
                                  firstname=u"J\xf6mes"))

        self.assertEqual(
            [member_block], get_backreferences(contact, IMemberBlock))

        member_block.manage_permission('View', roles=[])
        logout()

        self.assertEqual([], get_backreferences(contact, IMemberBlock))
