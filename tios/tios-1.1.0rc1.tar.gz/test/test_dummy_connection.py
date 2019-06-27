import unittest
from tios import imd_sim, communication

class TestDummyConnectionMethods(unittest.TestCase):

    def test_initialize_new_dummy_connection(self):
        connection = communication.select('Dummy', 'abc123')
        self.assertIsInstance(connection, communication.DummyConnection)

    def test_has_entry(self):
        connection = communication.DummyConnection('abc123')
        self.assertFalse(connection.has_entry())
        connection.add_entry()
        self.assertTrue(connection.has_entry())

    def test_set_title(self):
        title = 'New Tios Simulation'
        connection = communication.DummyConnection('abc123')
        update = {'title': title}
        connection.put(update)
        self.assertEqual(title, connection.get('title'))

