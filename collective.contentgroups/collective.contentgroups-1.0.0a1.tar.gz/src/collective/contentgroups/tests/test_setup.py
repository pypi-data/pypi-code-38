# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.contentgroups import testing
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFPlone.utils import get_installer

import unittest


class TestSetup(unittest.TestCase):
    """Test that collective.contentgroups is properly installed."""

    layer = testing.COLLECTIVE_CONTENT_GROUPS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.installer = get_installer(self.portal)

    def test_product_installed(self):
        """Test if collective.contentgroups is installed."""
        self.assertTrue(self.installer.is_product_installed("collective.contentgroups"))

    def test_plugin_installed(self):
        from collective.contentgroups.config import PLUGIN_ID

        self.assertIn(PLUGIN_ID, self.portal.acl_users.objectIds())

    def test_add_contentgroups_plugin(self):
        # We do not use this, but it should not fail either.
        from collective.contentgroups.plugins import add_contentgroups_plugin

        self.assertIsNone(add_contentgroups_plugin())


class TestUninstall(unittest.TestCase):

    layer = testing.COLLECTIVE_CONTENT_GROUPS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.installer = get_installer(self.portal)
        roles_before = api.user.get_roles(username=TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.assertTrue(self.installer.uninstall_product("collective.contentgroups"))
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if collective.contentgroups is cleanly uninstalled."""
        self.assertFalse(
            self.installer.is_product_installed("collective.contentgroups")
        )
        self.assertTrue(
            self.installer.is_product_installable("collective.contentgroups")
        )

    def test_plugin_uninstalled(self):
        from collective.contentgroups.config import PLUGIN_ID

        self.assertNotIn(PLUGIN_ID, self.portal.acl_users.objectIds())
