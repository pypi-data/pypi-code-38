# -*- coding: utf-8 -*-
from plone.app.testing import TEST_USER_ID
from zope.component import queryUtility
from zope.component import createObject
from plone.app.testing import setRoles
from plone.dexterity.interfaces import IDexterityFTI
from plone import api

from collective.embeddedpage.testing import COLLECTIVE_EMBEDDEDPAGE_INTEGRATION_TESTING  # noqa
from collective.embeddedpage.interfaces import IEmbeddedPage

import unittest


class EmbeddedPageIntegrationTest(unittest.TestCase):

    layer = COLLECTIVE_EMBEDDEDPAGE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='EmbeddedPage')
        schema = fti.lookupSchema()
        self.assertEqual(IEmbeddedPage, schema)

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='EmbeddedPage')
        self.assertTrue(fti)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='EmbeddedPage')
        factory = fti.factory
        obj = createObject(factory)
        self.assertTrue(IEmbeddedPage.providedBy(obj))

    def test_adding(self):
        self.portal.invokeFactory('EmbeddedPage', 'EmbeddedPage')
        self.assertTrue(
            IEmbeddedPage.providedBy(self.portal['EmbeddedPage'])
        )
