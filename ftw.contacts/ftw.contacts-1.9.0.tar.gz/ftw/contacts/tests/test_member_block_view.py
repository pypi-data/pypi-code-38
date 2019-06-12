from ftw.builder import Builder
from ftw.builder import create
from ftw.contacts.testing import FTW_CONTACTS_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from plone.api.content import delete
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase

import transaction


class TestMemberBlockView(TestCase):

    layer = FTW_CONTACTS_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.contactfolder = create(
            Builder('contact folder').titled(u'Contact folder'))

    @browsing
    def test_call_view_does_not_fail(self, browser):
        contact = create(Builder('contact')
                         .with_minimal_info(u'Ch\xf6ck', u'4orris')
                         .within(self.contactfolder))

        member_block = create(Builder('member block')
                              .within(self.contactfolder)
                              .contact(contact)
                              .titled(u"A MemberBlock")
                              .having(show_title=True))

        browser.login().visit(member_block, view="block_view")
        self.assertEqual(u'A MemberBlock', browser.css('h3').first.text)

    @browsing
    def test_block_with_deleted_contact_returns_hint_for_editors(self, browser):

        contact = create(Builder('contact')
                         .with_minimal_info(u'Ch\xf6ck', u'4orris')
                         .within(self.contactfolder))

        member_block = create(Builder('member block')
                              .within(self.contactfolder)
                              .contact(contact))

        delete(contact, check_linkintegrity=False)
        transaction.commit()

        browser.login().visit(member_block, view="block_view")

        self.assertEqual(1, len(browser.css('#member-no-contact-exist')))

    @browsing
    def test_block_without_contact_renders_hint_for_editors(self, browser):
        page = create(Builder('sl content page'))
        contact = create(Builder('contact')
                         .with_minimal_info(u'Ch\xf6ck', u'4orris')
                         .within(self.contactfolder))
        member_block = create(Builder('member block').within(page).contact(contact))

        # Remove the referenced contact.
        member_block.contact = None
        transaction.commit()

        browser.raise_http_errors = False
        browser.login().visit(member_block, view='block_view')
        self.assertEqual(
            [
                'The related contact does no longer exists. '
                'Delete this content or edit it to replace the deleted with an existing contact'
            ],
            browser.css('#member-no-contact-exist').text,
            'A hint should be rendered about the block\'s missing contact.'
        )

    @browsing
    def test_call_returns_member_view(self, browser):
        contact = create(Builder('contact')
                         .with_maximal_info(u'Ch\xf6ck', u'4orris')
                         .within(self.contactfolder))

        member_block = create(Builder('member block')
                              .within(self.contactfolder)
                              .contact(contact))

        browser.login().visit(member_block, view="block_view")

        self.assertEqual(0, len(browser.css('#member-no-contact-exist')))
        self.assertEqual(0, len(browser.css('#member-empty')))
        self.assertEqual(1, len(browser.css('.memberContactInfo')))

    @browsing
    def test_block_with_deleted_contact_returns_hint_for_anonymous(self, browser):
        contact = create(Builder('contact')
                         .with_minimal_info(u'Ch\xf6ck', u'4orris')
                         .within(self.contactfolder))

        member_block = create(Builder('member block')
                              .within(self.contactfolder)
                              .contact(contact))

        delete(contact, check_linkintegrity=False)
        transaction.commit()

        browser.visit(member_block, view="block_view")

        self.assertEqual(1, len(browser.css('#member-empty')))

    @browsing
    def test_block_without_contact_renders_hint_for_anonymous(self, browser):
        page = create(Builder('sl content page'))
        contact = create(Builder('contact')
                         .with_minimal_info(u'Ch\xf6ck', u'4orris')
                         .within(self.contactfolder))
        member_block = create(Builder('member block').within(page).contact(contact))

        # Remove the referenced contact.
        member_block.contact = None
        transaction.commit()

        browser.raise_http_errors = False
        browser.visit(member_block, view='block_view')
        self.assertEqual(
            [],
            browser.css('#member-no-contact-exist').text,
            'Blocks without contact should render nothing for anonymous users.'
        )

    @browsing
    def test_function_is_acquired(self, browser):
        """
        This test makes sure that the function of the contact is rendered
        on the member block if the address is acquired.
        """
        contact = create(Builder('contact')
                         .with_minimal_info(u'Dent', u'Arthur')
                         .having(address=u'End Of The Universe')
                         .having(function=u'Function of the contact')
                         .within(self.contactfolder))

        member_block = create(Builder('member block')
                              .within(self.contactfolder)
                              .having(acquire_address=True)
                              .contact(contact))

        browser.visit(member_block, view='block_view')
        self.assertEqual(
            ['Dent Arthur Function of the contact'],
            browser.css('.memberContactInfo').text
        )

    @browsing
    def test_memberblock_function_takes_precendence_over_contact_function(self, browser):
        """
        This test makes sure that the function of the memberblock
        takes precedence over the acquired function from the contact.
        """
        contact = create(Builder('contact')
                         .with_minimal_info(u'Dent', u'Arthur')
                         .having(address=u'End Of The Universe')
                         .having(function=u'Function of the contact')
                         .within(self.contactfolder))

        member_block = create(Builder('member block')
                              .within(self.contactfolder)
                              .having(acquire_address=True)
                              .having(function=u'Function of the member block')
                              .contact(contact))

        browser.visit(member_block, view='block_view')
        self.assertEqual(
            ['Dent Arthur Function of the member block'],
            browser.css('.memberContactInfo').text
        )
