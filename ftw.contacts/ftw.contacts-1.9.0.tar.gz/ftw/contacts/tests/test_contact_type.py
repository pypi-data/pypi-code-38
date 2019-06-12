from ftw.builder import Builder
from ftw.builder import create
from ftw.contacts.contents.contact import IContactSchema
from ftw.contacts.interfaces import IContact
from ftw.contacts.testing import FTW_CONTACTS_FUNCTIONAL_TESTING
from ftw.contacts.testing import FTW_CONTACTS_GEO_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from unittest2 import TestCase
from z3c.relationfield.interfaces import IHasIncomingRelations
from zope.component import createObject
from zope.component import queryUtility


class TestDefaultView(TestCase):
    layer = FTW_CONTACTS_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.contactfolder = create(
            Builder('contact folder').titled(u'Contact folder'))

    @browsing
    def test_call_view_does_not_fail(self, browser):
        browser.login().visit(
            self.contactfolder, view="++add++ftw.contacts.Contact")

        browser.fill({
            'Organization': '',
            'Firstname': 'Chuck',
            'Lastname': 'N\xc3\xb6rris'}).submit()

        self.assertEqual(1, len(browser.css('#contact-view')))

    @browsing
    def test_do_not_show_map_widget(self, browser):
        browser.login().visit(
            self.contactfolder, view="++add++ftw.contacts.Contact")

        browser.fill({
            'Firstname': 'Chuck',
            'Lastname': 'N\xc3\xb6rris'}).submit()

        self.assertEqual(0, len(browser.css('.mapWidget')))

    @browsing
    def test_show_memberships_of_contact(self, browser):
        contact = create(Builder('contact')
                         .with_minimal_info(u'Ch\xf6ck', u'4orris')
                         .within(self.contactfolder))

        create(Builder('member block')
               .within(self.contactfolder)
               .contact(contact)
               .titled(u"A MemberBlock"))

        create(Builder('member block')
               .within(self.contactfolder)
               .contact(contact)
               .titled(u"A MemberBlock"))

        browser.login().visit(contact)

        self.assertEqual(2, len(browser.css('.memberships li')))

        # Now hide the memberships
        browser.visit(contact, view='edit')
        browser.fill({u'Hide memberships': True}).submit()
        self.assertEqual([], browser.css('.memberships'))

    @browsing
    def test_memberships_sorted_alphabetically(self, browser):
        """
        This test makes sure that the back references (AKA member ships)
        of a contact are sorted alphabetically by the title of their
        container.
        """
        contact = create(Builder('contact')
                         .with_minimal_info(u'John', u'Doe')
                         .within(self.contactfolder))

        zzz = create(Builder('sl content page').titled(u'ZZZ'))
        create(Builder('member block')
               .within(zzz)
               .contact(contact))

        aaa = create(Builder('sl content page').titled(u'AAA'))
        create(Builder('member block')
               .within(aaa)
               .contact(contact))

        ttt = create(Builder('sl content page').titled(u'TTT'))
        create(Builder('member block')
               .within(ttt)
               .contact(contact))

        browser.login().visit(contact)
        self.assertEqual(
            [
                'AAA',
                'TTT',
                'ZZZ',
            ],
            browser.css('.memberships li').text
        )

    @browsing
    def test_membership_links_point_to_container(self, browser):
        """
        This test makes sure that the membership links on the contact
        point to the container of the memberblock and not the
        memberblock itself.
        """
        contact = create(Builder('contact')
                         .with_minimal_info(u'Ch\xf6ck', u'4orris')
                         .within(self.contactfolder))

        page = create(Builder('sl content page').titled(u'Team'))

        create(Builder('member block')
               .within(page)
               .contact(contact)
               .titled(u"A MemberBlock")
               .having(function=u'Epic splitter'))

        browser.login().visit(contact)
        self.assertEqual(
            'http://nohost/plone/team#a-memberblock',
            browser.css('.memberships li a').first.attrib['href']
        )


class TestIdGeneration(TestCase):

    layer = FTW_CONTACTS_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    @browsing
    def test_generate_id_from_last_and_firstname(self, browser):
        contactfolder = create(
            Builder('contact folder').titled(u'Contact folder'))
        browser.login().visit(
            contactfolder, view="++add++ftw.contacts.Contact")

        browser.fill({
            'Organization': '',
            'Firstname': 'Chuck',
            'Lastname': 'N\xc3\xb6rris'}).submit()

        self.assertEqual(
            1, len(contactfolder.listFolderContents()),
            "Something went wrong while creating the contact")

        self.assertEqual(
            "norris-chuck", contactfolder.listFolderContents()[0].id)

    @browsing
    def test_generate_id_from_organization(self, browser):
        contactfolder = create(
            Builder('contact folder').titled(u'Contact folder'))
        browser.login().visit(
            contactfolder, view="++add++ftw.contacts.Contact")

        browser.fill({
            'Organization': 'CIA Headquarter',
            'Firstname': '',
            'Lastname': ''}).submit()

        self.assertEqual(
            1, len(contactfolder.listFolderContents()),
            "Something went wrong while creating the contact")

        self.assertEqual(
            "cia-headquarter", contactfolder.listFolderContents()[0].id)


class TestTitleGeneration(TestCase):
    """
    """
    layer = FTW_CONTACTS_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    @browsing
    def test_generate_title_from_last_and_firstname(self, browser):
        contactfolder = create(
            Builder('contact folder').titled(u'Contact folder'))
        browser.login().visit(
            contactfolder, view="++add++ftw.contacts.Contact")

        browser.fill({
            'Organization': '',
            'Firstname': 'Chuck',
            'Lastname': 'N\xc3\xb6rris'}).submit()

        self.assertEqual(
            1, len(contactfolder.listFolderContents()),
            "Something went wrong while creating the contact")

        self.assertEqual(
            u'N\xf6rris Chuck', contactfolder.listFolderContents()[0].title)

    @browsing
    def test_generate_title_from_organization(self, browser):
        contactfolder = create(
            Builder('contact folder').titled(u'Contact folder'))
        browser.login().visit(
            contactfolder, view="++add++ftw.contacts.Contact")

        browser.fill({
            'Organization': 'CIA Headquarter',
            'Firstname': '',
            'Lastname': ''}).submit()

        self.assertEqual(
            1, len(contactfolder.listFolderContents()),
            "Something went wrong while creating the contact")

        self.assertEqual(
            u"CIA Headquarter", contactfolder.listFolderContents()[0].title)

    @browsing
    def test_setting_title_does_nothing(self, browser):
        contactfolder = create(
            Builder('contact folder').titled(u'Contact folder'))
        browser.login().visit(
            contactfolder, view="++add++ftw.contacts.Contact")

        browser.fill({
            'Organization': 'CIA Headquarter',
            'Firstname': '',
            'Lastname': ''}).submit()

        contact = contactfolder.listFolderContents()[0]
        contact.setTitle("Chucks Headquarter")

        self.assertEqual(
            u"CIA Headquarter", contactfolder.listFolderContents()[0].title)


class TestContactValidateOrganizationOrFullname(TestCase):

    layer = FTW_CONTACTS_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    @browsing
    def test_error_if_no_first_last_and_org_name(self, browser):
        contactfolder = create(
            Builder('contact folder').titled(u'Contact folder'))
        browser.login().visit(
            contactfolder, view="++add++ftw.contacts.Contact")

        browser.fill({
            'Organization': '',
            'Firstname': '',
            'Lastname': ''}).submit()

        self.assertEqual(1, len(browser.css('.portalMessage.error')))
        self.assertTrue(browser.url.endswith('++add++ftw.contacts.Contact'))

    @browsing
    def test_error_if_only_firstname_exists(self, browser):
        contactfolder = create(
            Builder('contact folder').titled(u'Contact folder'))
        browser.login().visit(
            contactfolder, view="++add++ftw.contacts.Contact")

        browser.fill({'Firstname': "Chuck"}).submit()

        self.assertEqual(1, len(browser.css('.portalMessage.error')))
        self.assertTrue(browser.url.endswith('++add++ftw.contacts.Contact'))

    @browsing
    def test_error_if_only_lastname_exists(self, browser):
        contactfolder = create(
            Builder('contact folder').titled(u'Contact folder'))
        browser.login().visit(
            contactfolder, view="++add++ftw.contacts.Contact")

        browser.fill({'Lastname': "Norris"}).submit()

        self.assertEqual(1, len(browser.css('.portalMessage.error')))
        self.assertTrue(browser.url.endswith('++add++ftw.contacts.Contact'))

    @browsing
    def test_no_error_if_org_name_exists(self, browser):
        contactfolder = create(
            Builder('contact folder').titled(u'Contact folder'))
        browser.login().visit(
            contactfolder, view="++add++ftw.contacts.Contact")

        browser.fill({'Organization': "CIA"}).submit()

        self.assertEqual(0, len(browser.css('.portalMessage.error')))
        self.assertEqual(
            1, len(contactfolder.listFolderContents()),
            "Something went wrong while creating the contact")

    @browsing
    def test_no_error_if_first_and_last_name_exists(self, browser):
        contactfolder = create(
            Builder('contact folder').titled(u'Contact folder'))
        browser.login().visit(
            contactfolder, view="++add++ftw.contacts.Contact")

        browser.fill({
            'Firstname': "Chuck",
            'Lastname': "N\xc3\xb6rris"}).submit()

        self.assertEqual(0, len(browser.css('.portalMessage.error')))
        self.assertEqual(
            1, len(contactfolder.listFolderContents()),
            "Something went wrong while creating the contact")


class TestContactInstallation(TestCase):

    layer = FTW_CONTACTS_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_adding(self):
        contact = create(Builder('contact'))
        self.assertTrue(IContact.providedBy(contact))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='ftw.contacts.Contact')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='ftw.contacts.Contact')
        schema = fti.lookupSchema()
        self.assertEqual(IContactSchema, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='ftw.contacts.Contact')
        factory = fti.factory
        new_object = createObject(factory)
        self.assertTrue(IContactSchema.providedBy(new_object))

    def test_relation(self):
        contact = create(Builder('contact'))
        self.assertTrue(IHasIncomingRelations.providedBy(contact))


class TestDefaultGeoView(TestCase):
    layer = FTW_CONTACTS_GEO_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.contactfolder = create(
            Builder('contact folder').titled(u'Contact folder'))

    @browsing
    def test_show_map_widget(self, browser):
        browser.login().visit(
            self.contactfolder, view="++add++ftw.contacts.Contact")

        browser.fill({
            'Firstname': 'Chuck',
            'Lastname': 'N\xc3\xb6rris'}).submit()

        self.assertEqual(1, len(browser.css('.mapWidget')))

        # Now hide map
        browser.find('Edit').click()
        browser.fill({u'Hide map': True}).submit()
        self.assertEqual([], browser.css('.mapWidget'))
