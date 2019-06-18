from unittest import TestCase

from dateutil.parser import parse
import pycodestyle

from ems_client.service import Service


class TestCodeFormat(TestCase):

    def test_conformance(self):
        """Test that we conform to PEP-8."""
        style = pycodestyle.StyleGuide()
        result = style.check_files(['ems_client'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")


class ServiceTests(TestCase):

    def setUp(self):
        if not hasattr(self, '_api'):
            self._api = Service()

    def test_apiversion(self):
        version = self._api.get_api_version()
        self.assertGreaterEqual(version["Version"], "1.1.32.0", "API version")
        self.assertTrue(version["License"] in ["Basic", "Advanced"])

    def test_booking(self):
        booking = self._api.get_booking(8152)
        self.assertEquals(booking.event_name, 'Joe & Harold Wedding Reception')
        self.assertEquals(booking.contact, 'Harold Jones 555-555-1010')
        booking = self._api.get_booking(8806)
        self.assertEquals(booking.event_name, 'Test')
        self.assertEquals(booking.contact, '206-685-9906')

    def test_bookings(self):
        bookings = self._api.get_bookings('2016-01-01', '2016-01-01')
        self.assertGreaterEqual(len(bookings), 1)
        self.assertEquals(bookings[0].contact, '206-685-9906')
        self.assertEquals(bookings[0].contact_email_address, 'bradleyb@uw.edu')
        self.assertIsNone(bookings[1].contact_email_address)
        bookings = self._api.get_bookings('2016-01-02', '2016-01-02')
        self.assertGreaterEqual(len(bookings), 1)
        self.assertEquals(bookings[0].contact, 'Harold Jones 555-555-1010')
        self.assertEquals(bookings[0].contact_email_address,
                          'harold.n.jones@example.com')

    def test_bookings2(self):
        bookings = self._api.get_bookings2(439, '2016-01-01', '2016-01-01')
        self.assertEquals(len(bookings), 1)
        self.assertEquals(bookings[0].contact, '206-685-9906')
        self.assertEquals(bookings[0].contact_email_address, 'bradleyb@uw.edu')
        bookings = self._api.get_bookings2(439, '2016-01-02', '2016-01-02')
        self.assertEquals(len(bookings), 0)

    def test_changed_bookings(self):
        bookings = self._api.get_changed_bookings('2015-06-23', '2015-06-25')
        self.assertGreaterEqual(len(bookings), 1)
        self.assertEquals(bookings[0].date_changed.date(),
                          parse('2015-06-24').date())

    def test_buildings(self):
        buildings = self._api.get_buildings()
        self.assertGreaterEqual(len(buildings), 3)

    def test_event_types(self):
        event_types = self._api.get_event_types()
        self.assertGreaterEqual(len(event_types), 3)

    def test_rooms(self):
        rooms = self._api.get_all_rooms()
        self.assertGreaterEqual(len(rooms), 0)
        active_rooms = list(filter(lambda rm: rm.active, rooms))
        self.assertEqual(len(active_rooms), 53)

    def test_service_orders(self):
        service_orders = self._api.get_service_order_details('2016-01-01',
                                                             '2016-01-01')
        self.assertEqual(len(service_orders), 2)
        service_orders = self._api.get_service_order_details('2016-01-02',
                                                             '2016-01-02')
        self.assertEqual(len(service_orders), 4)

    def test_statuses(self):
        statuses = self._api.get_statuses()
        self.assertGreaterEqual(len(statuses), 16)
