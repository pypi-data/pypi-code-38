from ftw.mobile.interfaces import IMobileButton
from ftw.mobile.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from plone import api
from zope.component import getMultiAdapter
import json
import transaction


class TestUserButton(FunctionalTestCase):

    def setUp(self):
        super(TestUserButton, self).setUp()

        self.user_button = getMultiAdapter((self.portal, self.request),
                                           IMobileButton,
                                           name="user-mobile-button")

    def test_user_button_label(self):
        self.assertEquals('User menu', self.user_button.label())

    def test_user_button_data_template(self):
        self.assertEquals('ftw-mobile-list-template',
                          self.user_button.data_template())

    def test_user_button_position(self):
        self.assertEquals(1000, self.user_button.position())

    def test_user_button_data(self):
        expect = [
            {u'url': u'http://nohost/plone/dashboard',
             u'label': u'Dashboard'},
            {u'url': u'http://nohost/plone/@@personal-preferences',
             u'label': u'Preferences'},
            {u'url': u'http://nohost/plone/logout',
             u'label': u'Log out'}, ]
        self.assertEquals(expect, (self.user_button.data()))

    @browsing
    def test_user_button_rendering(self, browser):
        html = self.user_button.render_button()
        browser.open_html(html)

        link = browser.css('a').first

        self.assertEquals(u'User menu', link.text)
        self.assertEquals(u'#', link.attrib['href'])
        self.assertEquals(u'', link.attrib['data-mobile_endpoint'])
        self.assertEquals(u'', link.attrib['data-mobile_startup_cachekey'])
        self.assertEquals(u'ftw-mobile-list-template',
                          link.attrib['data-mobile_template'])

        self.assertTrue(
            isinstance(json.loads(link.attrib['data-mobile_data']), list),
            'Expect valid json data in mobile-data')

    @browsing
    def test_user_button_labels_are_translated(self, browser):
        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage('de')
        transaction.commit()

        browser.login().open()
        link = browser.css('#user-mobile-button a').first
        data = link.attrib.get('data-mobile_data')
        self.assertEquals(
            [{u'url': u'http://nohost/plone/dashboard',
              u'label': u'Pers\xf6nliche Seite'},
             {u'url': u'http://nohost/plone/@@personal-preferences',
              u'label': u'Meine Einstellungen'},
             {u'url': u'http://nohost/plone/logout',
              u'label': u'Abmelden'},
            ],
            json.loads(data))
