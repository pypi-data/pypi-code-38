from ftw.logo.interfaces import IIconConfig
from ftw.logo.interfaces import ILogoConfig
from ftw.logo.testing import META_ZCML
from unittest2 import TestCase
from zope.component import getMultiAdapter
from zope.configuration.xmlconfig import ZopeXMLConfigurationError
from zope.interface import implementer
from zope.interface import Interface
from zope.interface.verify import verifyObject
import os


source_path = os.path.join(os.path.dirname(__file__), 'fixtures')
logo = os.path.join(source_path, 'logo.svg')
icon = os.path.join(source_path, 'logo.svg')
custom = os.path.join(source_path, 'custom.svg')

logo_img = os.path.join(source_path, 'logo.png')
mobile_img = os.path.join(source_path, 'mobile.png')


class IDummyLayer(Interface):
    pass


@implementer(IDummyLayer)
class DummyRequest(object):
    pass


class TestZCML(TestCase):
    layer = META_ZCML

    def test_logo_component(self):
        self.load_zcml('<logo:logo base="{}" />'.format(logo))
        registry = getMultiAdapter((None, None), ILogoConfig)
        verifyObject(ILogoConfig, registry)

    def test_logo_component_with_other_image_attr(self):
        self.load_zcml('<logo:logo base="{}" logo="{}" />'.format(logo, logo_img))
        registry = getMultiAdapter((None, None), ILogoConfig)
        verifyObject(ILogoConfig, registry)

        self.load_zcml('<logo:logo base="{}" mobile="{}" />'.format(logo, mobile_img))
        registry = getMultiAdapter((None, None), ILogoConfig)
        verifyObject(ILogoConfig, registry)

    def test_logo_component_is_overwriteable(self):
        self.load_zcml(
            '<logo:logo base="{}" />'.format(logo),
            '<logo:logo base="{}"'.format(custom),
            '  layer="ftw.logo.tests.test_zcml.IDummyLayer" />')
        registry = getMultiAdapter((object(), DummyRequest()), ILogoConfig)
        verifyObject(ILogoConfig, registry)

    def test_icon_component(self):
        self.load_zcml(
            '<logo:icon base="{}" />'.format(icon))
        registry = getMultiAdapter((None, None), IIconConfig)
        verifyObject(IIconConfig, registry)

    def test_icon_component_is_overwriteable(self):
        self.load_zcml(
            '<logo:icon base="{}" />'.format(icon),
            '<logo:icon base="{}"'.format(custom),
            '  layer="ftw.logo.tests.test_zcml.IDummyLayer" />')
        registry = getMultiAdapter((object(), DummyRequest()), IIconConfig)
        verifyObject(IIconConfig, registry)

    def load_zcml(self, *lines):
        self.layer.load_zcml_string('\n'.join((
            '<configure ',
            '    xmlns:logo="https://namespaces.4teamwork.ch/ftw.logo"',
            '    i18n_domain="my.package"',
            '    package="ftw.logo.tests">',
        ) + lines + (
            '</configure>',
        )))

    def test_fail_to_load_if_no_valid_attr_is_present(self):
        with self.assertRaises(ZopeXMLConfigurationError):
            self.load_zcml('<logo:logo />'.format(logo))

        with self.assertRaises(ZopeXMLConfigurationError):
            self.load_zcml('<logo:logo dummy="nothing" />'.format(logo))

        with self.assertRaises(ZopeXMLConfigurationError):
            self.load_zcml('<logo:icon />'.format(logo))

        with self.assertRaises(ZopeXMLConfigurationError):
            self.load_zcml('<logo:icon dummy="nothing" />'.format(logo))
