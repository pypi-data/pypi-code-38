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
        api.content.create(self.portal, 'Folder', 'other-folder')
        api.content.create(self.portal, 'Document', 'front-page')

    def test_resolvegnd_is_registered(self):
        view = getMultiAdapter(
            (self.portal['other-folder'], self.portal.REQUEST),
            name='resolvegnd'
        )
        self.assertTrue(view.__name__ == 'resolvegnd')
        # self.assertTrue(
        #     'Sample View' in view(),
        #     'Sample View is not found in resolvegnd'
        # )

    def test_resolvegnd_not_matching_interface(self):
        with self.assertRaises(ComponentLookupError):
            getMultiAdapter(
                (self.portal['front-page'], self.portal.REQUEST),
                name='resolvegnd'
            )


class ViewsFunctionalTest(unittest.TestCase):

    layer = COLLECTIVE_GND_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
