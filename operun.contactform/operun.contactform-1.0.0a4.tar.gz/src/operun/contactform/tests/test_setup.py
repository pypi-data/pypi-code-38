# -*- coding: utf-8 -*-
"""Setup tests for this package."""

from operun.contactform.testing import OPERUN_CONTACTFORM_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


class TestSetup(unittest.TestCase):
    """Test that operun.contactform is properly installed."""

    layer = OPERUN_CONTACTFORM_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if operun.contactform is installed."""
        self.assertTrue(
            self.installer.isProductInstalled('operun.contactform')
        )

    def test_browserlayer(self):
        """Test that IOperunContactformLayer is registered."""
        from operun.contactform.interfaces import IOperunContactformLayer
        from plone.browserlayer import utils

        self.assertIn(IOperunContactformLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = OPERUN_CONTACTFORM_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstallProducts(['operun.contactform'])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if operun.contactform is cleanly uninstalled."""
        self.assertFalse(
            self.installer.isProductInstalled('operun.contactform')
        )

    def test_browserlayer_removed(self):
        """Test that IOperunContactformLayer is removed."""
        from operun.contactform.interfaces import IOperunContactformLayer
        from plone.browserlayer import utils

        self.assertNotIn(IOperunContactformLayer, utils.registered_layers())
