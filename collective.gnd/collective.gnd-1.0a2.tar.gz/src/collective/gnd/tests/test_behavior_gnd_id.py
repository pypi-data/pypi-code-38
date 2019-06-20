# -*- coding: utf-8 -*-
from collective.gnd.behaviors.gnd_id import IGndIdMarker
from collective.gnd.testing import COLLECTIVE_GND_INTEGRATION_TESTING  # noqa
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.behavior.interfaces import IBehavior
from zope.component import getUtility

import unittest


class GndIdIntegrationTest(unittest.TestCase):

    layer = COLLECTIVE_GND_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_behavior_gnd_id(self):
        behavior = getUtility(IBehavior, 'collective.gnd.gnd_id')
        self.assertEqual(
            behavior.marker,
            IGndIdMarker,
        )
