from ftw.builder import Builder
from ftw.builder import create
from ftw.slider.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import assert_message
from plone.app.textfield import RichTextValue


class TestSliderPane(FunctionalTestCase):

    def setUp(self):
        super(TestSliderPane, self).setUp()
        self.grant('Manager')

    @browsing
    def test_slider_pane_cannot_have_link_and_external_url(self, browser):
        """
        This test makes sure that the slider pane cannot have a link
        and an external url at the same time.
        """
        folder = create(Builder('folder').titled(u'Folder'))

        container = create(Builder('slider container')
                           .within(folder)
                           .titled(u'Slider Container'))

        pane = create(Builder('slider pane')
                      .within(container)
                      .titled(u'Pane 1')
                      .with_dummy_image())

        my_folder = create(Builder('folder').titled(u'My Folder'))

        browser.login().visit(pane)
        browser.find('Edit').click()
        browser.fill({
            'Link': my_folder,
            'External URL': 'http://4teamwork.ch',
        })
        browser.find_button_by_label('Save').click()

        assert_message('There were some errors.')

    @browsing
    def test_slider_pane_without_text_does_not_render_any_content(self, browser):
        """
        This test makes sure that a slider pane without text does not render any
        content (neither the title nor the text).
        """
        container = create(Builder('slider container')
                           .titled(u'Slider Container'))
        create(Builder('slider pane')
               .titled(u'The title of the pane')
               .with_dummy_image()
               .within(container))

        browser.visit(container, view='slider_view')
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
        container = create(Builder('slider container')
                           .titled(u'Slider Container'))
        create(Builder('slider pane')
               .titled(u'The title of the pane')
               .having(text=RichTextValue('The text of the pane'))
               .with_dummy_image()
               .within(container))

        browser.visit(container, view='slider_view')
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
        container = create(Builder('slider container')
                           .titled(u'Slider Container'))
        create(Builder('slider pane')
               .titled(u'The title of the pane')
               .having(show_title=True)
               .with_dummy_image()
               .within(container))

        browser.visit(container, view='slider_view')
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
        container = create(Builder('slider container')
                           .titled(u'Slider Container'))
        create(Builder('slider pane')
               .titled(u'The title of the pane')
               .having(text=RichTextValue('The text of the pane'))
               .having(show_title=True)
               .with_dummy_image()
               .within(container))

        browser.visit(container, view='slider_view')
        self.assertEqual(
            ['The title of the pane The text of the pane'],
            browser.css('.sliderPane').text
        )
