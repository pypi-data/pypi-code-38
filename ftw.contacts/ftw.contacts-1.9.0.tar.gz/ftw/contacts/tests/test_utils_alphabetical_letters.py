from ftw.builder import Builder
from ftw.builder import create
from ftw.contacts.testing import FTW_CONTACTS_FUNCTIONAL_TESTING
from ftw.contacts.utils import AlphabeticLetters
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase


class TestAlphabeticalSubjectListing(TestCase):

    layer = FTW_CONTACTS_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.catalog = getToolByName(self.portal, 'portal_catalog')

    def test_mark_current_letter(self):
        brains = self.catalog(portal_type="ftw.contacts.Contact")
        letters = AlphabeticLetters().letters('I', brains)
        letter = [
            letter.get('label') for letter in letters
            if letter.get('current')
            ][0]

        self.assertEqual('I', letter)

    def test_mark_no_letter(self):
        brains = self.catalog(portal_type="ftw.contacts.Contact")
        letters = AlphabeticLetters().letters('', brains)
        letter = [
            letter.get('label') for letter in letters
            if letter.get('current')
            ]

        self.assertEqual([], letter)

    def test_mark_special_letter_as_current_letter(self):
        brains = self.catalog(portal_type="ftw.contacts.Contact")
        letters = AlphabeticLetters().letters('#', brains)
        letter = [
            letter.get('label') for letter in letters
            if letter.get('current')
            ][0]

        self.assertEqual('#', letter)

    def test_mark_letters_with_contents(self):
        contactfolder = create(
            Builder('contact folder').titled(u'Contact folder'))

        create(Builder('contact')
               .with_maximal_info(u'Chuck', u'4orris')
               .within(contactfolder))

        create(Builder('contact')
               .with_maximal_info(u'J\xe4mes', u'B\xf6nd')
               .within(contactfolder))

        brains = self.catalog(portal_type="ftw.contacts.Contact")
        letters = AlphabeticLetters().letters('I', brains)

        letter = [
            letter.get('label') for letter in letters
            if letter.get('has_contents')
            ]

        self.assertEqual(['B', '#'], letter)
