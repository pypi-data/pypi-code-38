from ftw.builder import Builder
from ftw.builder import create
from ftw.subsite.testing import FTW_SUBSITE_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import plone
from unittest2 import TestCase


class TestSubsite(TestCase):

    layer = FTW_SUBSITE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    @browsing
    def test_subsite_addable(self, browser):
        browser.login().visit()
        factoriesmenu.add('Subsite')
        browser.fill({'Title': 'This is a Subsite'}).save()

        self.assertEquals('This is a Subsite', plone.first_heading())

    @browsing
    def test_subsite_has_simplelayout_as_default_page(self, browser):
        subsite = create(Builder('subsite').titled(u'A Subsite'))
        browser.login().visit(subsite)
        self.assertTrue(browser.css('.sl-simplelayout'))
