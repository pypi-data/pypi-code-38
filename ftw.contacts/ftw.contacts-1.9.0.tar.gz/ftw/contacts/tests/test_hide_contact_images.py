from ftw.builder import Builder
from ftw.builder import create
from ftw.contacts.tests import FunctionalTestCase
from ftw.testbrowser import browsing


class TestHideContactImages(FunctionalTestCase):

    def setUp(self):
        super(TestHideContactImages, self).setUp()
        self.grant('Manager')

    @browsing
    def test_contact_images_are_hidden_when_hide_images_checkbox_is_active(self, browser):
        contactfolder = create(Builder('contact folder')
                               .titled(u'Contact folder')
                               .having(hide_contacts_image=True))

        contact = create(Builder('contact')
                         .with_maximal_info(u'Chuck', u'Norris')
                         .within(contactfolder))

        browser.login().visit(contact, view='contact_summary')

        self.assertEqual(1, len(browser.css('div.contactSummary')))
        self.assertEqual(0, len(browser.css('a.contactImage')))

    @browsing
    def test_contact_images_are_shown_when_hide_images_checkbox_is_deactivated(self, browser):
        contactfolder = create(Builder('contact folder')
                               .titled(u'Contact folder')
                               .having(hide_contacts_image=False))

        contact = create(Builder('contact')
                         .with_maximal_info(u'Chuck', u'Norris')
                         .within(contactfolder))

        browser.login().visit(contact, view='contact_summary')

        self.assertEqual(1, len(browser.css('a.contactImage')))
