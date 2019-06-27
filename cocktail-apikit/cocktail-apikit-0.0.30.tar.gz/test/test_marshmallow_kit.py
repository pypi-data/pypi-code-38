import random
import string
import uuid

from bson import Binary
from bson.binary import STANDARD


def test_schema_mongo_valid_fields(demo_schema):
    valid_mongo_query_fields = demo_schema.valid_mongo_query_fields()
    assert len(valid_mongo_query_fields) == 8


def test_decimal_timestamp_deserialize(demo_schema, valid_decimal_timestamp, valid_datetime_string):
    input_data = {
        'name': 'demo',
        'ts': valid_datetime_string
    }
    loaded_data, errors = demo_schema.load(input_data)
    assert errors == {}
    assert loaded_data['ts'] == valid_decimal_timestamp


def test_decimal_timestamp_serialize(demo_schema, valid_decimal_timestamp, valid_datetime_string):
    input_data = {
        'name': 'demo',
        'ts': valid_decimal_timestamp
    }
    dumped_data, errors = demo_schema.dump(input_data)
    assert errors == {}
    assert dumped_data['ts'] == valid_datetime_string


def test_mongo_uuid_field_deserialize_serialize(demo_schema):
    raw_data = {
        'name': 'test',
        'mongo_uuid': None
    }

    ############################################################
    # Test a valid None value
    ############################################################
    loaded_data, error = demo_schema.load(raw_data)

    assert not error
    assert loaded_data['mongo_uuid'] is None

    dumped_data, error = demo_schema.dump(loaded_data)
    assert not error
    assert dumped_data['mongo_uuid'] is None

    ############################################################
    # Test a valid uuid string
    ############################################################
    raw_data['mongo_uuid'] = uuid.uuid4().hex

    print(raw_data)
    loaded_data2, error = demo_schema.load(raw_data)

    assert not error
    assert isinstance(loaded_data2['mongo_uuid'], Binary) and loaded_data2['mongo_uuid'].subtype == STANDARD

    dumped_data2, error = demo_schema.dump(loaded_data2)
    assert not error
    assert isinstance(dumped_data2['mongo_uuid'], str) and dumped_data2['mongo_uuid'].replace('-', '') == raw_data[
        'mongo_uuid']

    ############################################################
    # Test an invalid value
    ############################################################
    raw_data['mongo_uuid'] = ''.join(random.sample(string.ascii_letters, random.randint(1, 31)))
    loaded_data3, error = demo_schema.load(raw_data)
    assert 'mongo_uuid' in error


def test_schema_load_without_id_will_auto_create_ok(demo_schema):
    """
    Mock creation case when create object no need to specify id field 
    """
    payload = {
        'name': 'test'
    }

    loaded_data, error = demo_schema.load(payload)
    assert not error
    assert '_id' in loaded_data


def test_schema_load_with_id_will_keep_the_same_value_ok(demo_schema):
    """
    Mock update case when update object which may contain nested object with id field
    this case keep the orignal id field value instead of create a new one
    """

    payload = {
        'name': 'test',
        'id': uuid.uuid4().hex  
    }
    loaded_data1, error = demo_schema.load(payload)
    assert not error
    assert '_id' in loaded_data1

    payload['_id'] = payload.pop('id')  # Test a rare case 
    loaded_data2, error = demo_schema.load(payload)
    assert not error
    assert '_id' in loaded_data2

    assert isinstance(loaded_data1['_id'], Binary) 
    assert isinstance(loaded_data2['_id'], Binary) 
    assert loaded_data1['_id'] == loaded_data2['_id']


def test_schema_load_with_empty_id_value_ok(demo_schema):
    payload = {
        'name': 'test',
        'id': ''
    }
    loaded_data, error = demo_schema.load(payload)

    assert not error

    assert '_id' in loaded_data and isinstance(loaded_data['_id'], Binary) and loaded_data['_id'].subtype == STANDARD


def test_schema_load_with_invalid_uuid_as_id_value_fail(demo_schema):
    payload = {
        'name': 'teset',
        'id': 'any invalid uuid value'
    }
    loaded_data, error = demo_schema.load(payload)
    assert 'id' in error and 'Not a valid UUID.' in error['id']
