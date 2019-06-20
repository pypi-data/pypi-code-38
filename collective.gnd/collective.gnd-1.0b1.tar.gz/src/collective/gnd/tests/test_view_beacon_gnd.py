# -*- coding: utf-8 -*-
from collective.gnd.testing import COLLECTIVE_GND_FUNCTIONAL_TESTING
from collective.gnd.testing import COLLECTIVE_GND_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.component import getMultiAdapter
from zope.component.interfaces import ComponentLookupError

import unittest


class ViewsIntegrationTest(unittest.TestCase):

    layer = COLLECTIVE_GND_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        api.content.create(self.portal, 'Document', 'front-page')

    def test_beacon_gnd_is_registered(self):
        view = getMultiAdapter(
            (self.portal, self.portal.REQUEST),
            name='beacon-gnd.txt'
        )
        self.assertTrue(view.__name__ == 'beacon-gnd.txt')

    def test_beacon_gnd_not_matching_interface(self):
        with self.assertRaises(ComponentLookupError):
            getMultiAdapter(
                (self.portal['front-page'], self.portal.REQUEST),
                name='beacon-gnd.txt'
            )


class ViewsFunctionalTest(unittest.TestCase):

    layer = COLLECTIVE_GND_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
