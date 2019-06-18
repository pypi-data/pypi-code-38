from stackifyapm.instrumentation.packages.base import AbstractInstrumentedModule
from stackifyapm.traces import CaptureSpan
from stackifyapm.utils.helper import is_async_span


class PyMongoInstrumentation(AbstractInstrumentedModule):
    name = "pymongo"

    instrument_list = [
        ("pymongo.collection", "Collection.aggregate"),
        ("pymongo.collection", "Collection.bulk_write"),
        ("pymongo.collection", "Collection.count"),
        ("pymongo.collection", "Collection.create_index"),
        ("pymongo.collection", "Collection.create_indexes"),
        ("pymongo.collection", "Collection.delete_many"),
        ("pymongo.collection", "Collection.delete_one"),
        ("pymongo.collection", "Collection.distinct"),
        ("pymongo.collection", "Collection.drop"),
        ("pymongo.collection", "Collection.drop_index"),
        ("pymongo.collection", "Collection.drop_indexes"),
        ("pymongo.collection", "Collection.ensure_index"),
        ("pymongo.collection", "Collection.estimated_document_count"),
        ("pymongo.collection", "Collection.find"),
        ("pymongo.collection", "Collection.find_and_modify"),
        ("pymongo.collection", "Collection.find_one"),
        ("pymongo.collection", "Collection.find_one_and_delete"),
        ("pymongo.collection", "Collection.find_one_and_replace"),
        ("pymongo.collection", "Collection.find_one_and_update"),
        ("pymongo.collection", "Collection.group"),
        ("pymongo.collection", "Collection.inline_map_reduce"),
        ("pymongo.collection", "Collection.insert"),
        ("pymongo.collection", "Collection.insert_many"),
        ("pymongo.collection", "Collection.insert_one"),
        ("pymongo.collection", "Collection.map_reduce"),
        ("pymongo.collection", "Collection.reindex"),
        ("pymongo.collection", "Collection.remove"),
        ("pymongo.collection", "Collection.rename"),
        ("pymongo.collection", "Collection.replace_one"),
        ("pymongo.collection", "Collection.save"),
        ("pymongo.collection", "Collection.update"),
        ("pymongo.collection", "Collection.update_many"),
        ("pymongo.collection", "Collection.update_one"),
    ]

    def call(self, module, method, wrapped, instance, args, kwargs):
        cls_name, method_name = method.split(".", 1)
        signature = ".".join([instance.full_name, method_name])
        collection = instance.collection
        extra_data = {
            "wrapped_method": 'Execute',
            "provider": self.name,
            "type": "MongoDB",
            "sub_type": "database_sql",
            "collection": collection.full_name,
            "operation": method_name,
        }
        with CaptureSpan(signature, "db.mongodb.query", extra_data, leaf=True, is_async=is_async_span()):
            return wrapped(*args, **kwargs)


class PyMongoBulkInstrumentation(AbstractInstrumentedModule):
    name = "pymongo"

    instrument_list = [("pymongo.bulk", "BulkOperationBuilder.execute")]

    def call(self, module, method, wrapped, instance, args, kwargs):
        collection = instance._BulkOperationBuilder__bulk.collection
        signature = ".".join([collection.full_name, "bulk.execute"])
        extra_data = {
            "wrapped_method": 'Execute',
            "provider": self.name,
            "type": "MongoDB",
            "sub_type": "database_sql",
            "collection": collection.full_name,
            "operation": "bulk.execute",
        }
        with CaptureSpan(signature, "db.mongodb.query", extra_data, is_async=is_async_span()):
            return wrapped(*args, **kwargs)


class PyMongoCursorInstrumentation(AbstractInstrumentedModule):
    name = "pymongo"

    instrument_list = [("pymongo.cursor", "Cursor._refresh")]

    def call(self, module, method, wrapped, instance, args, kwargs):
        collection = instance.collection
        signature = ".".join([collection.full_name, "cursor.refresh"])
        extra_data = {
            "wrapped_method": 'Execute',
            "provider": self.name,
            "type": "MongoDB",
            "sub_type": "database_sql",
            "collection": collection.full_name,
            "row_count": instance.count(),
            "operation": "cursor.refresh",
        }
        with CaptureSpan(signature, "db.mongodb.query", extra_data, is_async=is_async_span()):
            return wrapped(*args, **kwargs)
