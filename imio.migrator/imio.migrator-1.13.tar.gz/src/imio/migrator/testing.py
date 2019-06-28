# -*- coding: utf-8 -*-
from plone.testing import z2, zca
from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import FunctionalTesting
import imio.migrator


MIGRATOR_ZCML = zca.ZCMLSandbox(filename="testing.zcml",
                                package=imio.migrator,
                                name='MIGRATOR_ZCML')

MIGRATOR_Z2 = z2.IntegrationTesting(bases=(z2.STARTUP, MIGRATOR_ZCML),
                                    name='MIGRATOR_Z2')

MIGRATOR_TESTING_PROFILE = PloneWithPackageLayer(
    zcml_filename="testing.zcml",
    zcml_package=imio.migrator,
    additional_z2_products=(),
    name="MIGRATOR_TESTING_PROFILE")

MIGRATOR_TESTING_PROFILE_FUNCTIONAL = FunctionalTesting(
    bases=(MIGRATOR_TESTING_PROFILE,), name="MIGRATOR_TESTING_PROFILE_FUNCTIONAL")

