def test_schema_mongo_valid_fields(demo_schema):
    valid_mongo_query_fields = demo_schema.valid_mongo_query_fields()
    assert len(valid_mongo_query_fields) == 7


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
