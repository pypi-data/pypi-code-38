from ftw.builder import Builder
from ftw.builder import create
from ftw.subsite.testing import FTW_SUBSITE_FUNCTIONAL_TESTING
from ftw.subsite.tests.helpers import introduce_language_subsites
from ftw.testbrowser import browsing
from plone.app.testing import applyProfile
from unittest2 import TestCase
import json
import transaction


class TestLanguageMobileButton(TestCase):

    layer = FTW_SUBSITE_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestLanguageMobileButton, self).setUp()
        portal = self.layer['portal']
        applyProfile(portal, 'ftw.mobile:default')
        transaction.commit()

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
        button = browser.css('#subsitelanguage-mobile-button a').first
        button_data = json.loads(button.attrib['data-mobile_data'])

        self.assertEquals(u'Fran\xe7ais', button_data[0]['label'])
        self.assertEquals(u'Italiano', button_data[1]['label'])

        self.assertEquals(french.absolute_url(), button_data[0]['url'])
        self.assertEquals(italian.absolute_url(), button_data[1]['url'])
