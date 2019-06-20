from Products.CMFCore.utils import getToolByName
from ftw.builder import Builder
from ftw.builder import create
from ftw.logo.manual_override import OVERRIDES_FIXED_ID
from ftw.logo.testing import BLUE_BASE_LOGO_FUNCTIONAL
from ftw.logo.testing import get_etag_value_for
from ftw.logo.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from wand.color import Color
from wand.exceptions import CorruptImageError
from wand.image import Image
from zope.annotation.interfaces import IAnnotations
import os


source_path = os.path.join(os.path.dirname(__file__), 'fixtures')
blue_svg = os.path.join(source_path, 'blue.svg')
red_svg = os.path.join(source_path, 'red.svg')
green_png = os.path.join(source_path, 'green.png')


def get_rgb(color):
    # Helper Function to get rgb and rgba for a color
    color_dict = {'red': 'rgb{}(255, 0, 0, 1)',
                  'green': 'rgb{}(0, 255, 0, 1)',
                  'blue': 'rgb{}(0, 0, 255, 1)'}

    return [color_dict[color].format(''), color_dict[color].format('a')]


class TestManualOverrides(FunctionalTestCase):
    layer = BLUE_BASE_LOGO_FUNCTIONAL

    @browsing
    def test_permission_for_overrides_form(self, browser):

        # test editor user can't use add form
        self.grant('Editor')
        with browser.expect_unauthorized():
            browser.login().visit(self.portal, view='@@logo-and-icon-overrides')

        # test site admin CAN use the overrides form
        self.grant('Site Administrator')
        browser.visit(self.portal, view='@@logo-and-icon-overrides')
        self.assertEqual(200, browser.status_code)

        # test editor user can't view the content type
        self.grant('Editor')
        with browser.expect_unauthorized():
            browser.login().visit(self.portal[OVERRIDES_FIXED_ID])

        # test editor user can't view the content type
        self.grant('Site Administrator')
        browser.login().visit(self.portal[OVERRIDES_FIXED_ID])
        self.assertEqual(200, browser.status_code)

    @browsing
    def test_addable_only_on_navroots(self, browser):
        self.grant('Site Administrator')
        browser.login()
        folder = create(Builder('folder'))
        with browser.expect_http_error(code=404):
            browser.login().visit(folder, view='@@logo-and-icon-overrides')

        # If we make the folder a navroot then we should be able to access the form on it
        # FIXME - 500 from ComponentLookupError in LogoViewletETagValue
        # alsoProvides(self.portal['folder'], INavigationRoot)
        # transaction.commit()
        # browser.visit(folder, view='@@logo-and-icon-overrides')
        # self.assertEqual(200, browser.status_code)

    def verify_correct_image(self, browser, view, expected_format, expected_color=None):
        """
        Verify that a logo/icon at a given view is as expected

        expected_format ('png', 'svg' etc.)
        expected_color - proves the *source* of the image by looking at the histogram
            - we use ZCML to set the base SVG image to 100% 'blue'
            - the TTW SVG (if set) is 100% 'red'
            - the TTW PNG (if set) is 100% GREEN ('#0f0')
        """
        # We logout to test images are *publicly* visible
        browser.logout()
        browser.visit(self.portal, view=view)
        self.assertEqual(200, browser.status_code)
        try:
            im = Image(blob=browser.contents, format=expected_format)
        except CorruptImageError:    # pragma: no cover
            self.fail("Image is incorrect format - expected {}".format(expected_format))
        if (expected_color):
            # Determine the source (SVG, PNG) by using the colour
            # Test that 90% of image is expected_color
            total_pixels = im.height * im.width
            im.alpha_channel = 'opaque'
            try:
                # I try rgb value as key otherwise rgba.
                value = (im.histogram.get(Color(get_rgb(expected_color)[0])) or
                         im.histogram.get(Color(get_rgb(expected_color)[1])))
                self.assertGreater(value, total_pixels * 0.9)
            except KeyError:    # pragma: no cover
                self.fail(("expected_color {} not found in image histogram\n"
                           "First 5 colours were: {}").format(Color(expected_color), im.histogram.keys()[:5]))
        return im

    @browsing
    def test_logo_overrides(self, browser):
        # We use primary colours to check the source of the scaled image

        self.grant('Site Administrator')
        browser.login().visit(self.portal, view='@@logo-and-icon-overrides')
        self.assertEqual(200, browser.status_code)
        with open(red_svg) as svg_file:
            browser.fill({'SVG base logo': svg_file}).submit()

        # Check SVG image is set
        self.verify_correct_image(browser, '@@logo/logo/BASE', 'svg',
                                  'red')
        # Check conversion to PNG
        img = self.verify_correct_image(browser, '@@logo/logo/MOBILE_LOGO',
                                        'png', 'red')
        self.assertEqual(50, img.height)
        # Check ZCML 'bypass' - base SVG should be shown
        img = self.verify_correct_image(browser, '@@logo/z/logo/MOBILE_LOGO',
                                        'png', 'blue')
        self.assertEqual(50, img.height)

        # verify icons are unaffected (i.e. still derive from base icon)
        self.verify_correct_image(browser, '@@logo/icon/BASE', 'svg',
                                  'blue')
        self.verify_correct_image(browser, '@@logo/icon/ANDROID_192X192',
                                  'png', 'blue')
        # Test PNG override
        # (Note: we don't test dimensions as they are not enforced)
        overrides = self.portal[OVERRIDES_FIXED_ID]
        browser.login().visit(overrides, view='@@edit')
        with open(green_png) as png_file:
            browser.fill({'Mobile logo (PNG)': png_file}).submit()

        self.verify_correct_image(browser, '@@logo/logo/MOBILE_LOGO', 'png',
                                  'green')

        # Check ZCML 'bypass' - a scale of the base SVG should be shown
        self.verify_correct_image(browser, '@@logo/z/logo/MOBILE_LOGO', 'png',
                                  'blue')

        # verify icons are unaffected (i.e. still derive from base icon)
        self.verify_correct_image(browser, '@@logo/icon/BASE', 'svg',
                                  'blue')
        self.verify_correct_image(browser, '@@logo/icon/ANDROID_192X192',
                                  'png', 'blue')

    @browsing
    def test_icon_overrides(self, browser):
        # We use primary colours to check the source of the scaled image

        self.grant('Site Administrator')
        browser.login().visit(self.portal, view='@@logo-and-icon-overrides')
        self.assertEqual(200, browser.status_code)
        with open(red_svg) as svg_file:
            browser.fill({'SVG base icon': svg_file}).submit()

        # Check SVG image is set
        self.verify_correct_image(browser, '@@logo/icon/BASE', 'svg',
                                  'red')
        # Check conversion to PNG
        img = self.verify_correct_image(browser, '@@logo/icon/FAVICON_32X32',
                                        'png', 'red')
        self.assertEqual(32, img.height)
        self.assertEqual(32, img.width)
        # Check ZCML 'bypass' - a scale of the base SVG should be shown
        img = self.verify_correct_image(browser, '@@logo/z/icon/FAVICON_32X32',
                                        'png', 'blue')
        self.assertEqual(32, img.height)
        self.assertEqual(32, img.width)

        # verify logos are unaffected (i.e. still derive from base logo)
        self.verify_correct_image(browser, '@@logo/logo/BASE', 'svg',
                                  'blue')
        self.verify_correct_image(browser, '@@logo/logo/LOGO', 'png',
                                  'blue')

        # Test PNG override (Note: we don't test dimensions as they are not enforced)
        overrides = self.portal[OVERRIDES_FIXED_ID]
        browser.login().visit(overrides, view='@@edit')
        with open(green_png) as png_file:
            browser.fill({'Favicon 32x32': png_file}).submit()
        self.verify_correct_image(browser, '@@logo/icon/FAVICON_32X32', 'png',
                                  'green')

        # Check ZCML 'bypass' - base SVG should be shown
        self.verify_correct_image(browser, '@@logo/z/icon/FAVICON_32X32',
                                  'png', 'blue')

        # verify logos are unaffected (i.e. still derive from base logo)
        self.verify_correct_image(browser, '@@logo/logo/BASE', 'svg',
                                  'blue')
        self.verify_correct_image(browser, '@@logo/logo/LOGO', 'png',
                                  'blue')

    @browsing
    def test_form_validation(self, browser):
        self.grant('Site Administrator')

        browser.login().visit(self.portal, view='@@logo-and-icon-overrides')
        with open(green_png) as png_file:
            browser.fill({'SVG base logo': png_file}).submit()
        self.assertIn('This image must be a SVG file (image/png supplied)', browser.contents)

        overrides = self.portal[OVERRIDES_FIXED_ID]
        browser.login().visit(overrides, view='@@edit')
        with open(red_svg) as svg_file:
            browser.fill({'Apple touch icon': svg_file}).submit()
        self.assertIn('This image must be a PNG file (image/svg+xml supplied)', browser.contents)

    @browsing
    def test_uninstall_removes_annotations_removed(self, browser):

        self.grant('Site Administrator')

        # add some overrides
        browser.login().visit(self.portal, view='@@logo-and-icon-overrides')
        with open(red_svg) as svg_file:
            browser.fill({'SVG base logo': svg_file,
                          'SVG base icon': svg_file}).submit()

        # Check we have some annotations
        override_obj = self.portal[OVERRIDES_FIXED_ID]
        annotations = IAnnotations(override_obj)
        self.assertGreater(len(annotations), 0, 'Sanity check annotations added')

        # Uninstall
        quick_installer_tool = getToolByName(self.layer['portal'],
                                             'portal_quickinstaller')
        quick_installer_tool.uninstallProducts(['ftw.logo'])

        # check all annotations are gone
        annotations = IAnnotations(override_obj)
        self.assertEqual(len(annotations), 0, 'Uninstallation should remove all annotations')

    def assertDistinctETags(self, etagList, extra_msg=''):
        if len(etagList) != len(set(etagList)):
            self.fail("ETag values are not distinct {} {}".format(etagList, extra_msg))

    @browsing
    def test_etag_for_overrides(self, browser):
        """
        Test that the etag changes for each change of configuration, so caching works
        """
        self.grant('Site Administrator')
        etagValues = []
        etagValues.append(get_etag_value_for(self.portal, self.request))
        browser.login().visit(self.portal, view='@@logo-and-icon-overrides')
        with open(red_svg) as svg_file:
            browser.fill({'SVG base icon': svg_file}).submit()

        etagValues.append(get_etag_value_for(self.portal, self.request))
        self.assertDistinctETags(etagValues, 'after overriding base SVG icon')

        overrides = self.portal[OVERRIDES_FIXED_ID]
        browser.login().visit(overrides, view='@@edit')
        with open(green_png) as png_file:
            browser.fill({'Favicon 32x32': png_file}).submit()

        etagValues.append(get_etag_value_for(self.portal, self.request))
        self.assertDistinctETags(etagValues, 'after overriding PNG icon')

        browser.login().visit(overrides, view='@@edit')
        with open(green_png) as png_file:
            browser.fill({'Android icon 512x512': png_file}).submit()

        etagValues.append(get_etag_value_for(self.portal, self.request))
        self.assertDistinctETags(etagValues, 'after overriding a second PNG icon')
