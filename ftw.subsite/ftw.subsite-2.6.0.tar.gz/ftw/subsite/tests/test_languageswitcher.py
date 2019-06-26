from ftw.builder import Builder
from ftw.builder import create
from ftw.subsite.testing import FTW_SUBSITE_FUNCTIONAL_TESTING
from ftw.subsite.tests.helpers import introduce_language_subsites
from ftw.subsite.tests.pages import LanguageSwitcher
from ftw.testbrowser import browsing
from unittest2 import TestCase


class TestLanguageSwitcher(TestCase):

    layer = FTW_SUBSITE_FUNCTIONAL_TESTING

    @browsing
    def test_shows_other_referenced_languages(self, browser):
        german = create(Builder('subsite')
                        .titled(u'Subsite DE')
                        .with_language('de'))
        french = create(Builder('subsite')
                        .titled(u'Subsite FR')
                        .with_language('fr'))
        italian = create(Builder('subsite')
                         .titled(u'Subsite IT')
                         .with_language('it'))
        introduce_language_subsites(german, french, italian)

        browser.login().visit(german)
        self.assertEquals([u'Fran\xe7ais', u'Italiano'],
                          LanguageSwitcher().languages)

    @browsing
    def test_going_to_another_language(self, browser):
        german = create(Builder('subsite')
                        .titled(u'Subsite DE')
                        .with_language('de'))
        french = create(Builder('subsite')
                        .titled(u'Subsite FR')
                        .with_language('fr'))
        introduce_language_subsites(german, french)

        browser.login().visit(german)
        LanguageSwitcher().click_language(u'Fran\xe7ais')
        self.assertEquals(french.absolute_url(), browser.url)
        LanguageSwitcher().click_language(u'Deutsch')
        self.assertEquals(german.absolute_url(), browser.url)

    @browsing
    def test_switch_is_invisible_unless_languages_hooked_up(self, browser):
        german = create(Builder('subsite')
                        .titled(u'Subsite DE')
                        .with_language('de'))
        french = create(Builder('subsite')
                        .titled(u'Subsite FR')
                        .with_language('fr'))

        browser.login().visit(german)
        self.assertFalse(LanguageSwitcher().available)
        introduce_language_subsites(german, french)
        browser.login().visit(german)
        self.assertTrue(LanguageSwitcher().available)

    @browsing
    def test_other_site_not_visible_when_no_subsite_language_defined(self, browser):
        german = create(Builder('subsite')
                        .titled(u'Subsite DE')
                        .with_language('de'))
        unkown = create(Builder('subsite')
                        .titled(u'Subsite ...'))
        introduce_language_subsites(german, unkown)

        browser.login().visit(german)
        self.assertEquals([], LanguageSwitcher().languages)

    @browsing
    def test_does_not_show_subsites_of_other_language_groups(self, browser):
        german = create(Builder('subsite')
                        .titled(u'Subsite DE')
                        .with_language('de'))
        french = create(Builder('subsite')
                        .titled(u'Subsite FR')
                        .with_language('fr'))
        italian = create(Builder('subsite')
                         .titled(u'Subsite IT')
                         .with_language('it'))
        spanish = create(Builder('subsite')
                         .titled(u'Subsite ES')
                         .with_language('es'))

        introduce_language_subsites(german, french)
        introduce_language_subsites(italian, spanish)

        browser.login()

        self.assertEquals(
            {'german': [u'Fran\xe7ais'],
             'french': [u'Deutsch'],
             'italian': [u'Espa\xf1ol'],
             'spanish': [u'Italiano']},

            {'german': LanguageSwitcher().visit(german).languages,
             'french': LanguageSwitcher().visit(french).languages,
             'italian': LanguageSwitcher().visit(italian).languages,
             'spanish': LanguageSwitcher().visit(spanish).languages})

    @browsing
    def test_hooking_up_language_subsites_with_site_root(self, browser):
        # Assumed that the site root is configured to be english.
        german = create(Builder('subsite')
                        .titled(u'Subsite')
                        .with_language('de')
                        .having(link_site_in_languagechooser=True))
        french = create(Builder('subsite')
                        .titled(u'Subsite')
                        .with_language('fr')
                        .having(link_site_in_languagechooser=True))

        introduce_language_subsites(german, french)

        browser.login()

        self.assertEquals(
            {'site root': [u'Deutsch', u'Fran\xe7ais'],
             'german': [u'English', u'Fran\xe7ais'],
             'french': [u'Deutsch', u'English']},

            {'site root': LanguageSwitcher().visit_portal().languages,
             'german': LanguageSwitcher().visit(german).languages,
             'french': LanguageSwitcher().visit(french).languages})

    @browsing
    def test_listing_only_site_root_works(self, browser):
        german = create(Builder('subsite')
                        .titled(u'Subsite')
                        .with_language('de')
                        .having(link_site_in_languagechooser=True))

        browser.login().visit(german)
        self.assertEquals([u'English'], LanguageSwitcher().languages)

    @browsing
    def test_current_link_is_current_language(self, browser):
        german = create(Builder('subsite')
                        .titled(u'Subsite DE')
                        .with_language('de'))
        french = create(Builder('subsite')
                        .titled(u'Subsite FR')
                        .with_language('fr'))
        introduce_language_subsites(german, french)

        browser.login().visit(german)
        self.assertEquals(u'Deutsch', LanguageSwitcher().current)

    @browsing
    def test_current_link_is_language_on_plone_site_root(self, browser):
        create(Builder('subsite')
               .titled(u'Subsite')
               .with_language('de')
               .having(link_site_in_languagechooser=True))

        browser.login().visit()
        self.assertEquals(u'English', LanguageSwitcher().current)
