from ftw.builder import Builder
from ftw.builder import create
from ftw.slider.testing import SLIDER_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from unittest2 import TestCase


class TestSliderPaneView(TestCase):

    layer = SLIDER_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Contributor', 'Manager'])
        login(self.portal, TEST_USER_NAME)

        self.folder = create(Builder('folder')
                             .titled(u'Folder'))

        self.container = create(Builder('slider container')
                                .within(self.folder)
                                .titled(u'Slider Container'))

    @browsing
    def test_do_not_redirect_if_there_is_no_link(self, browser):
        pane = create(Builder('slider pane')
                      .within(self.container)
                      .titled(u'Pane 1')
                      .with_dummy_image())

        browser.login().visit(pane)
        self.assertEquals(pane.absolute_url(), browser.url)

    @browsing
    def test_do_not_redirect_external_url_if_user_can_edit(self, browser):
        pane = create(Builder('slider pane')
                      .within(self.container)
                      .titled(u'Pane 1')
                      .having(external_url=self.portal.absolute_url())
                      .with_dummy_image())

        browser.login().visit(pane)
        self.assertEquals(pane.absolute_url(), browser.url)

    @browsing
    def test_do_not_redirect_internal_url_if_user_can_edit(self, browser):
        target = create(Builder('folder')
                        .titled(u'Target folder'))

        portal_path = '/'.join(self.portal.getPhysicalPath())
        pane = create(Builder('slider pane')
                      .within(self.container)
                      .titled(u'Pane 1')
                      .having(link='/'.join(target.getPhysicalPath())[len(portal_path):])
                      .with_dummy_image())

        browser.login().visit(pane)
        self.assertEquals(pane.absolute_url(), browser.url)

    @browsing
    def test_redirect_internal_url_if_user_cannot_edit(self, browser):
        target = create(Builder('folder')
                        .titled(u'Target folder'))

        portal_path = '/'.join(self.portal.getPhysicalPath())
        pane = create(Builder('slider pane')
                      .within(self.container)
                      .titled(u'Pane 1')
                      .having(link='/'.join(target.getPhysicalPath())[len(portal_path):])
                      .with_dummy_image())

        browser.visit(pane)
        self.assertEquals(target.absolute_url(), browser.url)

    @browsing
    def test_redirect_external_url_if_user_cannot_edit(self, browser):
        pane = create(Builder('slider pane')
                      .within(self.container)
                      .titled(u'Pane 1')
                      .having(external_url=self.portal.absolute_url())
                      .with_dummy_image())

        browser.visit(pane)
        self.assertEquals(self.portal.absolute_url(), browser.url)

    @browsing
    def test_internal_url_on_slider_view(self, browser):
        target = create(Builder('folder')
                        .titled(u'Target folder'))

        portal_path = '/'.join(self.portal.getPhysicalPath())
        create(Builder('slider pane')
               .within(self.container)
               .titled(u'Pane 1')
               .having(link='/'.join(target.getPhysicalPath())[len(portal_path):])
               .with_dummy_image())

        # The internal links of the panes in the slider view must be of the form
        # "http://nohost/plone/target-folder" and not only "/target-folder" in order
        # for the links to work on localhost too.
        browser.login().visit(self.container, view='slider_view')
        self.assertEqual(
            ['http://nohost/plone/target-folder'],
            [link.attrib['href'] for link in browser.css('.sliderPane a')]
        )
