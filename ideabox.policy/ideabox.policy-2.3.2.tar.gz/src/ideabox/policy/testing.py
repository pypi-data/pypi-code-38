# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import ideabox.policy


class IdeaboxPolicyLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.app.dexterity

        self.loadZCML(package=plone.app.dexterity)
        self.loadZCML(package=ideabox.policy)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "ideabox.policy:default")


IDEABOX_POLICY_FIXTURE = IdeaboxPolicyLayer()


IDEABOX_POLICY_INTEGRATION_TESTING = IntegrationTesting(
    bases=(IDEABOX_POLICY_FIXTURE,), name="IdeaboxPolicyLayer:IntegrationTesting"
)


IDEABOX_POLICY_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(IDEABOX_POLICY_FIXTURE,), name="IdeaboxPolicyLayer:FunctionalTesting"
)


IDEABOX_POLICY_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(IDEABOX_POLICY_FIXTURE, REMOTE_LIBRARY_BUNDLE_FIXTURE, z2.ZSERVER_FIXTURE),
    name="IdeaboxPolicyLayer:AcceptanceTesting",
)
