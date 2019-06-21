from copy import deepcopy
from ftw.logo import converter
from ftw.logo.testing import get_etag_value_for
from ftw.logo.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from wand.exceptions import CorruptImageError
from wand.image import Image
from zope.interface import Interface
import os


source_path = os.path.join(os.path.dirname(__file__), 'fixtures')
custom = os.path.join(source_path, 'custom.svg')
png = os.path.join(source_path, 'green.png')
logo = os.path.join(source_path, 'logo.png')


class IDummyLayer(Interface):
    pass


class TestLogoView(FunctionalTestCase):

    def setUp(self):
        super(TestLogoView, self).setUp()

        # Isolate changes on SCALES
        self.origin_scales = deepcopy(converter.SCALES)

    def tearDown(self):
        super(TestLogoView, self).tearDown()
        converter.SCALES = self.origin_scales

    def verify_image_format(self, browser, view, expected_format):
        browser.visit(self.portal, view=view)
        self.assertEqual(200, browser.status_code)
        try:
            im = Image(blob=browser.contents, format=expected_format)
        except CorruptImageError:    # pragma: no cover
            self.fail("Image is incorrect format - expected {}".format(expected_format))
        return im

    @browsing
    def test_logo_view(self, browser):
        self.verify_image_format(browser, '@@logo/logo/BASE', 'svg')

    @browsing
    def test_icon_view(self, browser):
        self.verify_image_format(browser, '@@logo/icon/BASE', 'svg')

    @browsing
    def test_logo_scale(self, browser):
        im = self.verify_image_format(browser, '@@logo/logo/MOBILE_LOGO', 'png')
        self.assertEqual(50, im.height)

    @browsing
    def test_icon_scale(self, browser):
        im = self.verify_image_format(browser, '@@logo/icon/ANDROID_192X192', 'png')
        self.assertEqual(192, im.height)
        self.assertEqual(192, im.width)

    @browsing
    def test_not_found(self, browser):
        with browser.expect_http_error(code=404):
            browser.login().visit(self.portal, view='@@logo/logo/not_found')

        with browser.expect_http_error(code=404):
            browser.login().visit(self.portal, view='@@logo/not_found')

    def test_etag_value_invalidates(self):
        before = get_etag_value_for(self.portal, self.request)
        self.layer['load_zcml_string']('''
        <configure
            xmlns:logo="https://namespaces.4teamwork.ch/ftw.logo"
            i18n_domain="my.package"
            package="ftw.logo.tests">
            <logo:logo base="{}" />
        </configure>
        '''.format(custom))
        after = get_etag_value_for(self.portal, self.request)

        self.assertNotEqual(
            before,
            after)

    @browsing
    def test_special_get_logo_scale_name_returns_svg_by_default(self, browser):
        self.verify_image_format(browser, '@@logo/logo/get_logo', 'svg')
        self.grant('Site Administrator')
        browser.login().visit(self.portal, view='@@logo-and-icon-overrides')

        with open(png) as green_png:
            browser.fill({'Standard (desktop) logo (PNG)': green_png}).submit()
            self.verify_image_format(browser, '@@logo/logo/get_logo', 'png')

    @browsing
    def test_special_get_logo_scale_name_returns_uploaded_png(self, browser):
        self.verify_image_format(browser, '@@logo/logo/get_logo', 'svg')
        self.grant('Site Administrator')
        browser.login().visit(self.portal, view='@@logo-and-icon-overrides')

        with open(png) as green_png:
            browser.fill({'Standard (desktop) logo (PNG)': green_png}).submit()
            self.verify_image_format(browser, '@@logo/logo/get_logo', 'png')

    @browsing
    def test_special_get_logo_scale_name_returns_uploaded_svg(self, browser):
        self.verify_image_format(browser, '@@logo/logo/get_logo', 'svg')
        self.grant('Site Administrator')
        browser.login().visit(self.portal, view='@@logo-and-icon-overrides')

        with open(png) as green_png:
            browser.fill({'Standard (desktop) logo (PNG)': green_png}).submit()
            self.verify_image_format(browser, '@@logo/logo/get_logo', 'png')

    def test_primary_logo_scale(self):
        self.layer['load_zcml_string']('''
        <configure
            xmlns:logo="https://namespaces.4teamwork.ch/ftw.logo"
            i18n_domain="my.package"
            package="ftw.logo.tests">
            <logo:logo base="{}" primary_logo_scale="logo" />
        </configure>
        '''.format(custom))

        # Simulate publishTraverse of '@@logo/logo/get_logo'
        view = self.portal.restrictedTraverse('@@logo')
        view.publishTraverse(view.request, u"logo")
        view.publishTraverse(view.request, u"get_logo")
        view()
        self.assertEquals('LOGO', view.scale)

    def test_change_logo_height(self):
        self.layer['load_zcml_string']('''
        <configure
            xmlns:logo="https://namespaces.4teamwork.ch/ftw.logo"
            i18n_domain="my.package"
            package="ftw.logo.tests">
            <logo:logo base="{}" height="100" mobile_height="30" />
        </configure>
        '''.format(custom))

        # Simulate publishTraverse of '@@logo/logo/get_logo'
        view = self.portal.restrictedTraverse('@@logo')
        view.publishTraverse(view.request, u"logo")
        view.publishTraverse(view.request, u"LOGO")
        img = Image(blob=view())
        self.assertEquals(100, img.width)

        # Simulate publishTraverse of '@@logo/logo/get_logo'
        view = self.portal.restrictedTraverse('@@logo')
        view.publishTraverse(view.request, u"logo")
        view.publishTraverse(view.request, u"MOBILE_LOGO")
        img = Image(blob=view())
        self.assertEquals(30, img.width)
