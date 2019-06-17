from uuid import uuid4, UUID

from bson import Binary, binary
from cocktail_apikit import DictMongoQueryBuilder, MongoDBManager


def test_dict_mongo_query_builder(demo_schema):
    id_value = str(uuid4())
    query_dict = {'name__eq': 'demo', 'id__ne': id_value}

    builder = DictMongoQueryBuilder(query_data=query_dict, schema=demo_schema)

    mongo_query = builder.to_mongo_query()

    print(mongo_query.to_dict())
    mongo_query_dict = mongo_query.to_dict()

    assert mongo_query_dict['name'] == {'$eq': 'demo'}
    assert mongo_query_dict['_id'] == {'$ne': Binary(UUID(id_value).bytes, binary.STANDARD)}

    for key in ['sort', 'projection', 'page', 'limit', 'skip']:
        assert key in mongo_query_dict


def test__mongo_db_manager__caching_connection_ok(mongo_uri):
    config1 = {'MONGODB_URI': mongo_uri, 'DB_NAME': 'testDB', 'COLLECTION_NAME': 'demos'}
    config2 = {'MONGODB_URI': mongo_uri, 'DB_NAME': 'testDB', 'COLLECTION_NAME': 'demos2'}
    config3 = {'MONGODB_URI': mongo_uri, 'DB_NAME': 'testDB', 'COLLECTION_NAME': 'demos3'}
    db1 = MongoDBManager(config1)
    db2 = MongoDBManager(config2)
    db3 = MongoDBManager(config3)

    assert db1.CLIENTS == db2.CLIENTS == db3.CLIENTS
    assert len(db1.CLIENTS) == len(db2.CLIENTS) == len(db3.CLIENTS) == 1
    assert db1.collection.name == 'demos'
    assert db2.collection.name == 'demos2'
    assert db3.collection.name == 'demos3'
