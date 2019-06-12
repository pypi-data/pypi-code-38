# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.embeddedpage.testing import COLLECTIVE_EMBEDDEDPAGE_INTEGRATION_TESTING  # noqa
from plone import api

import unittest


class TestSetup(unittest.TestCase):
    """Test that collective.embeddedpage is properly installed."""

    layer = COLLECTIVE_EMBEDDEDPAGE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.embeddedpage is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'collective.embeddedpage'))

    def test_browserlayer(self):
        """Test that ICollectiveEmbeddedpageLayer is registered."""
        from collective.embeddedpage.interfaces import (
            ICollectiveEmbeddedpageLayer)
        from plone.browserlayer import utils
        self.assertIn(ICollectiveEmbeddedpageLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_EMBEDDEDPAGE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['collective.embeddedpage'])

    def test_product_uninstalled(self):
        """Test if collective.embeddedpage is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'collective.embeddedpage'))

    def test_browserlayer_removed(self):
        """Test that ICollectiveEmbeddedpageLayer is removed."""
        from collective.embeddedpage.interfaces import ICollectiveEmbeddedpageLayer  # noqa
        from plone.browserlayer import utils
        self.assertNotIn(
            ICollectiveEmbeddedpageLayer,
            utils.registered_layers()
        )
