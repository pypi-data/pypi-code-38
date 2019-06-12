# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import collective.embeddedpage


class CollectiveEmbeddedpageLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=collective.embeddedpage)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.embeddedpage:default')


COLLECTIVE_EMBEDDEDPAGE_FIXTURE = CollectiveEmbeddedpageLayer()


COLLECTIVE_EMBEDDEDPAGE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_EMBEDDEDPAGE_FIXTURE,),
    name='CollectiveEmbeddedpageLayer:IntegrationTesting'
)


COLLECTIVE_EMBEDDEDPAGE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_EMBEDDEDPAGE_FIXTURE, z2.ZSERVER_FIXTURE),
    name='CollectiveEmbeddedpageLayer:FunctionalTesting'
)


COLLECTIVE_EMBEDDEDPAGE_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_EMBEDDEDPAGE_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='CollectiveEmbeddedpageLayer:AcceptanceTesting'
)
