from ftw.subsite.interfaces import ILanguages
from plone.app.layout.viewlets import common
from zope.component import getMultiAdapter
from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from zope.publisher.browser import BrowserView


class Languages(BrowserView):

    def available(self):
        langs = getMultiAdapter((self.context, self.request), ILanguages)
        return bool(langs.get_related_languages())

    def current(self):
        langs = getMultiAdapter((self.context, self.request), ILanguages)
        return langs.get_current_language()


    def languages(self):
        langs = getMultiAdapter((self.context, self.request), ILanguages)
        return langs.get_related_languages()


class LanguageSelector(common.ViewletBase, Languages):
    implements(IViewlet)
