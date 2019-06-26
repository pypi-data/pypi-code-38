
import boto3
import os


class DynamoHelperBase:

    def get_dynamo_db(self):
        raise NotImplementedError()


class DynamoHelper(DynamoHelperBase):

    def get_dynamo_db(self):
        dynamodb = boto3.resource('dynamodb' )
        return dynamodb


class DynamoTestHelper(DynamoHelperBase):

    def get_dynamo_db(self):
        dynamo_alternate_endpoint = "http://localhost:8008"
        dynamodb = boto3.resource('dynamodb', endpoint_url=dynamo_alternate_endpoint, region_name="us-west-1")
        return dynamodb


class EnvironmentControlledDynamoHelper(DynamoHelperBase):

    def __init__(self):
        self.dynamo_helper = DynamoHelper()
        self.test_dynamo_helper = DynamoTestHelper()

    def get_dynamo_db(self):
        use_test_env_flag = os.environ.get('PROPERLY_USE_LOCAL_DYNAMO', None)
        if (use_test_env_flag is None):
            return self.dynamo_helper.get_dynamo_db()
        else:
            return self.test_dynamo_helper.get_dynamo_db()


