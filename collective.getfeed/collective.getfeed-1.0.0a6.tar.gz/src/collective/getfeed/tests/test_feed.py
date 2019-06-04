# -*- coding: utf-8 -*-
from plone.app.testing import TEST_USER_ID
from zope.component import queryUtility
from zope.component import createObject
from plone.app.testing import setRoles
from plone.dexterity.interfaces import IDexterityFTI
from plone import api

from collective.getfeed.testing import COLLECTIVEGETFEED_CORE_INTEGRATION_TESTING  # noqa
from collective.getfeed.interfaces import IFeed

import unittest


class KontaktIntegrationTest(unittest.TestCase):

    layer = COLLECTIVEGETFEED_CORE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer = api.portal.get_tool('portal_quickinstaller')
        fti = queryUtility(IDexterityFTI, name='Feed')
        fti.global_allow = True

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='Feed')
        schema = fti.lookupSchema()
        self.assertEqual(IFeed, schema)

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='Feed')
        self.assertTrue(fti)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='Feed')
        factory = fti.factory
        obj = createObject(factory)
        self.assertTrue(IFeed.providedBy(obj))

    def test_adding(self):
        feed = api.content.create(
            container=self.portal, type='Feed', id='feed')
        self.assertTrue(IFeed.providedBy(feed))

    def test_allowed_content_types(self):
        feed = api.content.create(
            container=self.portal, type='Feed', id='feed')
        feed_item_fti = queryUtility(IDexterityFTI, name='Feed Item')
        self.assertIn(feed_item_fti, feed.allowedContentTypes())
