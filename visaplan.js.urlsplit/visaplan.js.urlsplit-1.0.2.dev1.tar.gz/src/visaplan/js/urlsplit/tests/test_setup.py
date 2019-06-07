# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from visaplan.js.urlsplit.testing import VISAPLAN_JS_URLSPLIT_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that visaplan.js.urlsplit is properly installed."""

    layer = VISAPLAN_JS_URLSPLIT_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if visaplan.js.urlsplit is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'visaplan.js.urlsplit'))

    def test_browserlayer(self):
        """Test that IVisaplanJsUrlsplitLayer is registered."""
        from visaplan.js.urlsplit.interfaces import (
            IVisaplanJsUrlsplitLayer)
        from plone.browserlayer import utils
        self.assertIn(
            IVisaplanJsUrlsplitLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = VISAPLAN_JS_URLSPLIT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstallProducts(['visaplan.js.urlsplit'])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if visaplan.js.urlsplit is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'visaplan.js.urlsplit'))

    def test_browserlayer_removed(self):
        """Test that IVisaplanJsUrlsplitLayer is removed."""
        from visaplan.js.urlsplit.interfaces import \
            IVisaplanJsUrlsplitLayer
        from plone.browserlayer import utils
        self.assertNotIn(
            IVisaplanJsUrlsplitLayer,
            utils.registered_layers())
