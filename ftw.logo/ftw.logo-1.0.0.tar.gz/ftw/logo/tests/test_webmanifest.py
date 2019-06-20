from ftw.logo.tests import FunctionalTestCase
from ftw.testbrowser import browsing


class TestWebmanifestView(FunctionalTestCase):

    @browsing
    def test_webmanifest_view(self, browser):
        browser.login().visit(self.portal, view='manifest.json')
        self.assertEqual('application/json', browser.mimetype)
        self.assertEqual({
            "theme_color": "#ffffff",
            "name": "logo",
            "short_name": "logo",
            "icons": [
                {
                    "src": "http://nohost/plone/@@logo/icon/ANDROID_192X192",
                    "type": "image/png",
                    "sizes": "192x192"
                },
                {
                    "src": "http://nohost/plone/@@logo/icon/ANDROID_512X512",
                    "type": "image/png",
                    "sizes": "512x512"
                }
            ],
            "background_color": "#ffffff",
            "display": "standalone"
        }, browser.json)
