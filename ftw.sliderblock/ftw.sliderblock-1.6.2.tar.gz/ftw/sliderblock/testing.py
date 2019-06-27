from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from ftw.sliderblock.tests import builders
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2
from Testing.ZopeTestCase.utils import setupCoreSessions
from zope.configuration import xmlconfig


class FtwSliderblockLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '</configure>',
            context=configurationContext)
        setupCoreSessions(app)
        z2.installProduct(app, 'ftw.simplelayout')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'ftw.simplelayout.contenttypes:default')
        applyProfile(portal, 'ftw.sliderblock:default')


FTW_SLIDERBLOCK_FIXTURE = FtwSliderblockLayer()

FTW_SLIDERBLOCK_INTEGRATION_TESTING = IntegrationTesting(
    bases=(FTW_SLIDERBLOCK_FIXTURE,),
    name="ftw.sliderblock:integration")

FTW_SLIDERBLOCK_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FTW_SLIDERBLOCK_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="ftw.sliderblock:functional")
