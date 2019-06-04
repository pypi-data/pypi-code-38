from ftw.mobile.buttons import BaseButton
from ftw.mobile.interfaces import IMobileButton
from plone import api
from plone.app.multilingual.browser.selector import LanguageSelectorViewlet
from zope.interface import implementsOnly


class MultilanguageButton(BaseButton, LanguageSelectorViewlet):

    implementsOnly(IMobileButton)

    def __init__(self, context, request):
        super(MultilanguageButton, self).__init__(context, request)
        self.tool = api.portal.get_tool('portal_languages')
        self.buttons = self.get_buttons()

    def available(self):
        """
        Only render the button if there is more than one language configured
        in Plone because it does not make sense to render the button if
        the user has no other language to switch to.
        """
        return len(self.buttons) > 1

    def data(self):
        return self.buttons

    def label(self):
        return api.portal.get_current_language()

    def position(self):
        return 300

    def get_buttons(self):
        translation_languages = self.languages()
        return [
            dict(url=language['url'], label=language['native'])
            for language in translation_languages
        ]
