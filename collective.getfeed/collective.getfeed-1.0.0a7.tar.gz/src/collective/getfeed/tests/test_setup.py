# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.getfeed.testing import COLLECTIVEGETFEED_CORE_INTEGRATION_TESTING  # noqa
from plone import api

try:
    from Products.CMFPlone.utils import get_installer
except ImportError:  # Plone < 5.1
    HAS_INSTALLER = False
else:
    HAS_INSTALLER = True

import unittest


class TestSetup(unittest.TestCase):
    """Test that collective.getfeed is properly installed."""

    layer = COLLECTIVEGETFEED_CORE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        if HAS_INSTALLER:
            self.installer = get_installer(self.portal)
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.getfeed is installed."""
        if HAS_INSTALLER:
            self.assertTrue(
                self.installer.is_product_installed('collective.getfeed')
            )
        else:
            self.assertTrue(
                self.installer.isProductInstalled(
                    'collective.getfeed'
                )
            )

    def test_browserlayer(self):
        """Test that ICollectivegetfeedCoreLayer is registered."""
        from collective.getfeed.interfaces import (
            ICollectivegetfeedCoreLayer)
        from plone.browserlayer import utils
        self.assertIn(ICollectivegetfeedCoreLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVEGETFEED_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        if HAS_INSTALLER:
            self.installer = get_installer(self.portal)
            self.installer.uninstall_product('collective.getfeed')
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')
            self.installer.uninstallProducts(['collective.getfeed'])

    def test_product_uninstalled(self):
        """Test if collective.getfeed is cleanly uninstalled."""
        if HAS_INSTALLER:
            self.assertFalse(
                self.installer.is_product_installed('collective.getfeed')
            )
        else:
            self.assertFalse(
                self.installer.isProductInstalled(
                    'collective.getfeed'
                )
            )

    def test_browserlayer_removed(self):
        """Test that ICollectivegetfeedCoreLayer is removed."""
        from collective.getfeed.interfaces import ICollectivegetfeedCoreLayer
        from plone.browserlayer import utils
        self.assertNotIn(ICollectivegetfeedCoreLayer, utils.registered_layers())
