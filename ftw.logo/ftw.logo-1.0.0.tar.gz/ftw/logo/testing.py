from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from ftw.testing import IS_PLONE_5
from ftw.testing.layer import COMPONENT_REGISTRY_ISOLATION
from ftw.testing.layer import ComponentRegistryLayer
from plone.app.caching.interfaces import IETagValue
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.testing import z2
from zope.component import getMultiAdapter
from zope.configuration import xmlconfig
import os


source_path = os.path.join(os.path.dirname(__file__), 'tests', 'fixtures')
blue_svg = os.path.join(source_path, 'blue.svg')


class MetaZCMLLayer(ComponentRegistryLayer):

    def setUp(self):
        super(MetaZCMLLayer, self).setUp()
        import ftw.logo
        self.load_zcml_file('meta.zcml', ftw.logo)


META_ZCML = MetaZCMLLayer()


class LogoLayer(PloneSandboxLayer):
    defaultBases = (COMPONENT_REGISTRY_ISOLATION, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '</configure>',
            context=configurationContext)

        z2.installProduct(app, 'ftw.logo')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.logo:default')


LOGO_FIXTURE = LogoLayer()
LOGO_FUNCTIONAL = FunctionalTesting(
    bases=(LOGO_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="ftw.logo:functional")


class BlueBaseLogoLayer(PloneSandboxLayer):
    defaultBases = (COMPONENT_REGISTRY_ISOLATION, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            ('<configure xmlns="http://namespaces.zope.org/zope"'
             '    xmlns:logo="https://namespaces.4teamwork.ch/ftw.logo">'
             '  <include package="z3c.autoinclude" file="meta.zcml" />'
             '  <includePlugins package="plone" />'
             '  <includePluginsOverrides package="plone" />'
             '  <logo:logo base="{0}"/>'
             '  <logo:icon base="{0}"/>'
             '</configure>').format(blue_svg),
            context=configurationContext)

        z2.installProduct(app, 'ftw.logo')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.logo:default')

        if IS_PLONE_5:
            applyProfile(portal, 'plone.app.contenttypes:default')


BLUE_BASE_LOGO_FIXTURE = BlueBaseLogoLayer()
BLUE_BASE_LOGO_FUNCTIONAL = FunctionalTesting(
    bases=(BLUE_BASE_LOGO_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="ftw.logo:bluebasefunctional")


def get_etag_value_for(context, request):
    adapter = getMultiAdapter((context, request),
                              IETagValue,
                              name='logo-viewlet')
    return adapter()
