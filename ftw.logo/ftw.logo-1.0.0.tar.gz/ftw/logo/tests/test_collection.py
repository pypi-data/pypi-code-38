from unittest2 import TestCase
from ftw.logo.logoconfig import LogoConfig
from ftw.logo.logoconfig import IconConfig
import os


source = os.path.join(os.path.dirname(__file__), 'fixtures/logo.svg')
img_source = os.path.join(os.path.dirname(__file__), 'fixtures/logo.png')


class TestCollecter(TestCase):

    def assertImage(self, img, width, height, format=None):
        self.assertEqual(img['width'], width)
        self.assertEqual(img['height'], height)
        if format:
            self.assertEqual(img['format'].lower(), format.lower())

    def test_all_logos_are_collected(self):
        component = LogoConfig(base=source)

        self.assertEqual(len(component.scales), 3, 'Should store three scales')
        self.assertImage(component.get_scale('BASE'), 1, 1, 'svg')
        self.assertImage(component.get_scale('LOGO'), 80, 80, 'png')
        self.assertImage(component.get_scale('MOBILE_LOGO'), 50, 50, 'png')

    def test_all_icons_are_collected(self):
        component = IconConfig(base=source)

        self.assertEqual(len(component.scales), 8, 'Should store eight scales')
        self.assertImage(component.get_scale('BASE'), 1, 1, 'svg')
        self.assertImage(component.get_scale('APPLE_TOUCH_ICON'), 180, 180, 'png')
        self.assertImage(component.get_scale('FAVICON_32X32'), 32, 32, 'png')
        self.assertImage(component.get_scale('FAVICON_16X16'), 16, 16, 'png')
        self.assertImage(component.get_scale('MSTILE_150X150'), 150, 150, 'png')
        self.assertImage(component.get_scale('ANDROID_192X192'), 192, 192, 'png')
        self.assertImage(component.get_scale('ANDROID_512X512'), 512, 512, 'png')
        self.assertImage(component.get_scale('FAVICON'), 16, 16, 'ico')

    def test_add_specific_logo_as_config(self):
        component = LogoConfig(base=source, logo=img_source)

        self.assertEqual(len(component.scales), 3, 'Should store one scales')
        self.assertImage(component.get_scale('LOGO'), 762, 80, 'png')

        self.assertImage(component.get_scale('BASE'), 1, 1, 'svg')
        self.assertImage(component.get_scale('MOBILE_LOGO'), 50, 50, 'png')

    def test_primary_logo_scale(self):
        component = LogoConfig(base=source, logo=img_source,
                               primary_logo_scale='logo')
        self.assertEquals('logo', component.primary_logo_scale)
