# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import visaplan.js.urlsplit


class VisaplanJsUrlsplitLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.app.dexterity
        self.loadZCML(package=plone.app.dexterity)
        self.loadZCML(package=visaplan.js.urlsplit)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'visaplan.js.urlsplit:default')


VISAPLAN_JS_URLSPLIT_FIXTURE = VisaplanJsUrlsplitLayer()


VISAPLAN_JS_URLSPLIT_INTEGRATION_TESTING = IntegrationTesting(
    bases=(VISAPLAN_JS_URLSPLIT_FIXTURE,),
    name='VisaplanJsUrlsplitLayer:IntegrationTesting',
)


VISAPLAN_JS_URLSPLIT_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(VISAPLAN_JS_URLSPLIT_FIXTURE,),
    name='VisaplanJsUrlsplitLayer:FunctionalTesting',
)


VISAPLAN_JS_URLSPLIT_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        VISAPLAN_JS_URLSPLIT_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='VisaplanJsUrlsplitLayer:AcceptanceTesting',
)
