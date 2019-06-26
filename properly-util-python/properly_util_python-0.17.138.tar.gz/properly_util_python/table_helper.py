import os

from properly_util_python.dynamo_helper import DynamoHelperBase, DynamoTestHelper

class TableHelper:

    TABLE_TEMPLATE = "{0}-{1}"

    OFFER_TABLE_NAME = "Offer-002"

    PROPERTY_TABLE_NAME = "Property-002"

    USER_TABLE_NAME = "User-002"

    META_TABLE_NAME = "Meta-001"

    HISTORICAL_RAW_NAME = "property-historical-clean-003"

    HISTORICAL_CLEAN_NAME = "property-historical-clean-003"

    def __init__(self, dynamo_helper: DynamoHelperBase):
        self.dynamo_helper = dynamo_helper

    def get_table_name(self, name):
        stage = os.environ.get('PROPERLY_STAGE')
        table_name = TableHelper.TABLE_TEMPLATE.format(stage, name)
        return table_name

    def get_table(self, name):
        table_name = self.get_table_name(name)
        helper = self.dynamo_helper
        dynamodb = helper.get_dynamo_db()
        table = dynamodb.Table(table_name)
        return table


    def build_tables_for_test(self):

        if (not isinstance(self.dynamo_helper, DynamoTestHelper)):
            # do not build tables if it is prod. a safety check
            return

        ddb = self.dynamo_helper.get_dynamo_db()

        table_name = self.get_table_name(TableHelper.META_TABLE_NAME)
        ddb.create_table(
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                },
            ],
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            },
        )
        table_name = self.get_table_name(TableHelper.OFFER_TABLE_NAME)
        ddb.create_table(
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                },
            ],
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            },
        )

        table_name = self.get_table_name(TableHelper.PROPERTY_TABLE_NAME)
        ddb.create_table(
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'locationPlaceId',
                    'AttributeType': 'S'
                },
            ],
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'
                },
            ],

            GlobalSecondaryIndexes=[
                TableHelper.index_from_name_and_attribute('LocationPlaceIdIndex', 'locationPlaceId')
            ],

            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            },
        )

        table_name = self.get_table_name(TableHelper.USER_TABLE_NAME)
        ddb.create_table(
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'authIdCognito',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'unverifiedEmail',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'verifiedEmail',
                    'AttributeType': 'S'
                },
            ],
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'
                },
            ],

            GlobalSecondaryIndexes=[
                TableHelper.index_from_name_and_attribute('authIdCognito-index', 'authIdCognito'),
                TableHelper.index_from_name_and_attribute('unverifiedEmail-index', 'unverifiedEmail'),
                TableHelper.index_from_name_and_attribute('verifiedEmail-index', 'verifiedEmail'),
            ],

            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            },
        )


    @classmethod
    def index_from_name_and_attribute(cls, name: str, attribute: str):
        return_val = {
                        'IndexName': name,
                        'KeySchema': [
                            {
                                'AttributeName': attribute,
                                'KeyType': 'HASH'
                            },
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL',
                        },
                        'ProvisionedThroughput': {
                            'ReadCapacityUnits': 5,
                            'WriteCapacityUnits': 5
                        }
                    }
        return return_val



