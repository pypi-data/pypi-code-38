from ftw.builder import Builder
from ftw.builder import create
from ftw.contacts.contents.contact import IContactSchema
from ftw.contacts.interfaces import IContact
from ftw.contacts.interfaces import ILDAPAttributeMapper
from ftw.contacts.interfaces import ILDAPCustomUpdater
from ftw.contacts.sync.sync import get_ldap_attribute_mapper
from ftw.contacts.sync.sync import sync_contacts
from ftw.contacts.tests import FunctionalTestCase
from zope.component import adapts
from zope.component import getGlobalSiteManager
from zope.component import provideAdapter
from zope.component import provideUtility
from zope.interface import implements
from zope.interface import Interface
import ldif
import os.path


class TestContactSynchronization(FunctionalTestCase):

    def setUp(self):
        super(TestContactSynchronization, self).setUp()
        self.grant('Manager')
        self.contacts = create(Builder('contact folder').titled(u'Contacts'))

    def test_sync_creates_contacts(self):
        res = sync_contacts(self.contacts, get_ldif_records('contacts.ldif'))
        self.assertEquals(5, res['created'])
        self.assertEquals(5, len(self.contacts.objectIds()))

    def test_sync_creates_contact_with_attributes(self):
        res = sync_contacts(self.contacts, get_ldif_records('contact.ldif'))
        self.assertEquals(1, res['created'])

        contact = self.contacts['nina-mueller']
        self.assertEquals(u'cn=M\xfcller Nina,ou=Payroll,dc=domain, dc=net',
                          IContactSchema(contact).ldap_dn)
        self.assertEquals('Nina', IContactSchema(contact).firstname)
        self.assertEquals('M\xc3\xbcller', IContactSchema(contact).lastname)
        self.assertEquals('4teamwork AG', IContactSchema(contact).organization)
        self.assertEquals('n.mueller@4teamwork.ch', IContactSchema(contact).email)
        self.assertEquals('Biel', IContactSchema(contact).city)

    def test_sync_updates_contact(self):
        contact = create(Builder('contact').within(self.contacts).having(
            _id='nina.mueller',
            ldap_dn=u'cn=M\u00fcller Nina,ou=Payroll,dc=domain, dc=net',
            firstname='Nina',
            lastname='Meier',
            ))
        self.contacts.manage_renameObject(contact.id, 'nina-mueller')
        res = sync_contacts(self.contacts, get_ldif_records('contact.ldif'))
        self.assertEquals(1, res['modified'])
        self.assertEquals('Nina', IContactSchema(contact).firstname)
        self.assertEquals('M\xc3\xbcller', IContactSchema(contact).lastname)
        self.assertEquals('4teamwork AG', IContactSchema(contact).organization)
        self.assertEquals('n.mueller@4teamwork.ch', IContactSchema(contact).email)

    def test_sync_contact_without_changes(self):
        res = sync_contacts(self.contacts, get_ldif_records('contact.ldif'))
        res = sync_contacts(self.contacts, get_ldif_records('contact.ldif'))
        self.assertEquals(1, res['unchanged'])

    def test_sync_deletes_contact(self):
        create(Builder('contact').within(self.contacts).having(
            _id='julia.meier',
            ldap_dn=u'cn=Meier Julia,ou=Payroll,dc=domain, dc=net',
        ))
        res = sync_contacts(self.contacts, get_ldif_records('contact.ldif'))
        self.assertEquals(1, res['deleted'])
        self.assertNotIn('julia.meier', self.contacts.objectIds())

    def test_sync_reindexes_updated_contact(self):
        contact = create(Builder('contact').within(self.contacts).having(
            _id='nina-mueller',
            ldap_dn=u'cn=M\u00fcller Nina,ou=Payroll,dc=domain, dc=net',
            firstname='Nina',
            lastname='Meier',
            ))
        self.contacts.manage_renameObject(contact.id, 'nina-mueller')
        res = sync_contacts(self.contacts, get_ldif_records('contact.ldif'))
        self.assertEquals(1, res['modified'])
        catalog_results = self.portal.portal_catalog(Title='M\xc3\xbcller')
        self.assertEquals(1, len(catalog_results))
        self.assertEquals('M\xc3\xbcller Nina', catalog_results[0].Title)


class TestLDAPAttributeMapper(FunctionalTestCase):

    def test_default_mapper(self):
        mapper = get_ldap_attribute_mapper()
        self.assertEquals('uid', mapper.id())
        self.assertEquals('lastname', mapper.mapping()['sn'])

    def test_custom_mapper(self):
        class MyLDAPAttributeMapper(object):
            implements(ILDAPAttributeMapper)

            def mapping(self):
                return {'sAMAccountName': 'userid'}

            def id(self):
                return 'sAMAccountName'

        my_mapper = MyLDAPAttributeMapper()
        provideUtility(my_mapper)
        mapper = get_ldap_attribute_mapper()

        self.assertEquals('sAMAccountName', mapper.id())
        self.assertEquals('userid', mapper.mapping()['sAMAccountName'])

        # cleanup
        getGlobalSiteManager().unregisterUtility(my_mapper, ILDAPAttributeMapper)


class TestCustomUpdater(FunctionalTestCase):

    class MyCustomUpdater(object):
        implements(ILDAPCustomUpdater)
        adapts(IContact, Interface)

        def __init__(self, contact, record):
            self.contact = contact
            self.record = record

        def update(self):
            IContactSchema(self.contact).firstname = 'Tania'
            return True

    def setUp(self):
        super(TestCustomUpdater, self).setUp()
        self.grant('Manager')
        self.contacts = create(Builder('contact folder').titled(u'Contacts'))
        provideAdapter(TestCustomUpdater.MyCustomUpdater)

    def tearDown(self):
        getGlobalSiteManager().unregisterAdapter(TestCustomUpdater.MyCustomUpdater)

    def test_custom_updater_updates_field(self):
        sync_contacts(self.contacts, get_ldif_records('contact.ldif'))
        self.assertEquals(
            'Tania',
            IContactSchema(self.contacts['nina-mueller']).firstname)


def get_ldif_records(filename):
    path = os.path.join(os.path.dirname(__file__), 'assets', filename)
    rlist = ldif.LDIFRecordList(open(path, 'rb'))
    rlist.parse()
    return rlist.all_records
