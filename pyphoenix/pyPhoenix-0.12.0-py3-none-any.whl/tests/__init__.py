import os
import unittest
import pyphoenix

TEST_DB_URL = os.environ.get('pyphoenix_TEST_DB_URL')


@unittest.skipIf(TEST_DB_URL is None, "these tests require the pyphoenix_TEST_DB_URL environment variable set to a clean database")
class DatabaseTestCase(unittest.TestCase):
    
    def setUp(self):
        self.conn = pyphoenix.connect(TEST_DB_URL, autocommit=True)
        self.cleanup_tables = []

    def tearDown(self):
        self.doCleanups()
        self.conn.close()

    def addTableCleanup(self, name):
        def dropTable():
            with self.conn.cursor() as cursor:
                cursor.execute("DROP TABLE IF EXISTS {}".format(name))
        self.addCleanup(dropTable)

    def createTable(self, name, columns):
        with self.conn.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS {}".format(name))
            cursor.execute("CREATE TABLE {} ({})".format(name, columns))
            self.addTableCleanup(name)
