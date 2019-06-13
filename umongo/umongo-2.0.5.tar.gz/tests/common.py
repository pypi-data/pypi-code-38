import pymongo

from umongo.document import DocumentImplementation
from umongo.instance import Instance, LazyLoaderInstance
from umongo.builder import BaseBuilder
from umongo.frameworks import register_builder


TEST_DB = 'umongo_test'


# Use a sync driver for easily drop the test database
con = pymongo.MongoClient()


# Provide mocked database, collection and builder for easier testing


class MockedCollection():

    def __init__(self, db, name):
        self.db = db
        self.name = name

    def __eq__(self, other):
        return (isinstance(other, MockedCollection) and
                self.db == other.db and self.name == other.name)

    def __repr__(self):
        return "<%s db=%s, name=%s>" % (self.__class__.__name__, self.db, self.name)


class MockedDB:

    def __init__(self, name):
        self.name = name
        self.cols = {}

    def __getattr__(self, name):
        if name not in self.cols:
            self.cols[name] = MockedCollection(self, name)
        return self.cols[name]

    def __getitem__(self, name):
        if name not in self.cols:
            self.cols[name] = MockedCollection(self, name)
        return self.cols[name]

    def __eq__(self, other):
        return isinstance(other, MockedDB) and self.name == other.name

    def __repr__(self):
        return "<%s name=%s>" % (self.__class__.__name__, self.name)


class MockedBuilder(BaseBuilder):

    BASE_DOCUMENT_CLS = DocumentImplementation

    @staticmethod
    def is_compatible_with(db):
        return isinstance(db, MockedDB)


register_builder(MockedBuilder)


class MockedInstance(LazyLoaderInstance):
    BUILDER_CLS = MockedBuilder


class BaseTest:

    def setup(self):
        self.instance = Instance(MockedDB('my_moked_db'))


class BaseDBTest:

    def setup(self):
        con.drop_database(TEST_DB)
