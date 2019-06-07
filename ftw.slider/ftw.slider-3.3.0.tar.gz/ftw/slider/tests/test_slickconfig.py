from ftw.builder import Builder
from ftw.builder import create
from ftw.slider.contents.container import validate_slick_config
from ftw.slider.testing import SLIDER_FUNCTIONAL_TESTING
from ftw.slider.testing import SLIDER_INTEGRATION_TESTING
from ftw.testbrowser import browsing
from helper import LanguageToolHelper
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from unittest2 import TestCase
import json


class TestSliderConfig(TestCase, LanguageToolHelper):

    layer = SLIDER_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

        setRoles(self.portal, TEST_USER_ID, ['Contributor', 'Manager'])
        login(self.portal, TEST_USER_NAME)

        self.folder = create(Builder('folder')
                             .titled(u'Folder'))

    @browsing
    def test_slider_adds_slick_config_if_available(self, browser):
        self.manage_set_language_settings(default='de',
                                          supported=['de'],
                                          use_combined=False,
                                          content_negotiation=False)

        container = create(Builder('slider container')
                           .within(self.folder)
                           .having(slick_config=json.dumps({'is_chuck': True}))
                           .titled(u'Slider Container'))

        create(Builder('slider pane')
               .within(container)
               .titled(u'Pane 1')
               .with_dummy_image())

        browser.login().visit(self.folder)

        self.assertEqual(
            {u'labels': {u'pause': u'Pause',
                         u'play': u'Abspielen',
                         u'prev': u'Vorheriges Bild',
                         u'next': u'N\xe4chstes Bild'},
             u'is_chuck': True},
            json.loads(browser.css('#slider-panes').first.get('data-settings')))


class TestSliderConfigValidator(TestCase):

    layer = SLIDER_INTEGRATION_TESTING

    def test_convert_to_json_is_possible(self):
        self.assertEqual(
            True,
            validate_slick_config(json.dumps({'is_chuck': True}))
            )

    def test_convert_to_json_is_not_possible(self):
        self.assertEqual(
            False,
            validate_slick_config("no_json")
            )
