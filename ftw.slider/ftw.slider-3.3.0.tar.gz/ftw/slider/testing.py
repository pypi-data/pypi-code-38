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
from plone.app.testing import TEST_USER_NAME
from zope.configuration import xmlconfig
import ftw.referencewidget.tests.widgets
import ftw.slider.tests.builders  # noqa


class SliderLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '</configure>',
            context=configurationContext)

    def setUpPloneSite(self, portal):
        login(portal, TEST_USER_NAME)
        # Install into Plone site using portal_setup
        applyProfile(portal, 'ftw.slider:default')
        if IS_PLONE_5:
            applyProfile(portal, 'plone.app.contenttypes:default')


SLIDER_TAGS_FIXTURE = SliderLayer()
SLIDER_INTEGRATION_TESTING = IntegrationTesting(
    bases=(SLIDER_TAGS_FIXTURE,),
    name="ftw.slider:integration")
SLIDER_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(SLIDER_TAGS_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="ftw.slider:functional")
