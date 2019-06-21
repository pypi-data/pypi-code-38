from unittest import TestCase, mock

import unittest

from utils2devops.aws.aws_lambda import list_lambda_function
from utils2devops.tests.aws_base import SingletonSession

functions_mock = {
    'ResponseMetadata': {
        'RequestId': '4077d71d-936b-11e9-91ae-0b5a911986a2',
        'HTTPStatusCode': 200,
        'HTTPHeaders': {
            'date': 'Thu, 20 Jun 2019 14:54:06 GMT',
            'content-type': 'application/json',
            'content-length': '755',
            'connection': 'keep-alive',
            'x-amzn-requestid': '4077d71d-936b-11e9-91ae-0b5a911986a2'
        },
        'RetryAttempts': 0
    },
    'Functions': [{
        'FunctionName': 'hf-al-s3-get-object',
        'FunctionArn': 'arn:aws:lambda:us-east-2:397270606208:function:hf-al-s3-get-object',
        'Runtime': 'python3.7',
        'Role': 'arn:aws:iam::397270606208:role/service-role/hf-role-s3-ro',
        'Handler': 'lambda_function.lambda_handler',
        'CodeSize': 566,
        'Description': 'An Amazon S3 trigger that retrieves metadata for the object that has been updated.',
        'Timeout': 3,
        'MemorySize': 128,
        'LastModified': '2019-06-20T09:08:10.964+0000',
        'CodeSha256': 'Wg0ZsXe2tOdL+IBvvNe0JrZpkKKFgRDA1aE4BN6Xr7E=',
        'Version': '$LATEST',
        'TracingConfig': {
            'Mode': 'PassThrough'
        },
        'RevisionId': 'd471c835-6bb0-44cb-b542-9af4cacc7984'
    }]
}
conf_mock = {
    'ResponseMetadata': {
        'RequestId': '5e6c7294-936b-11e9-a565-f92e534a48b2',
        'HTTPStatusCode': 200,
        'HTTPHeaders': {
            'date': 'Thu, 20 Jun 2019 14:54:56 GMT',
            'content-type': 'application/json',
            'content-length': '2451',
            'connection': 'keep-alive',
            'x-amzn-requestid': '5e6c7294-936b-11e9-a565-f92e534a48b2'
        },
        'RetryAttempts': 0
    }, 'Configuration': {
        'FunctionName': 'hf-al-s3-get-object',
        'FunctionArn': 'arn:aws:lambda:us-east-2:397270606208:function:hf-al-s3-get-object',
        'Runtime': 'python3.7',
        'Role': 'arn:aws:iam::397270606208:role/service-role/hf-role-s3-ro',
        'Handler': 'lambda_function.lambda_handler',
        'CodeSize': 566,
        'Description': 'An Amazon S3 trigger that retrieves metadata for the object that has been updated.',
        'Timeout': 3,
        'MemorySize': 128,
        'LastModified': '2019-06-20T09:08:10.964+0000',
        'CodeSha256': 'Wg0ZsXe2tOdL+IBvvNe0JrZpkKKFgRDA1aE4BN6Xr7E=',
        'Version': '$LATEST',
        'TracingConfig': {
            'Mode': 'PassThrough'
        },
        'RevisionId': 'd471c835-6bb0-44cb-b542-9af4cacc7984'
    }, 'Code': {
        'RepositoryType': 'S3',
        'Location': 'https://awslambda-us-east-2-tasks.s3.us-east-2.amazonaws.com/snapshots'
    }, 'Tags': {
        'lambda-console:blueprint': 's3-get-object-python'
    }
}
result = [
    'resource "aws_lambda_function" "hf-al-s3-get-object" {\n',
    '\tfunction_name = "hf-al-s3-get-object"\n',
    '\thandler = "lambda_function.lambda_handler"\n',
    '\trole = "arn:aws:iam::397270606208:role/service-role/hf-role-s3-ro"\n',
    '\tdescription = "An Amazon S3 trigger that retrieves metadata for the object ',
    'that has been updated."\n',
    '\tmemory_size = "128"\n',
    '\truntime = "python3.7"\n',
    '\ttimeout = "3"\n',
    '\tsource_code_hash = "Wg0ZsXe2tOdL+IBvvNe0JrZpkKKFgRDA1aE4BN6Xr7E="\n',
    '\ttags {\n',
    '\t\t"lambda-console:blueprint" = "s3-get-object-python"\n',
    '\t}\n',
    '}\n',
]
expected_result = ''.join(result)

"""
for future add of feature:
input data from AWS
list_aliases
list_event_source_mappings
list_layers
list_tags
"lambda-console:blueprint"
list_versions_by_function
{
    "CodeSha256": "Wg0ZsXe2tOdL+IBvvNe0JrZpkKKFgRDA1aE4BN6Xr7E=",
    "CodeSize": 566,
    "Description": "An Amazon S3 trigger that retrieves metadata for the object that has been updated.",
    "FunctionArn": "arn:aws:lambda:us-east-2:397270606208:function:hf-al-s3-get-object:$LATEST",
    "FunctionName": "hf-al-s3-get-object",
    "Handler": "lambda_function.lambda_handler",
    "LastModified": "2019-06-20T09:08:10.964+0000",
    "MemorySize": 128,
    "RevisionId": "d471c835-6bb0-44cb-b542-9af4cacc7984",
    "Role": "arn:aws:iam::397270606208:role/service-role/hf-role-s3-ro",
    "Runtime": "python3.7",
    "Timeout": 3,
    "TracingConfig": {
        "Mode": "PassThrough"
    },
    "Version": "$LATEST"
}
"""


class AwsLambdaTestCase(TestCase):
    @mock.patch('boto3.Session', SingletonSession)
    def test_list_lambda_nominal(self):
        # nominal
        profile_name = 'test'
        region_name = 'us-east-2'
        session = SingletonSession(profile_name=profile_name)
        client = session.client(service_name='lambda', region_name=region_name)
        client.lambda_functions = functions_mock
        client.lambda_conf = conf_mock
        ls = list_lambda_function(profile_name, region_name)
        self.assertEqual(expected_result, str(ls[0]))


if __name__ == '__main__':
    unittest.main()
