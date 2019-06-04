# -*- coding: utf-8 -*-
from plone.app.testing import TEST_USER_ID
from zope.component import queryUtility
from zope.component import createObject
from plone.app.testing import setRoles
from plone.dexterity.interfaces import IDexterityFTI
from plone import api

from collective.getfeed.testing import COLLECTIVEGETFEED_CORE_INTEGRATION_TESTING  # noqa
from collective.getfeed.interfaces import IFeedItem

import unittest


class KontaktIntegrationTest(unittest.TestCase):

    layer = COLLECTIVEGETFEED_CORE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer = api.portal.get_tool('portal_quickinstaller')
        fti = queryUtility(IDexterityFTI, name='Feed Item')
        fti.global_allow = True

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='Feed Item')
        schema = fti.lookupSchema()
        self.assertEqual(IFeedItem, schema)

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='Feed Item')
        self.assertTrue(fti)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='Feed Item')
        factory = fti.factory
        obj = createObject(factory)
        self.assertTrue(IFeedItem.providedBy(obj))

    def test_adding(self):
        feeditem = api.content.create(
            container=self.portal, type='Feed Item', id='feeditem')
        self.assertTrue(IFeedItem.providedBy(feeditem))

    def test_allowed_content_types(self):
        feeditem = api.content.create(
            container=self.portal, type='Feed Item', id='feeditem')
        feed_item_fti = queryUtility(IDexterityFTI, name='Image')
        self.assertIn(feed_item_fti, feeditem.allowedContentTypes())
