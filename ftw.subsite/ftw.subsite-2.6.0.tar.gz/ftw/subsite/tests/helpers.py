from ftw.testing import IS_PLONE_5
from plone import api
from plone.registry.interfaces import IRegistry
from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
import transaction


def introduce_language_subsites(*subsites):
    intids = getUtility(IIntIds)

    for subsite in subsites:
        ids = [intids.getId(obj) for obj in subsites]
        ids.remove(intids.getId(subsite))
        subsite.language_references = [RelationValue(id_) for id_ in ids]

        transaction.commit()


class LanguageSetter(object):

    def set_language_settings(self, default='en', supported=None,
                              use_combined=False, start_neutral=True):
        """
        Sets language settings regardeless if plone4.3 or plone5.1
        :param default: default site language
        :param supported: list of supported languages
        """
        # startNeutral is not used/available in plone 5.1 anymore

        if not supported:
            supported = ['en']

        if IS_PLONE_5:
            from Products.CMFPlone.interfaces import ILanguageSchema

            self.ltool = api.portal.get_tool('portal_languages')
            self.ltool.setDefaultLanguage(default)
            for lang in supported:
                self.ltool.addSupportedLanguage(lang)
            self.ltool.settings.use_combined_language_codes = False
            self.ltool.setLanguageCookie()
            registry = getUtility(IRegistry)
            language_settings = registry.forInterface(ILanguageSchema, prefix='plone')
            language_settings.use_content_negotiation = True
        else:
            self.ltool = self.portal.portal_languages
            self.ltool.manage_setLanguageSettings(
                default,
                supported,
                setUseCombinedLanguageCodes=use_combined,
                # Set this only for better testing ability
                setCookieEverywhere=True,
                startNeutral=start_neutral,
                setContentN=True)
        transaction.commit()
