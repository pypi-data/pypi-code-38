from plone.app.layout.viewlets.common import ViewletBase
from plone.app.layout.navigation.root import getNavigationRoot
from ftw.subsite.interfaces import ISubsite
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class CSSViewlet(ViewletBase):

    template = ViewPageTemplateFile('cssviewlet.pt')

    def __init__(self, context, request, view, manager=None):
        super(CSSViewlet, self).__init__(context, request, view, manager)
        self.nav_root = None

    def render(self):
        self.nav_root = self.context.restrictedTraverse(
            getNavigationRoot(self.context), None)
        if ISubsite.providedBy(self.nav_root):
            return self.template()
        else:
            return ''

    def get_css(self):
        return self.nav_root.additional_css
