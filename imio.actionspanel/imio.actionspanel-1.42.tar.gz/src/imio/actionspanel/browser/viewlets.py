from plone.app.layout.viewlets import ViewletBase
from zope.component import getMultiAdapter


class ActionsPanelViewlet(ViewletBase):
    '''This viewlet displays the available actions on the context.'''

    async = False

    def show(self):
        """Will we show the viewlet on context?"""
        context_state = getMultiAdapter(
            (self.context, self.request), name=u'plone_context_state')
        return context_state.is_view_template() and 'ajax_load' not in self.request

    def renderViewlet(self):
        """Render the view @@actions_panel that display relevant actions.
           Here we want to display elements with full space, so not as icons."""
        if self.show():
            return self.context.restrictedTraverse(
                "@@actions_panel")(useIcons=False)
