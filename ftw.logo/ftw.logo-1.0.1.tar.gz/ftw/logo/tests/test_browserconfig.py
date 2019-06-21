from ftw.logo.tests import FunctionalTestCase
from ftw.testbrowser import browsing


class TestBrowserconfigView(FunctionalTestCase):

    @browsing
    def test_browserconfig_view(self, browser):
        browser.login().visit(self.portal, view='browserconfig.xml')
        self.assertEqual('text/xml', browser.mimetype)
        self.assertMultiLineEqual(
            '<?xml version="1.0" encoding="utf-8"?>'
            '<browserconfig>'
            '<msapplication>'
            '<tile>'
            '<square150x150logo src="http://nohost/plone/@@logo/icon/MSTILE_150X150"/>'
            '<TileColor>#da532c</TileColor>'
            '</tile>'
            '</msapplication>'
            '</browserconfig>', browser.contents)
