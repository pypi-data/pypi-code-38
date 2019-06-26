from zope.component import getUtility
from zope.publisher.browser import BrowserView
from plone.portlets.interfaces import IPortletManager
from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName

class SubsiteView(BrowserView):

    @memoize
    def empty(self):
        dashboards = [getUtility(IPortletManager, name=name) for name in
                        ['ftw.subsite.front1',
                         'ftw.subsite.front2',
                         'ftw.subsite.front3',
                         'ftw.subsite.front4',
                         'ftw.subsite.front5',
                         'ftw.subsite.front6',
                         'ftw.subsite.front7']]

        num_portlets = 0
        for dashboard in dashboards:
            num_portlets += len(dashboard)
        return num_portlets == 0

    def is_anon(self):
        member_tool = getToolByName(self, 'portal_membership')
        isAnon = member_tool.isAnonymousUser()
        return isAnon
