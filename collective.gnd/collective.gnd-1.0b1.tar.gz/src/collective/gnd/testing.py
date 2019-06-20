# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import collective.gnd


class CollectiveGndLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.restapi
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=collective.gnd)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.gnd:default')


COLLECTIVE_GND_FIXTURE = CollectiveGndLayer()


COLLECTIVE_GND_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_GND_FIXTURE,),
    name='CollectiveGndLayer:IntegrationTesting',
)


COLLECTIVE_GND_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_GND_FIXTURE,),
    name='CollectiveGndLayer:FunctionalTesting',
)


COLLECTIVE_GND_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_GND_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='CollectiveGndLayer:AcceptanceTesting',
)
