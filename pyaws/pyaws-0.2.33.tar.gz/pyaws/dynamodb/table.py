
import boto3

# Get the service resource.
dynamodb = boto3.resource('dynamodb')


def create_dynamodb_table(tablename, keys, attributes):
    """
    Summary.

    Creates table with keys and attributes

    Args:
        :keys (list):  List of dictionaries specifying hash, range
        :attributes (list): List of dictionaries specifying table attributes

    Returns:
        table name (str)
    """
    # Create the DynamoDB table.
    table = dynamodb.create_table(
        TableName='users',
        KeySchema=[
            {
                'AttributeName': 'username',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'last_name',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'username',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'last_name',
                'AttributeType': 'S'
            },

        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
