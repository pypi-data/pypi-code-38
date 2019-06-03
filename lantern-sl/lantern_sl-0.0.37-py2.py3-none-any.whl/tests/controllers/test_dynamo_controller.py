import botocore
import boto3
import pytest
from lantern_sl.controllers.dynamo_controller import (
    DynamoController, get_dynamo_connection, 
    ExceptionInvalidDynamoControllerNotFound)


def eq(a, b):
    for k in a.keys():
        if a.get(k) != b.get(k):
            return False
    for k in b.keys():
        if a.get(k) != b.get(k):
            return False
    return True


class TestDynamoController:
    TABLE_NAME = "test-dynamo-controller"
    controller = DynamoController(TABLE_NAME)
    dynamodb = get_dynamo_connection(force_local=True)

    def setup(self):
        # Create table if it doesnt exist
        try:
            self.dynamodb.create_table(
                TableName=self.TABLE_NAME,
                KeySchema=[{ 'AttributeName': 'id', 'KeyType': 'HASH'}],
                AttributeDefinitions=[{ 'AttributeName': 'id', 'AttributeType': 'S' }, { 'AttributeName': 'username', 'AttributeType': 'S' }],
                ProvisionedThroughput={ 'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5 },
                GlobalSecondaryIndexes=[
                    {'IndexName': 'username-index', 'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {'WriteCapacityUnits': 5, 'ReadCapacityUnits': 5},
                    'KeySchema': [{'KeyType': 'HASH', 'AttributeName': 'username'}]}])
        except Exception as e:
            if('ResourceInUseException' in str(e)):
                pass
            else:
                raise e


    @pytest.mark.parametrize("data, id, expected", [
        ({"first_name": "Armando", "age": 25}, "", False),
        ({"first_name": "Armando", "age": 25}, "1", True),
        ({"first_name": "Arturo", "age": 35}, "2", True),
    ])
    def test_create(self, data, id, expected):
        self.setup()
        try:
            data["id"] = id
            created = self.controller.create(data)
            if expected:
                assert eq(data, created), "Item Created!"
            else:
                assert not eq(data, created), "Item not created"
        except Exception as e:
            if expected:
                raise e
            else:
                assert True, "It was expected to fail"

    @pytest.mark.parametrize("data, id, expected", [
        ({"first_name": "Armando", "age": 25}, "10", True),
        ({"first_name": "Arturo", "age": 35}, "20", True),
    ])
    def test_get(self, data, id, expected):
        self.setup()
        try:
            data["id"] = id
            created = self.controller.create(data)
            item = self.controller.get(primary_keys={"id": id})
            if expected:
                assert eq(item, data), "Item Fetched!"
            else:
                assert not eq(item, data), "Item not Fetched"
        except Exception as e:
            if expected:
                raise e
            else:
                assert True, "It was expected to fail"
    
    @pytest.mark.parametrize("data, update_data, id, expected", [
        ({"first_name": "Armando", "age": 25}, {"first_name": "Juan"}, "100", True),
        ({"first_name": "Arturo", "age": 35}, {"age": 33},"200", True),
    ])
    def test_update(self, data, update_data, id, expected):
        self.setup()
        try:
            data["id"] = id
            created = self.controller.create(data)
            for k in update_data.keys():
                created[k] = update_data[k]
            del created["id"]
            updated = self.controller.update(primary_keys={"id": id}, data=created)
            del updated["id"]
            if expected:
                assert eq(created, updated), "Item Updated"
            else:
                assert eq(created, updated), "Item Not Updated"
        except Exception as e:
            if expected:
                raise e
            else:
                assert True, "It was expected to fail"


    @pytest.mark.parametrize("data, id, expected", [
        ({"first_name": "Armando", "age": 25},  "1000", True),
        ({"first_name": "Armando", "age": 25},  "2000", True),
    ])
    def test_delete(self, data, id, expected):
        self.setup()
        try:
            data["id"] = id
            created = self.controller.create(data)
            item = self.controller.get(primary_keys={"id": id})
            self.controller.delete(primary_keys={"id": id})
            try:
                item = self.controller.get(primary_keys={"id": id})
                assert False, "Item should be deleted"
            except ExceptionInvalidDynamoControllerNotFound as e:
                if expected:
                    assert True, "Element was deleted"
                else:
                    raise e
        except Exception as e:
            if expected:
                raise e
            else:
                assert True, "It was expected to fail"

    FILTERING_DATA = [
        {"first_name": "Armando", "age": 10, "username": "u1"},
        {"first_name": "Armando Juan", "age": 20, "username": "u1"},
        {"first_name": "Juan", "age": 30, "username": "u2"},
        {"first_name": "Rogelio", "age": 40, "username": "u2"}]

    @pytest.mark.parametrize("data_set, key, value, order_by, limit, next, index, order_type, filter_expression, expected_count", [
        (FILTERING_DATA, "username", "u1", None, 50, None, None, DynamoController.ORDER_DESC, None, 2),
        (FILTERING_DATA, "username", "u2", None, 50, None, None, DynamoController.ORDER_DESC, None, 2),
        (FILTERING_DATA, "username", "u2", None, 1, None, None, DynamoController.ORDER_DESC, None, 1),
    ])
    def test_filter(self, data_set, key, value, order_by, limit, next, index, order_type, filter_expression, expected_count):
        self.setup()
        for i, data in enumerate(data_set):
            data["id"] = '{}'.format((i + 1) * 10000)
            self.controller.create(data)
        res, count, next = self.controller.filter(
            key=key, value=value, order_by=order_by, 
            limit=limit, next=next, index=index, order_type=order_by, 
            filter_expression=filter_expression)
        assert count == expected_count