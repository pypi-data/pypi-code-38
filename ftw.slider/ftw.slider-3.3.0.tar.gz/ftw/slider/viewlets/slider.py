from Acquisition import aq_parent, aq_inner
from ftw.slider.interfaces import SLIDER_VIEW
from plone.app.layout.viewlets import ViewletBase
from zope.component import getMultiAdapter


class SliderViewlet(ViewletBase):

    def render(self):
        context = self.context

        plone = getMultiAdapter((self.context, self.request), name="plone")
        if plone.isDefaultPageInFolder():
            context = aq_parent(aq_inner(self.context))

        containers = context.getFolderContents(
            contentFilter={'portal_type': 'ftw.slider.Container'},
            full_objects=True)
        self.container = len(containers) > 0 and containers[0] or None
        if self.container:
            view = self.container.restrictedTraverse(SLIDER_VIEW, None)
            if view:
                return view()
        return ''
