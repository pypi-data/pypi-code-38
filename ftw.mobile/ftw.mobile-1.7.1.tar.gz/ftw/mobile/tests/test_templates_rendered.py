from ftw.mobile.tests import FunctionalTestCase
from ftw.testbrowser import browsing


class TestHandlebarsTemplates(FunctionalTestCase):

    @browsing
    def test_list_template_is_available(self, browser):
        browser.login().visit()

        self.assertTrue(len(browser.css('#ftw-mobile-list-template')),
                        'Expect templates for lists in DOM.')

    @browsing
    def test_navigation_template_is_available(self, browser):
        browser.login().visit()

        self.assertTrue(len(browser.css('#ftw-mobile-navigation-template')),
                        'Expect templates for navigation in DOM.')
