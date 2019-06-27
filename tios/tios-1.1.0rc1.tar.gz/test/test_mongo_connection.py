import unittest
from tios import communication 

class TestMongoConnectionMethods(unittest.TestCase):

    def test_initialize_new_mongo_connection(self):
        connection = communication.select('Mongo', 'abc123')
        self.assertIsInstance(connection, communication.MongoConnection)

    def test_has_entry(self):
        connection = communication.MongoConnection('abc123')
        while connection.has_entry():
            connection.delete_entry()
        self.assertFalse(connection.has_entry())
        connection.add_entry()
        self.assertTrue(connection.has_entry())

    def test_set_title(self):
        title = 'New Tios Simulation'
        connection = communication.MongoConnection('abc123')
        update = {'title': title}
        connection.put(update)
        self.assertEqual(title, connection.get('title'))

