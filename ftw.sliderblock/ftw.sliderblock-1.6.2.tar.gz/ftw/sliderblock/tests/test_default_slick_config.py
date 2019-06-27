from ftw.builder import Builder
from ftw.builder import create
from ftw.sliderblock.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class TestDefaultSlickConfig(FunctionalTestCase):

    def setUp(self):
        super(TestDefaultSlickConfig, self).setUp()
        self.grant('Manager')

    @browsing
    def test_default_slick_config_when_adding_a_slider_block(self, browser):
        """
        When adding a slider block, the field for the Slick configuration
        is prefilled with the value stored in the registry.
        """

        registry = getUtility(IRegistry)
        self.assertEqual(
            '{"autoplay": true, "autoplaySpeed": 2000}',
            registry['ftw.sliderblock.default_slick_config']
        )

        browser.login()
        contentpage = create(Builder('sl content page').titled(u'A page'))
        browser.visit(contentpage)

        factoriesmenu.add('SliderBlock')

        self.assertEqual(
            '{"autoplay": true, "autoplaySpeed": 2000}',
            browser.find_field_by_text('Configuration').value
        )

    @browsing
    def test_customized_default_slick_config(self, browser):
        """
        When adding a slider block, the field for the Slick configuration
        is prefilled with a customized value.
        """

        registry = getUtility(IRegistry)
        registry['ftw.sliderblock.default_slick_config'] = u'{"foo": "bar"}'

        browser.login()
        contentpage = create(Builder('sl content page').titled(u'A page'))
        browser.visit(contentpage)

        factoriesmenu.add('SliderBlock')

        self.assertEqual(
            '{"foo": "bar"}',
            browser.find_field_by_text('Configuration').value
        )

    @browsing
    def test_fallback_default_slick_config_when_registry_record_is_missing(self, browser):
        """
        When adding a slider block, the field for the Slick configuration
        is prefilled with a default value even if the registry record is missing
        because it uses a fallback value.
        """

        registry = getUtility(IRegistry)
        del registry.records['ftw.sliderblock.default_slick_config']

        browser.login()
        contentpage = create(Builder('sl content page').titled(u'A page'))
        browser.visit(contentpage)

        factoriesmenu.add('SliderBlock')

        self.assertEqual(
            '{"autoplay": true, "autoplaySpeed": 2000}',
            browser.find_field_by_text('Configuration').value
        )

    @browsing
    def test_fallback_default_slick_config_when_registry_record_is_empty(self, browser):
        """
        When adding a slider block, the field for the Slick configuration
        is prefilled with a default value even if the registry record is empty
        because it uses a fallback value.
        """

        registry = getUtility(IRegistry)
        registry['ftw.sliderblock.default_slick_config'] = u'{}'

        browser.login()
        contentpage = create(Builder('sl content page').titled(u'A page'))
        browser.visit(contentpage)

        factoriesmenu.add('SliderBlock')

        self.assertEqual(
            '{}',
            browser.find_field_by_text('Configuration').value
        )
