from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter


BROWSERCONFIG_TEMPLATE = '''
<?xml version="1.0" encoding="utf-8"?>
<browserconfig>
<msapplication>
<tile>
<square150x150logo src="{}/@@logo/icon/MSTILE_150X150"/>
<TileColor>#da532c</TileColor>
</tile>
</msapplication>
</browserconfig>
'''


class BrowserconfigView(BrowserView):

    def __call__(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        navigation_root_url = portal_state.navigation_root_url()
        response = self.request.response
        response.setHeader('Content-Type', 'text/xml')

        return BROWSERCONFIG_TEMPLATE.replace('\n', '').format(navigation_root_url)
