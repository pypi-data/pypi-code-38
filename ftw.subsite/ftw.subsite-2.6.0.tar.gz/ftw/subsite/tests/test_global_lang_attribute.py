from ftw.builder import Builder
from ftw.builder import create
from ftw.subsite.testing import FTW_SUBSITE_FUNCTIONAL_TESTING
from ftw.subsite.tests.helpers import LanguageSetter
from ftw.testbrowser import browsing
from unittest2 import TestCase
import transaction


class TestSubsiteForceLanguage(TestCase, LanguageSetter):

    layer = FTW_SUBSITE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.setup_language_tool()
        self.make_document_addable_on_subsite()

    def setup_language_tool(self):
        default = 'en'
        supported = ['en', 'de', 'fr']
        self.set_language_settings(default=default, supported=supported)

    def make_document_addable_on_subsite(self):
        types_tool = self.portal.portal_types
        subsite_fti = types_tool.get('ftw.subsite.Subsite')
        subsite_fti.allowed_content_types = ('Document', )
        transaction.commit()

    @browsing
    def test_global_lang_is_en(self, browser):
        self.assertEquals(
            'en',
            browser.login().visit().css('html').first.attrib['lang'])

    @browsing
    def test_plone_negotiator_still_works_on_non_subsite(self, browser):
        document = create(Builder('document').having(language='fr'))
        self.assertEquals(
            'fr',
            browser.login().visit(document).css('html').first.attrib['lang'])

    @browsing
    def test_global_lang_is_set_on_subsite(self, browser):
        subsite = create(Builder('subsite').having(force_language='de'))
        self.assertEquals(
            'de',
            browser.login().visit(subsite).css('html').first.attrib['lang'])

    @browsing
    def test_plone_negotiator_looses_against_subsite_language(self, browser):
        subsite = create(Builder('subsite').having(force_language='de'))
        document = create(Builder('document')
                          .within(subsite)
                          .having(language='fr'))

        self.assertEquals(
            'de',
            browser.login().visit(document).css('html').first.attrib['lang'])
