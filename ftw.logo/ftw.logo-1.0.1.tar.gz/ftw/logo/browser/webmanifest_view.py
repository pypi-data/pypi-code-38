from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
import json


class WebmanifestView(BrowserView):

    def __call__(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        navigation_root_url = portal_state.navigation_root_url()
        response = self.request.response
        response.setHeader('Content-Type', 'application/json')

        return json.dumps({
            'name': 'logo',
            'short_name': 'logo',
            'icons': [
                {
                    'src': '{}/@@logo/icon/ANDROID_192X192'
                    .format(navigation_root_url),
                    'sizes': '192x192',
                    'type': 'image/png'
                },
                {
                    'src': '{}/@@logo/icon/ANDROID_512X512'
                    .format(navigation_root_url),
                    'sizes': '512x512',
                    'type': 'image/png'
                }
            ],
            'theme_color': '#ffffff',
            'background_color': '#ffffff',
            'display': 'standalone'
        })
