from ftw.builder import Builder
from ftw.builder import create
from ftw.copymovepatches.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from plone.uuid.interfaces import ATTRIBUTE_NAME
from plone.uuid.interfaces import IUUID
from plone.uuid.interfaces import IUUIDGenerator
from Products.Archetypes import config
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
import transaction


class TestCatalogFixesView(FunctionalTestCase):

    @browsing
    def test_rebuild_broken_uid_index(self, browser):
        self.grant('Manager')
        page = create(Builder('page'))
        self.break_object(page)

        browser.login().open(view='copymovepatches-catalog-fixes')
        self.assertEquals(
            u'UID index state BROKEN:\n'
            u'There are 1 errors in the UID index'
            u' (length difference between forward and backward index BTree).'
            u' The index should be rebuilt from scratch.\n'
            u'\xbb Rebuild UID index',
            browser.css('.uid-index-state-check').first.text)
        browser.click_on('Rebuild UID index')
        self.assertEquals(
            'UID index state OK:',
            browser.css('.uid-index-state-check').first.text)

    @browsing
    # @skipIf(IS_PLONE_5, 'We no longer create AT content within DX.')
    def test_rebuild_broken_brain_metadata(self, browser):
        self.grant('Manager')
        page = create(Builder('page'))
        self.break_object(page)

        browser.login().open(view='copymovepatches-catalog-fixes')
        self.assertEquals(
            u'UIDs in brain metadata: UNKOWN:\n'
            u'The brain metadata check depends on the UID index state,'
            u' which is currently broken.',
            browser.css('.brain-metadata-check').first.text)
        browser.click_on('Rebuild UID index')

        self.assertEquals(
            u'UIDs in brain metadata: BROKEN:\n'
            u'There are 1 brains with a wrong UID in the metadata.'
            u' The UID value in the brain metadata should be recalculated.\n'
            u'\xbb Rebuild brain metadata',
            browser.css('.brain-metadata-check').first.text)
        browser.click_on('Rebuild brain metadata')

        self.assertEquals(
            'UIDs in brain metadata: OK',
            browser.css('.brain-metadata-check').first.text)

    def break_object(self, obj):
        # Simulate that the object was copied without properly updating
        # the new UID, leaving the catalog in an inconsistent state.

        # Break UID index
        portal_catalog = getToolByName(self.portal, 'portal_catalog')
        del portal_catalog._catalog.indexes['UID']._index[IUUID(obj)]

        # Change UID so that brain metadata is incorrect.
        # This used to happen on copy/paste without the patch provided
        # by this package.
        self._change_uid(obj)

        transaction.commit()

    def _change_uid(self, obj):

        # Change UID for Archetypes:
        if hasattr(obj, config.UUID_ATTR):
            setattr(obj, config.UUID_ATTR, getUtility(IUUIDGenerator)())

        # Change UID for Dexterity:
        if hasattr(obj, ATTRIBUTE_NAME):
            setattr(obj, ATTRIBUTE_NAME, getUtility(IUUIDGenerator)())
