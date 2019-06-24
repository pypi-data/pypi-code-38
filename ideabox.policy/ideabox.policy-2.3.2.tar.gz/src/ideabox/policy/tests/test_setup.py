# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from ideabox.policy.testing import IDEABOX_POLICY_INTEGRATION_TESTING

import unittest


class TestSetup(unittest.TestCase):
    """Test that ideabox.policy is properly installed."""

    layer = IDEABOX_POLICY_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.installer = api.portal.get_tool("portal_quickinstaller")

    def test_product_installed(self):
        """Test if ideabox.policy is installed."""
        self.assertTrue(self.installer.isProductInstalled("ideabox.policy"))

    def test_browserlayer(self):
        """Test that IIdeaboxPolicyLayer is registered."""
        from ideabox.policy.interfaces import IIdeaboxPolicyLayer
        from plone.browserlayer import utils

        self.assertIn(IIdeaboxPolicyLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = IDEABOX_POLICY_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.installer = api.portal.get_tool("portal_quickinstaller")
        self.installer.uninstallProducts(["ideabox.policy"])

    def test_product_uninstalled(self):
        """Test if ideabox.policy is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled("ideabox.policy"))

    def test_browserlayer_removed(self):
        """Test that IIdeaboxPolicyLayer is removed."""
        from ideabox.policy.interfaces import IIdeaboxPolicyLayer
        from plone.browserlayer import utils

        self.assertNotIn(IIdeaboxPolicyLayer, utils.registered_layers())
