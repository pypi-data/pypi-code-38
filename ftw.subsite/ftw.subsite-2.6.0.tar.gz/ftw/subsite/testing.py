from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from ftw.testing import IS_PLONE_5
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import TEST_USER_ID, setRoles
from plone.app.testing import TEST_USER_NAME
from plone.testing import z2
from zope.configuration import xmlconfig
import ftw.subsite.tests.builders  # noqa


class FtwSubsiteIntegrationLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '</configure>',
            context=configurationContext)

        # Load ZCML
        import ftw.subsite
        xmlconfig.file('configure.zcml', ftw.subsite,
                       context=configurationContext)

        xmlconfig.file('overrides.zcml', ftw.subsite,
                       context=configurationContext)

        # import plone.app.portlets
        # xmlconfig.file('configure.zcml', plone.app.portlets,
        #                context=configurationContext)

        # import collective.MockMailHost
        # xmlconfig.file('configure.zcml', collective.MockMailHost,
        #                context=configurationContext)

        # installProduct() is *only* necessary for packages outside
        # the Products.* namespace which are also declared as Zope 2 products,
        # using <five:registerPackage /> in ZCML.
        z2.installProduct(app, 'plone.app.portlets')
        z2.installProduct(app, 'ftw.subsite')
        z2.installProduct(app, 'ftw.simplelayout')
        z2.installProduct(app, 'collective.MockMailHost')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'ftw.subsite:default')
        applyProfile(portal, 'collective.MockMailHost:default')
        if IS_PLONE_5:
            applyProfile(portal, 'plone.app.contenttypes:default')
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)


class FtwSubsiteWithoutApplyProfileLayer(FtwSubsiteIntegrationLayer):
    """Special layer, which does not install the ftw.subsite profile.
    This way the ftw.subsite browserlay will net be installed
    """

    def setUpPloneSite(self, portal):

        if IS_PLONE_5:
            applyProfile(portal, 'plone.app.contenttypes:default')
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)


FTW_SUBSITE_FIXTURE = FtwSubsiteIntegrationLayer()
FTW_SUBSITE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(FTW_SUBSITE_FIXTURE,), name="FtwSubsite:Integration")
FTW_SUBSITE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FTW_SUBSITE_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="FtwSubsite:Functional")

FTW_SUBSITE_SPECIAL_FIXTURE = FtwSubsiteWithoutApplyProfileLayer()
FTW_SUBSITE_SPECIAL_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FTW_SUBSITE_SPECIAL_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="FtwSubsite:SpecialFunctional")
