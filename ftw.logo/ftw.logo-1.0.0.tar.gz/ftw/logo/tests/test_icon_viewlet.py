from ftw.logo.testing import get_etag_value_for
from ftw.logo.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from ftw.testing import IS_PLONE_5
from unittest import skip
from unittest2 import skipIf


class TestIconViewlet(FunctionalTestCase):

    @skip("TODO: Remove defualt viewport from sunburst default template")
    @browsing
    def test_viewport_metatag(self, browser):
        browser.login().visit(self.portal)

        self.assertEqual(
            ['width=device-width, initial-scale=1'],
            map(lambda x: x.attrib['content'], browser.css(
                'meta[name="viewport"]'))
        )

    @skipIf(IS_PLONE_5, 'The apple touch logo is not configurable in plone5')
    @browsing
    def test_logo_viewlet_displays_relevant_metadata_in_header_part_one(self, browser):
        etag = get_etag_value_for(self.portal, self.request)
        browser.login().visit(self.portal)

        self.assertEqual(
            [{
                'href': 'http://nohost/plone/@@logo/icon/APPLE_TOUCH_ICON?r={}'.format(etag),
                'sizes': '180x180'}],
            map(lambda x: {
                'href': x.attrib['href'],
                'sizes': x.attrib['sizes'],
            }, browser.css('link[rel="apple-touch-icon"]'))
        )

    @browsing
    def test_logo_viewlet_displays_relevant_metadata_in_header_part_two(self, browser):
        etag = get_etag_value_for(self.portal, self.request)
        browser.login().visit(self.portal)

        self.assertEqual(
            [
                {
                    'type': 'image/png',
                    'sizes': '32x32',
                    'href': 'http://nohost/plone/@@logo/icon/FAVICON_32X32?r={}'.format(etag),
                },
                {
                    'type': 'image/png',
                    'sizes': '16x16',
                    'href': 'http://nohost/plone/@@logo/icon/FAVICON_16X16?r={}'.format(etag),
                },
                {
                    'type': '',
                    'sizes': '',
                    'href': 'http://nohost/plone/@@logo/icon/FAVICON?r={}'.format(etag),
                },
            ],
            map(lambda x: {
                'type': x.attrib.get('type', ''),
                'sizes': x.attrib.get('sizes', ''),
                'href': x.attrib['href'],
            }, browser.css('link[rel="icon"]'))
        )

        self.assertEqual(
            ['http://nohost/plone/manifest.json?r={}'.format(etag)],
            map(lambda x: x.attrib['href'], browser.css(
                'link[rel="manifest"]'))
        )

        self.assertEqual(
            ['http://nohost/plone/browserconfig.xml?r={}'.format(etag)],
            map(lambda x: x.attrib['content'], browser.css(
                'meta[name="msapplication-config"]'))
        )

        self.assertEqual(
            ['#ffffff'],
            map(lambda x: x.attrib['content'], browser.css(
                'meta[name="theme-color"]'))
        )
