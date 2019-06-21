from ftw.logo.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from ftw.logo.testing import get_etag_value_for


class TestLogoViewlet(FunctionalTestCase):

    @browsing
    def test_logo_tag(self, browser):
        etag = get_etag_value_for(self.portal, self.request)
        browser.login().visit(self.portal)

        self.assertEqual(
            map(lambda x: x.attrib['href'], browser.css('#portal-logo')),
            ['http://nohost/plone'],
        )

        self.assertEqual(
            map(lambda x: x.attrib['src'], browser.css('#portal-logo > img')),
            ['http://nohost/plone/@@logo/logo/get_logo?r={}'.format(etag)],
        )

    @browsing
    def test_mobile_logo_tag(self, browser):
        etag = get_etag_value_for(self.portal, self.request)
        browser.login().visit(self.portal)

        self.assertEqual(
            map(lambda x: x.attrib['href'], browser.css('#portal-mobilelogo')),
            ['http://nohost/plone'],
        )

        self.assertEqual(
            map(lambda x: x.attrib['src'], browser.css('#portal-mobilelogo > img')),
            ['http://nohost/plone/@@logo/logo/MOBILE_LOGO?r={}'.format(etag)],
        )
