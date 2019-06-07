from ftw.builder import Builder
from ftw.builder import create
from ftw.slider.testing import SLIDER_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import plone
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase
import transaction


class TestSliderCreation(TestCase):
    layer = SLIDER_FUNCTIONAL_TESTING

    def setUp(self):
        setRoles(self.layer['portal'], TEST_USER_ID, ['Contributor', 'Manager'])
        transaction.commit()

    @browsing
    def test_slider_container_is_addable(self, browser):
        browser.login().open()
        factoriesmenu.add('Slider Container')
        browser.fill({'Title': 'Container 1'}).submit()
        self.assertEquals('Container 1', plone.first_heading())
        self.assertEquals('ftw-slider-container', plone.portal_type())

    @browsing
    def test_redirect_if_there_is_already_a_container(self, browser):
        container = create(Builder('slider container').titled(u'Slider Container'))
        browser.login().open()
        factoriesmenu.add('Slider Container')
        self.assertEquals(container.absolute_url(), browser.url)
