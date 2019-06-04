from ftw.mobile.buttons import BaseButton
from ftw.mobile.interfaces import IMobileButton
from ftw.mobile.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from zope.component import getGlobalSiteManager
from zope.component import provideAdapter
from zope.interface import Interface
import transaction


class TestUserButton(FunctionalTestCase):

    def setUp(self):
        super(TestUserButton, self).setUp()
        self.buttonklass = None

    @browsing
    def test_viewlet_is_available(self, browser):
        browser.login().visit()

        self.assertTrue(browser.css('#ftw-mobile-menu-buttons'),
                        'Expect the ftw mobile viewlet on the site.')

    @browsing
    def test_default_buttons(self, browser):
        browser.login().visit()
        self.assertEquals(['Mobile navigation', 'User menu'],
                          browser.css('#ftw-mobile-menu-buttons a').text)

    @browsing
    def test_buttons_at_the_end(self, browser):

        self.register_button('somebutton', position=100000)

        try:
            browser.login().visit()
            self.assertEquals(['Mobile navigation', 'User menu', 'somebutton'],
                              browser.css('#ftw-mobile-menu-buttons a').text)
        finally:
            self.unregister_button('somebutton')

    @browsing
    def test_buttons_at_the_beginning(self, browser):

        self.register_button('somebutton', position=1)

        try:
            browser.login().visit()
            self.assertEquals(['somebutton', 'Mobile navigation', 'User menu'],
                              browser.css('#ftw-mobile-menu-buttons a').text)
        finally:
            self.unregister_button('somebutton')

    @browsing
    def test_buttons_in_the_middle(self, browser):

        self.register_button('somebutton', position=500)

        try:
            browser.login().visit()
            self.assertEquals(['Mobile navigation', 'somebutton', 'User menu'],
                              browser.css('#ftw-mobile-menu-buttons a').text)
        finally:
            self.unregister_button('somebutton')

    @browsing
    def test_button_with_empty_json_result_is_filtered(self, browser):

        self.register_button('somebutton', position=500, data=[])

        try:
            browser.login().visit()
            self.assertEquals(['Mobile navigation', 'User menu'],
                              browser.css('#ftw-mobile-menu-buttons a').text)
        finally:
            self.unregister_button('somebutton')

    def register_button(self, name, position, data=None):

        if data is None:
            data = [{'label': 'dummy', 'url': 'http://url.com'}]

        class SomeButton(BaseButton):
            def label(self):
                return name

            def position(self):
                return position

            def data(self):
                return data

        self.buttonklass = SomeButton

        provideAdapter(SomeButton,
                       adapts=(Interface, Interface),
                       name=name)
        transaction.commit()

    def unregister_button(self, name):

        sm = getGlobalSiteManager()
        sm.unregisterAdapter(self.buttonklass,
                             required=(Interface, Interface),
                             provided=IMobileButton,
                             name=name)
        transaction.commit()
