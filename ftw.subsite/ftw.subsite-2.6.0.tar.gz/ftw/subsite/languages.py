from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from ftw.subsite.interfaces import ILanguages
from ftw.subsite.interfaces import ISubsite
from zope.component import adapter
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.interface import implementer
from zope.interface import implements


def translate_language(context, language_code):
    ltool = getToolByName(context, 'portal_languages')
    info = ltool.getAvailableLanguageInformation().get(language_code, None)
    if info is not None:
        return info.get(u'native', None)
    return None


@implementer(ILanguages)
@adapter(Interface, Interface)
def inherit_languages(context, request):
    parent = aq_parent(aq_inner(context))
    return getMultiAdapter((parent, request), ILanguages)


class SubsiteLanguages(object):
    implements(ILanguages)
    adapts(ISubsite, Interface)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_current_language(self):
        language_code = self.context.force_language
        return {'url': self.context.absolute_url(),
                'title': translate_language(self.context, language_code),
                'code': language_code}

    def get_related_languages(self):
        results = []

        for relation in self.context.language_references:
            subsite = relation.to_object
            lang_code = subsite.force_language
            if not lang_code:
                continue

            results.append({
                'url': subsite.absolute_url(),
                'title': translate_language(self.context, lang_code),
                'code': lang_code})

        if self.context.link_site_in_languagechooser:
            portal_url = getToolByName(self.context, 'portal_url')
            ltool = getToolByName(self.context, 'portal_languages')
            lang_code = ltool.getDefaultLanguage()

            results.append({
                'url': portal_url(),
                'title': translate_language(self.context, lang_code),
                'code': lang_code})

        results.sort(key=lambda item: item.get('title'))
        return results


class PloneSiteLanguages(object):
    implements(ILanguages)
    adapts(IPloneSiteRoot, Interface)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_current_language(self):
        ltool = getToolByName(self.context, 'portal_languages')
        lang_code = ltool.getDefaultLanguage()
        return {'url': self.context.absolute_url(),
                'title': translate_language(self.context, lang_code),
                'code': lang_code}

    def get_related_languages(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        results = []

        for brain in catalog(object_provides=ISubsite.__identifier__):
            subsite = brain.getObject()
            if not subsite.link_site_in_languagechooser:
                continue

            lang_code = subsite.force_language
            if not lang_code:
                continue

            results.append({
                'url': subsite.absolute_url(),
                'title': translate_language(self.context, lang_code),
                'code': lang_code})

        results.sort(key=lambda item: item.get('title'))
        return results
