from ftw.mobile import _
from ftw.mobile.interfaces import IMobileButton
from plone import api
from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getAdapters
from zope.component import getMultiAdapter
from zope.i18n import translate
import json
import os


class MobileButtonViewlet(ViewletBase):

    template = ViewPageTemplateFile('templates/buttons_viewlet.pt')

    # Do not render handlebar template with PageTemplate engine,
    # There's actually nothing to process.
    with open(os.path.join(os.path.dirname(__file__),
                           'templates',
                           'list.html'), 'r') as html_file:
        handlebars_list_html = html_file.read()

    with open(os.path.join(os.path.dirname(__file__),
                           'templates',
                           'navigation.html'), 'r') as html_file:
        handlebars_navigation_html = html_file.read()

    def index(self):
        return self.template()

    def buttons(self):
        buttons = list(getAdapters((self.context, self.request),
                                   IMobileButton))

        buttons.sort(key=self.sort_buttons)

        for name, button in buttons:
            if button.available():
                yield {'html': button.render_button(),
                       'name': name}

    def sort_buttons(self, button):
        return button[1].position()

    def nav_root_url(self):
        return api.portal.get_navigation_root(self.context).absolute_url()

    def current_url(self):
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        return context_state.canonical_object().absolute_url()

    def translation_strings(self):

        return json.dumps(
            {'label_goto_parent': translate(_(u'label_goto_parent',
                                              default=u'Go to parent content of: '),
                                            context=self.request),
             'label_goto_children': translate(_(u'label_goto_children',
                                                default=u'Go to children of: '),
                                              context=self.request)})
