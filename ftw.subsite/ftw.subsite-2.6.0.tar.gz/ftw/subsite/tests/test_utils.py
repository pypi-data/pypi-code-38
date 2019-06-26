from ftw.subsite.testing import FTW_SUBSITE_INTEGRATION_TESTING
from ftw.subsite.utils import find_context
from ftw.subsite.utils import get_nav_root
from plone.app.layout.navigation.interfaces import INavigationRoot
from zope.interface import alsoProvides
import unittest2 as unittest


class TestUtilsIntegration(unittest.TestCase):

    layer = FTW_SUBSITE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def tearDown(self):
        if 'folder' in self.portal.objectIds():
            self.portal.manage_delObjects(['folder'])

    def test_get_nav_root(self):
        folder = self.portal.get(self.portal.invokeFactory('Folder', 'folder'))

        self.assertEquals(self.portal, get_nav_root(folder))
        self.assertEquals(self.portal, get_nav_root(self.portal))

        doc = folder.get(folder.invokeFactory('Document', 'doc'))
        self.assertEquals(self.portal, get_nav_root(doc))

        # Create a second document, because the first call with doc is cached
        doc2 = folder.get(folder.invokeFactory('Document', 'doc2'))
        alsoProvides(folder, INavigationRoot)
        self.assertEquals(folder, get_nav_root(doc2))

    def test_find_context(self):
        # This tests the edge case if no real Request (from a browser)
        # is available. It should return the app
        # All other testcases are tested by test_forcelanguage
        doc = self.portal.get(self.portal.invokeFactory('Document', 'doc'))
        self.assertEquals(self.layer['app'], find_context(doc.REQUEST))
