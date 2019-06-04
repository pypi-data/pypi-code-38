import copy
from ftw.mobile.interfaces import IMobileButton
from ftw.mobile.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from plone.app.multilingual.browser.setup import SetupMultilingualSite
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
import json
import transaction


class TestMultilingualButton(FunctionalTestCase):

    supported_languages = ['de', 'fr', 'en']

    def setUp(self):
        super(TestMultilingualButton, self).setUp()
        self.grant('Manager')

        self.language_tool = getToolByName(self.portal, 'portal_languages')
        for lang in self.supported_languages:
            self.language_tool.addSupportedLanguage(lang)

        pam_setup_tool = SetupMultilingualSite()
        pam_setup_tool.setupSite(self.portal)

        self._set_lang('de')
        self.button = getMultiAdapter(
            (self.portal, self.request),
            IMobileButton,
            name='multilanguage-mobile-button'
        )

    def _set_lang(self, lang='de'):
        self.language_tool.manage_setLanguageSettings(
            lang, self.supported_languages,
            setUseCombinedLanguageCodes=False)
        transaction.commit()

    def test_label(self):
        self.assertEquals(u'de', self.button.label())

    def test_data_template(self):
        self.assertEquals('ftw-mobile-list-template',
                          self.button.data_template())

    def test_position(self):
        self.assertEquals(300, self.button.position())

    def test_data(self):
        self.assertEquals(
            [
                {
                    'label': u'Deutsch',
                    'url': u'http://nohost/plone/@@multilingual-selector/notg/de?set_language=de',
                },
                {
                    'label': u'Fran\xe7ais',
                    'url': u'http://nohost/plone/@@multilingual-selector/notg/fr?set_language=fr',
                },
                {
                    'label': u'English',
                    'url': u'http://nohost/plone/@@multilingual-selector/notg/en?set_language=en',
                }
            ],
            self.button.data()
        )

    @browsing
    def test_rendering(self, browser):
        html = self.button.render_button()
        browser.open_html(html)

        link = browser.css('a').first

        self.assertEquals(u'de', link.text)
        self.assertEquals(u'#', link.attrib['href'])
        self.assertEquals(u'', link.attrib['data-mobile_endpoint'])
        self.assertEquals(u'', link.attrib['data-mobile_startup_cachekey'])
        self.assertEquals(u'ftw-mobile-list-template',
                          link.attrib['data-mobile_template'])

        self.assertTrue(
            isinstance(json.loads(link.attrib['data-mobile_data']), list),
            'Expect valid json data in mobile-data')

    def test_button_is_not_available(self):
        # The button must be here because of the 3 configured languages.
        self.assertEqual(
            True,
            self.button.available()
        )

        # Remove languages, keep only "de".
        langs = copy.deepcopy(self.supported_languages)
        langs.remove('de')
        self.language_tool.removeSupportedLanguages(langs)
        self.assertEqual(
            ['de'],
            self.language_tool.getSupportedLanguages()
        )

        # Make sure the button is no longer available.
        button = getMultiAdapter(
            (self.portal, self.request),
            IMobileButton,
            name='multilanguage-mobile-button'
        )
        self.assertEqual(
            False,
            button.available()
        )
