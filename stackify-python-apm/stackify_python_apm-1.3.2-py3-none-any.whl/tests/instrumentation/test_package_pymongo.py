import pymongo

from unittest import TestCase

from stackifyapm.base import Client
from stackifyapm.traces import get_transaction
from stackifyapm.traces import set_transaction
from stackifyapm.traces import Transaction
from stackifyapm.instrumentation import register
from stackifyapm.instrumentation import control
from stackifyapm.instrumentation.packages.pymongo import PyMongoCursorInstrumentation

CONFIG = {
    "SERVICE_NAME": "service_name",
    "ENVIRONMENT": "production",
    "HOSTNAME": "sample_host",
    "FRAMEWORK_NAME": "framework",
    "FRAMEWORK_VERSION": "1.0",
    "APPLICATION_NAME": "sample_application",
    "BASE_DIR": "path/to/application/",
}


class PyMongoInstrumentationTest(TestCase):
    def setUp(self):
        self.client = Client(CONFIG)
        register._cls_registers = {
            "stackifyapm.instrumentation.packages.pymongo.PyMongoBulkInstrumentation",
            "stackifyapm.instrumentation.packages.pymongo.PyMongoCursorInstrumentation",
            "stackifyapm.instrumentation.packages.pymongo.PyMongoInstrumentation",
        }

        params = {
            "host": "127.0.0.1",
            "port": 1113,
            "serverSelectionTimeoutMS": 10,
        }
        if pymongo.version_tuple < (3, 0):
            params["safe"] = True

        self.mongo = pymongo.MongoClient(**params)
        self.database = self.mongo.stackifydb

    def tearDown(self):
        control.uninstrument()
        self.mongo.drop_database("stackifydb")
        self.mongo.close()

    def bulk_write(self):
        self.database.test.bulk_write([
            pymongo.InsertOne({"foo": 1}),
            pymongo.InsertOne({"bar": 2}),
        ])

    def test_collection_bulk_write(self):
        control.instrument()
        self.client.begin_transaction("transaction_test")

        self.bulk_write()

        assert_span(operation='bulk_write', collection='stackifydb.test.collection')

    def test_collection_count(self):
        self.bulk_write()
        control.instrument()
        self.client.begin_transaction("transaction_test")

        count = self.database.test.estimated_document_count()
        assert count == 2
        assert_span(operation='estimated_document_count', collection='stackifydb.test.collection')

    def test_collection_delete_one(self):
        self.bulk_write()
        control.instrument()
        self.client.begin_transaction("transaction_test")

        self.database.test.delete_one({"foo": 1})

        assert_span(operation='delete_one', collection='stackifydb.test.collection')

    def test_collection_update_one(self):
        self.bulk_write()
        control.instrument()
        self.client.begin_transaction("transaction_test")

        self.database.test.update_one({"foo": 1}, {"$set": {"foo": 3}})

        assert_span(operation='update_one', collection='stackifydb.test.collection')

    def test_collection_update_many(self):
        self.bulk_write()
        control.instrument()
        self.client.begin_transaction("transaction_test")

        self.database.test.update_many({"foo": 1}, {"$set": {"foo": 3}})

        assert_span(operation='update_many', collection='stackifydb.test.collection')

    def test_collection_delete_many(self):
        self.bulk_write()
        control.instrument()
        self.client.begin_transaction("transaction_test")

        self.database.test.delete_many({"foo": 1})

        assert_span(operation='delete_many', collection='stackifydb.test.collection')

    def test_collection_insert(self):
        control.instrument()
        self.client.begin_transaction("transaction_test")

        self.database.test.insert_one({"foo": 1})

        assert_span(operation='insert_one', collection='stackifydb.test.collection')

    def test_collection_insert_many(self):
        control.instrument()
        self.client.begin_transaction("transaction_test")

        self.database.test.insert_many([{"foo": 1}])

        assert_span(operation='insert_many', collection='stackifydb.test.collection')

    def test_collection_find(self):
        self.bulk_write()
        control.instrument()
        self.client.begin_transaction("transaction_test")

        self.database.test.find({"foo": 1})

        assert_span(operation='find', collection='stackifydb.test.collection')

    def test_bulk_execute(self):
        control.instrument()
        self.client.begin_transaction("transaction_test")

        bulk = self.database.test.initialize_ordered_bulk_op()
        bulk.insert({"foo": 1})
        bulk.insert({"bar": 1})
        bulk.execute()

        assert_span(operation='bulk.execute', collection='stackifydb.test')


class CollectionMock(object):
    full_name = 'some.collection'


class InstanceMock(object):
    collection = CollectionMock()

    def count(self):
        return 2


class PyMongoCursorInstrumentationTest(TestCase):
    def setUp(self):
        client = Client(CONFIG)
        transaction = Transaction("request", None, meta_data=client.get_meta_data())
        set_transaction(transaction)

    def tearDown(self):
        get_transaction(clear=True)

    def test_sample(self):
        instrument = PyMongoCursorInstrumentation()

        instrument.call(None, None, lambda *args, **kwrags: '', InstanceMock(), [], {})

        assert_span(operation='cursor.refresh', collection='some.collection')


def assert_span(operation, collection):
    transaction = get_transaction()
    assert transaction
    assert transaction.get_spans()

    span = transaction.get_spans()[0]
    span_data = span.to_dict()

    assert span_data['reqBegin']
    assert span_data['reqEnd']
    assert span_data['transaction_id']
    assert span_data['call'] == 'db.mongodb.query'
    assert span_data['props']
    assert span_data['props']['CATEGORY'] == 'MongoDB'
    assert span_data['props']['SUBCATEGORY'] == 'Execute'
    assert span_data['props']['COMPONENT_CATEGORY'] == 'DB Query'
    assert span_data['props']['COMPONENT_DETAIL'] == 'Execute SQL Query'
    assert span_data['props']['PROVIDER'] == 'pymongo'
    assert span_data['props']['MONGODB_COLLECTION'] == collection
    assert span_data['props']['OPERATION'] == operation
