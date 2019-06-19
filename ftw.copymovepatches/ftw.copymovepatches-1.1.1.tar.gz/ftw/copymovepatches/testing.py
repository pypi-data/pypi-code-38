from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from ftw.copymovepatches.utils import IS_PLONE_5
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2
from zope.configuration import xmlconfig
import ftw.copymovepatches.tests.builders


class FtwLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '  <include package="ftw.copymovepatches.tests" file="profiles.zcml" />'
            '</configure>',
            context=configurationContext)

        if not IS_PLONE_5:
            z2.installProduct(app, 'collective.indexing')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.copymovepatches.tests:default')

        if IS_PLONE_5:
            applyProfile(portal, 'plone.app.contenttypes:default')


FTW_FIXTURE = FtwLayer()
FTW_FUNCTIONAL = FunctionalTesting(
    bases=(FTW_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="ftw.copymovepatches:functional")
