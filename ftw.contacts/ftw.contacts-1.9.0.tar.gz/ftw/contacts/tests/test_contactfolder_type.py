from ftw.builder import Builder
from ftw.builder import create
from ftw.contacts.contents.contactfolder import IContactFolderSchema
from ftw.contacts.interfaces import IContactFolder
from ftw.contacts.testing import FTW_CONTACTS_FUNCTIONAL_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from unittest2 import TestCase
from zope.component import createObject
from zope.component import queryUtility


class TestContactFolderInstallation(TestCase):

    layer = FTW_CONTACTS_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_adding(self):
        contactfolder = create(
            Builder('contact folder').titled(u'Contact folder'))

        self.assertTrue(IContactFolder.providedBy(contactfolder))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='ftw.contacts.ContactFolder')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='ftw.contacts.ContactFolder')
        schema = fti.lookupSchema()
        self.assertEqual(IContactFolderSchema, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='ftw.contacts.ContactFolder')
        factory = fti.factory
        new_object = createObject(factory)
        self.assertTrue(IContactFolderSchema.providedBy(new_object))
