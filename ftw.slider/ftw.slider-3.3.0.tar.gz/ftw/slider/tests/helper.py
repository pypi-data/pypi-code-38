from ftw.testing import IS_PLONE_5
from plone import api
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import transaction


class LanguageToolHelper(object):
    def __init__(self):
        self.lang_tool = None

    def manage_set_language_settings(self,
                                     default='en',
                                     supported=None,
                                     use_combined=False,
                                     start_neutral=True,
                                     content_negotiation=True):
        """
        Sets language settings regardeless if plone4.3 or plone5.1
        :param default: default site language
        :param supported: list of supported languages
        :param use_combined: setUseCombinedLanguageCodes in Plone 4.x
        :param start_neutral: startNeutral in Plone 4.x
        :param content_negotiation: default is False
        """
        # startNeutral is not used/available in plone 5.1 anymore

        if not supported:
            supported = ['en']

        if IS_PLONE_5:
            from Products.CMFPlone.interfaces import ILanguageSchema

            self.lang_tool = api.portal.get_tool('portal_languages')
            self.lang_tool.setDefaultLanguage(default)
            for lang in supported:
                self.lang_tool.addSupportedLanguage(lang)
            self.lang_tool.settings.use_combined_language_codes = False
            self.lang_tool.setLanguageCookie()
            registry = getUtility(IRegistry)
            language_settings = registry.forInterface(ILanguageSchema,
                                                      prefix='plone')
            language_settings.use_content_negotiation = content_negotiation
            language_settings.default_language = default

        else:
            self.lang_tool = self.portal.portal_languages
            self.lang_tool.manage_setLanguageSettings(
                default,
                supported,
                setUseCombinedLanguageCodes=use_combined,
                # Set this only for better testing ability
                setCookieEverywhere=True,
                startNeutral=start_neutral,
                setContentN=True)
        transaction.commit()
