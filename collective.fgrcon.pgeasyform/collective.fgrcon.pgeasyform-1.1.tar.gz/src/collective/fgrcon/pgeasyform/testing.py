# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import collective.fgrcon.pgeasyform


class CollectiveFgrconPgeasyformLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=collective.fgrcon.pgeasyform)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.fgrcon.pgeasyform:default')


COLLECTIVE_FGRCON_PGEASYFORM_FIXTURE = CollectiveFgrconPgeasyformLayer()


COLLECTIVE_FGRCON_PGEASYFORM_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_FGRCON_PGEASYFORM_FIXTURE,),
    name='CollectiveFgrconPgeasyformLayer:IntegrationTesting',
)


COLLECTIVE_FGRCON_PGEASYFORM_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_FGRCON_PGEASYFORM_FIXTURE,),
    name='CollectiveFgrconPgeasyformLayer:FunctionalTesting',
)


COLLECTIVE_FGRCON_PGEASYFORM_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_FGRCON_PGEASYFORM_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='CollectiveFgrconPgeasyformLayer:AcceptanceTesting',
)
