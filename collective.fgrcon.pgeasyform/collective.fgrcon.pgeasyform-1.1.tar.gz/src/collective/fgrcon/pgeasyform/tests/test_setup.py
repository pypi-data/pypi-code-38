# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.fgrcon.pgeasyform.testing import (
    COLLECTIVE_FGRCON_PGEASYFORM_INTEGRATION_TESTING,
)  # noqa
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


class TestSetup(unittest.TestCase):
    """Test that collective.fgrcon.pgeasyform is properly installed."""

    layer = COLLECTIVE_FGRCON_PGEASYFORM_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.fgrcon.pgeasyform is installed."""
        self.assertTrue(
            self.installer.isProductInstalled('collective.fgrcon.pgeasyform')
        )

    def test_browserlayer(self):
        """Test that ICollectiveFgrconPgeasyformLayer is registered."""
        from collective.fgrcon.pgeasyform.interfaces import (
            ICollectiveFgrconPgeasyformLayer,
        )
        from plone.browserlayer import utils

        self.assertIn(
            ICollectiveFgrconPgeasyformLayer, utils.registered_layers()
        )


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_FGRCON_PGEASYFORM_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstallProducts(['collective.fgrcon.pgeasyform'])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if collective.fgrcon.pgeasyform is cleanly uninstalled."""
        self.assertFalse(
            self.installer.isProductInstalled('collective.fgrcon.pgeasyform')
        )

    def test_browserlayer_removed(self):
        """Test that ICollectiveFgrconPgeasyformLayer is removed."""
        from collective.fgrcon.pgeasyform.interfaces import (
            ICollectiveFgrconPgeasyformLayer,
        )
        from plone.browserlayer import utils

        self.assertNotIn(
            ICollectiveFgrconPgeasyformLayer, utils.registered_layers()
        )
