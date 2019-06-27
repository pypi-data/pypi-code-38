from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.interfaces import ISimplelayoutDefaultSettings
from ftw.sliderblock.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.dexterity import erroneous_fields
from plone import api
from plone.app.textfield import RichTextValue
import json
import transaction


class TestSliderBlockRendering(FunctionalTestCase):

    def setUp(self):
        super(TestSliderBlockRendering, self).setUp()
        self.grant('Manager')

    def _create_test_content(self):
        """
        This method can be used to set up some test content. The method
        may be called from various test case, but not all (if they require
        very special test data).
        """
        self.page = create(Builder('sl content page'))

        slick_config = json.dumps(
            {'arrows': 'false', 'autoplaySpeed': 1000, 'autoplay': 'false'}
        )
        block_builder = Builder('sliderblock')
        block_builder.within(self.page)
        block_builder.titled('SliderBlock title')
        block_builder.having(slick_config=slick_config)
        self.block = create(block_builder)

        create(Builder('slider pane')
               .within(self.block)
               .titled(u'Pane 1')
               .with_dummy_image())
        create(Builder('slider pane')
               .within(self.block)
               .titled(u'Pane 2')
               .with_dummy_image())

    @browsing
    def test_slider_panes_visible(self, browser):
        self._create_test_content()
        browser.login().visit(self.block, view='@@block_view')
        self.assertEquals(2, len(browser.css('.sliderPane')))

    @browsing
    def test_custom_slick_config(self, browser):
        self._create_test_content()
        browser.login().visit(self.block, view='@@block_view')

        self.assertEquals(
            {'labels': {'pause': 'Pause',
                        'play': 'Play',
                        'prev': 'Previous',
                        'next': 'Next'},
             'arrows': 'false', 'autoplaySpeed': 1000, 'autoplay': 'false'},
            json.loads(browser.css('.sliderWrapper').first.attrib['data-settings']))

    @browsing
    def test_custom_slick_config_has_no_newline(self, browser):
        """
        This test makes sure the slick config does not contain newlines
        and is valid json.
        """
        self._create_test_content()
        browser.login().visit(self.block, view='edit.json')
        browser.parse(browser.json['content'])
        browser.fill(
            {'form.widgets.slick_config': u'{"foo": true, \n"bar": 2000}'}
        ).save()

        browser.login().visit(self.page)
        self.assertDictEqual(
            json.loads(
                '{"labels": {"prev": "Previous", "play": "Play", "pause": "Pause", "next": "Next"}, "foo": true, "bar": 2000}'
            ),
            json.loads(
                browser.css('.sl-block-content div').first.attrib['data-settings']
            )
        )

    @browsing
    def test_emtpy_slick_config(self, browser):
        page = create(Builder('sl content page'))
        block = create(Builder('sliderblock')
                       .within(page)
                       .titled('SliderBlock title')
                       .having(slick_config=''))

        create(Builder('slider pane')
               .within(block)
               .titled(u'Pane 1')
               .with_dummy_image())

        browser.login().open(page)
        self.assertEqual(
            '{}',
            browser.css('.sl-block-content div').first.attrib['data-settings'])

    @browsing
    def test_images_are_cropped_and_down_scaled_by_default(self, browser):
        self._create_test_content()
        browser.login().visit(self.block, view='@@block_view')

        img = browser.css('.sliderPane img').first
        self.assertEquals('1200', img.attrib['width'])
        self.assertEquals('800', img.attrib['height'])

    @browsing
    def test_images_are_not_cropped_and_upscaled_option(self, browser):
        self._create_test_content()
        self.block.crop_image = False
        transaction.commit()
        browser.login().visit(self.block, view='@@block_view')

        img = browser.css('.sliderPane img').first
        self.assertEquals('800', img.attrib['width'])
        self.assertEquals('800', img.attrib['height'])

    @browsing
    def test_slider_pane_without_text_does_not_render_any_content(self, browser):
        """
        This test makes sure that a slider pane without text does not render any
        content (neither the title nor the text).
        """
        page = create(Builder('sl content page'))
        container = create(Builder('sliderblock')
                           .titled(u'Title of the slider block')
                           .within(page))
        create(Builder('slider pane')
               .titled(u'The title of the pane')
               .with_dummy_image()
               .within(container))

        browser.login().visit(container, view='@@block_view')
        self.assertEqual(
            [''],
            browser.css('.sliderPane').text
        )

    @browsing
    def test_slider_pane_with_text_does_only_render_the_text(self, browser):
        """
        This test makes sure that a slider pane having some text will really
        render the text.
        """
        page = create(Builder('sl content page'))
        container = create(Builder('sliderblock')
                           .titled(u'Title of the slider block')
                           .within(page))
        create(Builder('slider pane')
               .titled(u'The title of the pane')
               .having(text=RichTextValue('The text of the pane'))
               .with_dummy_image()
               .within(container))

        browser.login().visit(container, view='@@block_view')
        self.assertEqual(
            ['The text of the pane'],
            browser.css('.sliderPane').text
        )

    @browsing
    def test_slider_pane_with_title_but_without_text(self, browser):
        """
        This test makes sure that a slider pane configured to show the title but
        without text will really render the title.
        """
        page = create(Builder('sl content page'))
        container = create(Builder('sliderblock')
                           .titled(u'Title of the slider block')
                           .within(page))
        create(Builder('slider pane')
               .titled(u'The title of the pane')
               .having(show_title=True)
               .with_dummy_image()
               .within(container))

        browser.login().visit(container, view='@@block_view')
        self.assertEqual(
            ['The title of the pane'],
            browser.css('.sliderPane').text
        )

    @browsing
    def test_slider_pane_with_title_and_with_text(self, browser):
        """
        This test makes sure that a slider pane configured to show the title
        and having some text will render both the title and the text.
        """
        page = create(Builder('sl content page'))
        container = create(Builder('sliderblock')
                           .titled(u'Title of the slider block')
                           .within(page))
        create(Builder('slider pane')
               .titled(u'The title of the pane')
               .having(text=RichTextValue('The text of the pane'))
               .having(show_title=True)
               .with_dummy_image()
               .within(container))

        browser.login().visit(container, view='@@block_view')
        self.assertEqual(
            ['The title of the pane The text of the pane'],
            browser.css('.sliderPane').text
        )

    def set_image_limit_config(self, config):
        api.portal.set_registry_record(
            'image_limits', config, ISimplelayoutDefaultSettings)

        transaction.commit()

    @browsing
    def test_show_soft_limit_indicator_if_soft_limit_is_not_satisfied(self, browser):
        container = create(Builder('sliderblock'))
        pane = create(Builder('slider pane').with_dummy_image().within(container))

        browser.login().visit(container, view='@@block_view')
        self.assertEquals(0, len(browser.css('.sliderPane .softLimitIndicator')))

        self.set_image_limit_config({
            pane.portal_type: [
                u'soft: width={}'.format(pane.image._width + 100)
            ]}
        )

        browser.login().visit(container, view='@@block_view')
        self.assertEquals(1, len(browser.css('.sliderPane .softLimitIndicator')))

    @browsing
    def test_show_hard_limit_indicator_if_hard_limit_is_not_satisfied(self, browser):
        container = create(Builder('sliderblock'))
        pane = create(Builder('slider pane').with_dummy_image().within(container))

        browser.login().visit(container, view='@@block_view')
        self.assertEquals(0, len(browser.css('.sliderPane .hardLimitIndicator')))

        self.set_image_limit_config({
            pane.portal_type: [
                u'hard: width={}'.format(pane.image._width + 100)
            ]}
        )

        browser.login().visit(container, view='@@block_view')
        self.assertEquals(1, len(browser.css('.sliderPane .hardLimitIndicator')))

    @browsing
    def test_show_only_hard_limit_indicator_if_hard_and_soft_limit_are_not_satisfied(self, browser):
        container = create(Builder('sliderblock'))
        pane = create(Builder('slider pane').with_dummy_image().within(container))

        browser.login().visit(container, view='@@block_view')
        self.assertEquals(0, len(browser.css('.sliderPane .limitIndicator')))

        self.set_image_limit_config({
            pane.portal_type: [
                u'soft: width={}'.format(pane.image._width + 100),
                u'hard: width={}'.format(pane.image._width + 200)
            ]}
        )

        browser.login().visit(container, view='@@block_view')
        self.assertEquals(1, len(browser.css('.sliderPane .limitIndicator')))
        self.assertEquals(1, len(browser.css('.sliderPane .hardLimitIndicator')))

    @browsing
    def test_do_not_show_limit_indicator_if_all_limits_are_satisfied(self, browser):
        container = create(Builder('sliderblock'))
        pane = create(Builder('slider pane').with_dummy_image().within(container))

        browser.login().visit(container, view='@@block_view')

        self.assertEquals(0, len(browser.css('.sliderPane .limitIndicator')))

        self.set_image_limit_config({
            pane.portal_type: [
                u'soft: width={}'.format(pane.image._width - 100),
                u'hard: width={}'.format(pane.image._width - 200)
            ]}
        )

        browser.visit(container)
        self.assertEquals(0, len(browser.css('.sliderPane .limitIndicator')))

    @browsing
    def test_only_show_limit_indicator_for_editors(self, browser):
        container = create(Builder('sliderblock'))
        pane = create(Builder('slider pane').with_dummy_image().within(container))

        self.set_image_limit_config({
            pane.portal_type: [
                u'soft: width={}'.format(pane.image._width + 100),
            ]}
        )

        browser.login().visit(container, view='@@block_view')
        self.assertEquals(1, len(browser.css('.limitIndicator')))

        browser.logout().visit(container, view='@@block_view')
        self.assertEquals(0, len(browser.css('.sliderPane .limitIndicator')))

    @browsing
    def test_raise_invalid_on_form_validation_if_hard_limit_is_not_satisfied(self, browser):
        container = create(Builder('sliderblock'))

        pane = create(Builder('slider pane')
                      .titled('Pane')
                      .with_dummy_image()
                      .within(container))

        self.set_image_limit_config({
            pane.portal_type: [
                u'hard: width={}'.format(pane.image._width + 100)
            ]}
        )

        browser.login().visit(pane, view="edit")
        browser.find_button_by_label('Save').click()

        self.assertEqual(
            [["The image doesn't fit the required dimensions of width: 101px (current: 1px)"]],
            erroneous_fields().values())

    @browsing
    def test_display_corpped_image_if_available(self, browser):
        container = create(Builder('sliderblock'))
        pane = create(Builder('slider pane')
                      .titled('Pane')
                      .with_dummy_image()
                      .within(container))

        pane.cropped_image = pane.image

        block_view = container.restrictedTraverse('block_view')
        browser.open_html(block_view())

        url = browser.css('.sliderImage img').first.get('src')

        pane.cropped_image = None

        browser.open_html(block_view())
        self.assertNotEqual(browser.css('.sliderImage img').first.get('src'), url)
