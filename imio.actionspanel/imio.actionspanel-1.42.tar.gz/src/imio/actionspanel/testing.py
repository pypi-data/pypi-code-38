# -*- coding: utf-8 -*-
from plone.testing import z2, zca
from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import FunctionalTesting
import imio.actionspanel


ACTIONSPANEL_ZCML = zca.ZCMLSandbox(filename="testing.zcml",
                                    package=imio.actionspanel,
                                    name='ACTIONSPANEL_ZCML')

ACTIONSPANEL_Z2 = z2.IntegrationTesting(bases=(z2.STARTUP, ACTIONSPANEL_ZCML),
                                        name='ACTIONSPANEL_Z2')

ACTIONSPANEL_TESTING_PROFILE = PloneWithPackageLayer(
    zcml_filename="testing.zcml",
    zcml_package=imio.actionspanel,
    additional_z2_products=(),
    name="ACTIONSPANEL_TESTING_PROFILE")

ACTIONSPANEL_TESTING_PROFILE_FUNCTIONAL = FunctionalTesting(
    bases=(ACTIONSPANEL_TESTING_PROFILE,), name="ACTIONSPANEL_TESTING_PROFILE_FUNCTIONAL")
