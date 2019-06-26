from ftw.mobile.buttons import BaseButton
from ftw.subsite.interfaces import ILanguages
from zope.component import getMultiAdapter


class SubsiteLanguageButton(BaseButton):

    def label(self):
        langs = getMultiAdapter((self.context, self.request), ILanguages)
        return langs.get_current_language().get('code', None)

    def position(self):
        return 300

    def data(self):
        langs = getMultiAdapter((self.context, self.request), ILanguages)

        def link_data(item):
            return {'url': item.get('url'),
                    'label': item.get('title')}
        return map(link_data, langs.get_related_languages())

    def available(self):
        langs = getMultiAdapter((self.context, self.request), ILanguages)
        return bool(langs.get_related_languages())
