from plone.app.layout.viewlets.common import ViewletBase
from zope.component import getMultiAdapter
from plone.app.caching.interfaces import IETagValue


class LogoBaseViewlet(ViewletBase):

    def get_etag_value(self):
        navigation_root = self.portal_state.navigation_root()
        adapter = getMultiAdapter((navigation_root, self.request),
                                  IETagValue,
                                  name='logo-viewlet')
        return adapter()

    def update(self):
        super(LogoBaseViewlet, self).update()
        self.cachekey = self.get_etag_value()
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.navigation_root_url = self.portal_state.navigation_root_url()
