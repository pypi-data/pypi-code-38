from ftw.builder import Builder
from ftw.builder import create
from ftw.contacts.browser.contactfolder import ContactFolderReload
from ftw.contacts.testing import FTW_CONTACTS_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase
import json


class TestContactFolderReloadLetter(TestCase):

    layer = FTW_CONTACTS_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.catalog = getToolByName(self.portal, 'portal_catalog')

        self.contactfolder = create(
            Builder('contact folder').titled(u'Contact folder'))

        self.view = self.contactfolder.unrestrictedTraverse('reload_contacts')

    @browsing
    def test_returns_html_letters(self, browser):
        create(Builder('contact')
               .with_minimal_info(u'Chuck', u'4orris')
               .within(self.contactfolder))

        create(Builder('contact')
               .with_minimal_info(u'J\xe4mes', u'B\xf6nd')
               .within(self.contactfolder))

        brains = self.catalog(portal_type="ftw.contacts.Contact")

        browser.open_html(self.view.rendered_letters(brains, 'B'))

        self.assertEqual(2, len(browser.css('.letter.withContent')))
        self.assertEqual(1, len(browser.css('.letter.active')))


class TestContactFolderReloadContact(TestCase):

    layer = FTW_CONTACTS_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.catalog = getToolByName(self.portal, 'portal_catalog')

        self.contactfolder = create(
            Builder('contact folder').titled(u'Contact folder'))

        self.view = self.contactfolder.unrestrictedTraverse('reload_contacts')

    @browsing
    def test_returns_html_contacts(self, browser):
        create(Builder('contact')
               .with_minimal_info(u'Chuck', u'4orris')
               .within(self.contactfolder))

        create(Builder('contact')
               .with_minimal_info(u'J\xe4mes', u'B\xf6nd')
               .within(self.contactfolder))

        brains = self.catalog(portal_type="ftw.contacts.Contact")

        browser.open_html(self.view.rendered_contacts(
            brains, 0, 10))

        self.assertEqual(2, len(browser.css('.contactSummary')))

    @browsing
    def test_restrict_from_and_to(self, browser):
        create(Builder('contact')
               .with_minimal_info(u'Chuck', u'4orris')
               .within(self.contactfolder))

        create(Builder('contact')
               .with_minimal_info(u'J\xe4mes', u'B\xf6nd')
               .within(self.contactfolder))

        create(Builder('contact')
               .with_minimal_info(u'Max', u'Muster')
               .within(self.contactfolder))

        brains = self.catalog(portal_type="ftw.contacts.Contact")

        browser.open_html(self.view.rendered_contacts(brains, 1, 3))

        self.assertEqual(
            2, len(browser.css('.contactSummary')),
            "Should return only the second and third contact")

        browser.open_html(self.view.rendered_contacts(brains, 0, 1))

        self.assertEqual(
            1, len(browser.css('.contactSummary')),
            "Should return only the first contact")


class TestContactFolderReloadView(TestCase):

    layer = FTW_CONTACTS_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.catalog = getToolByName(self.portal, 'portal_catalog')

        self.contactfolder = create(
            Builder('contact folder').titled(u'Contact folder'))

        self.view = self.contactfolder.unrestrictedTraverse('reload_contacts')

    @browsing
    def test_json_string_on_call(self, browser):
        create(Builder('contact')
               .with_minimal_info(u'Chuck', u'4orris')
               .within(self.contactfolder))

        create(Builder('contact')
               .with_minimal_info(u'J\xe4mes', u'B\xf6nd')
               .within(self.contactfolder))

        create(Builder('contact')
               .with_minimal_info(u'Max', u'Muster')
               .within(self.contactfolder))

        data = json.loads(self.view())

        self.assertEqual(3, data.get('max_contacts'))

        browser.open_html(data.get('contacts'))

        self.assertEqual(3, len(browser.css('.contactSummary')))

        browser.open_html(data.get('letters'))

        self.assertEqual(3, len(browser.css('.letter.withContent')))

    @browsing
    def test_restrict_contacts_with_searchable_text(self, browser):
        create(Builder('contact')
               .with_minimal_info(u'Chuck', u'4orris')
               .within(self.contactfolder))

        create(Builder('contact')
               .with_minimal_info(u'J\xe4mes', u'B\xf6nd')
               .within(self.contactfolder))

        create(Builder('contact')
               .with_minimal_info(u'Max', u'Muster')
               .within(self.contactfolder))

        self.request.form['searchable_text'] = "B\xc3\xb6"

        view = ContactFolderReload(self.contactfolder, self.request)
        data = json.loads(view())

        self.assertEqual(1, data.get('max_contacts'))

        browser.open_html(data.get('contacts'))

        self.assertEqual(1, len(browser.css('.contactSummary')))

        browser.open_html(data.get('letters'))

        self.assertEqual(1, len(browser.css('.letter.withContent')))

    @browsing
    def test_search_with_special_chars(self, browser):
        create(Builder('contact')
               .with_minimal_info(u'Chuck', u'4orris')
               .within(self.contactfolder))

        self.request.form['searchable_text'] = "Ch/*+uck 4or"

        view = ContactFolderReload(self.contactfolder, self.request)
        data = json.loads(view())

        self.assertEqual(
            1, data.get('max_contacts'),
            "There should be one contact, the 'Chuck 4orris'. " +
            "The special chars are replaced with an empty string.")

    @browsing
    def test_search_only_special_chars(self, browser):
        create(Builder('contact')
               .with_minimal_info(u'Chuck', u'4orris')
               .within(self.contactfolder))

        self.request.form['searchable_text'] = "  /*+  "

        view = ContactFolderReload(self.contactfolder, self.request)
        data = json.loads(view())

        self.assertEqual(
            1, data.get('max_contacts'),
            "There should be all contacts." +
            "The special chars are replaced with an empty string.")

    @browsing
    def test_search_with_empty_string(self, browser):
        create(Builder('contact')
               .with_minimal_info(u'Chuck', u'4orris')
               .within(self.contactfolder))

        self.request.form['searchable_text'] = ""

        view = ContactFolderReload(self.contactfolder, self.request)
        data = json.loads(view())

        self.assertEqual(
            1, data.get('max_contacts'), "There should be all contacts")

    @browsing
    def test_max_contacts_with_letters_filter(self, browser):
        create(Builder('contact')
               .with_minimal_info(u'Chuck', u'Borris')
               .within(self.contactfolder))

        create(Builder('contact')
               .with_minimal_info(u'J\xe4mes', u'B\xf6nd')
               .within(self.contactfolder))

        create(Builder('contact')
               .with_minimal_info(u'Max', u'Muster')
               .within(self.contactfolder))

        create(Builder('contact')
               .with_minimal_info(u'Max', u'4uster')
               .within(self.contactfolder))

        self.request.form['letter'] = "B"

        view = ContactFolderReload(self.contactfolder, self.request)
        data = json.loads(view())

        self.assertEqual(
            2, data.get('max_contacts'),
            """Becauswe the letter B is active, the max_contacts should
            be only contain the Chuck and James contact, means '2'"""
            )

        browser.open_html(data.get('contacts'))

        self.assertEqual(
            2, len(browser.css('.contactSummary')),
            """Should return the Chuck and james contact because the
            letter filter""")

        browser.open_html(data.get('letters'))

        self.assertEqual(
            3, len(browser.css('.letter.withContent')),
            """Should show all available letters, means the #, M and B""")

    @browsing
    def test_max_contacts_with_special_letters_filter(self, browser):
        create(Builder('contact')
               .with_minimal_info(u'Chuck', u'Borris')
               .within(self.contactfolder))

        create(Builder('contact')
               .with_minimal_info(u'J\xe4mes', u'B\xf6nd')
               .within(self.contactfolder))

        create(Builder('contact')
               .with_minimal_info(u'Bud', u'Muster')
               .within(self.contactfolder))

        create(Builder('contact')
               .with_minimal_info(u'Max', u'4uster')
               .within(self.contactfolder))

        self.request.form['letter'] = "#"

        view = ContactFolderReload(self.contactfolder, self.request)
        data = json.loads(view())

        self.assertEqual(
            1, data.get('max_contacts'),
            """Becauswe the letter # is active, only the contacts
            with a special char should be shown. Means, the Max 4uster"""
            )

        browser.open_html(data.get('contacts'))

        self.assertEqual(
            1, len(browser.css('.contactSummary')),
            """Should return the Max contact because the letter filter""")

        browser.open_html(data.get('letters'))

        self.assertEqual(
            3, len(browser.css('.letter.withContent')),
            """Should show all available letters, means the #, M and B""")
