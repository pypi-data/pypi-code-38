from ftw.builder import Builder
from ftw.builder import create
from ftw.contacts.testing import FTW_CONTACTS_FUNCTIONAL_TESTING
from ftw.geo.interfaces import IGeocodableLocation
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase
from zope.component import queryAdapter


class TestLocationString(TestCase):

    layer = FTW_CONTACTS_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_none_if_no_address_zip_and_city(self):
        contact = create(Builder('contact'))

        location_adapter = queryAdapter(contact, IGeocodableLocation)

        self.assertEqual(
            None, location_adapter.getLocationString(),
            """If there is no address, no zip_code and no city
            on the contact, it is not possible to do a meaningful
            geocode lookup. So it should return None""")

    def test_full_string_if_address_zip_and_city_is_set(self):
        contact = create(Builder('contact').having(
            address=u"Ch\xfcckstreet 12  ",
            postal_code=u"1234  ",
            city=u"New York  "))

        location_adapter = queryAdapter(contact, IGeocodableLocation)

        self.assertEqual(
            u"Ch\xfcckstreet 12, 1234, New York, Schweiz",
            location_adapter.getLocationString(),
            "The order should be: street, zip, city, country")

    def test_location_string_if_some_info_is_missing(self):
        contact = create(Builder('contact').having(
            address=u"   ",
            city=u"New York"))

        location_adapter = queryAdapter(contact, IGeocodableLocation)

        self.assertEqual(
            u"New York, Schweiz",
            location_adapter.getLocationString(),
            """The adapter should concatenate only the fields with a value""")

    def test_remove_postfach_if_exists_in_address(self):
        contact = create(Builder('contact').having(
            address=u"Ch\xfcckstreet 12\rPostfach",
            city=u"New York"))

        location_adapter = queryAdapter(contact, IGeocodableLocation)

        self.assertEqual(
            u"Ch\xfcckstreet 12, New York, Schweiz",
            location_adapter.getLocationString(),
            """The adapter should concatenate only the fields with a value""")
