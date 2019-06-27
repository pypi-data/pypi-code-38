from ftw.builder import Builder
from ftw.builder import create
import transaction
from ftw.sliderblock.testing import FTW_SLIDERBLOCK_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase


class TestSliderBlockContentType(TestCase):

    layer = FTW_SLIDERBLOCK_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestSliderBlockContentType, self).setUp()
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager', 'Site Administrator'])
        transaction.commit()

    @browsing
    def test_add_sliderblock(self, browser):
        contentpage = create(Builder('sl content page').titled(u'A page'))

        browser.login().visit(contentpage)
        factoriesmenu.add('SliderBlock')
        browser.fill({'Title': u'This is a SliderBlock'})

        browser.find_button_by_label('Save').click()
        browser.visit(contentpage)

        self.assertTrue(len(browser.css('.sl-block')), 'Expect one block')
