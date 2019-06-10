import boto3
import json
import os


LOCALSTACK_DUMMY_AWS_ACCOUNT_ID = "123456789012"
LOCALSTACK_AWS_REGION = 'us-east-1'


def _fake_aws_credentials():
    return {
        'region_name': LOCALSTACK_AWS_REGION,
        'aws_access_key_id': 'dummy-access-key',
        'aws_secret_access_key': 'dummy-secret',
        'aws_session_token': 'dummy-token'
    }


def get_s3_client():
    s3_localstack_url = os.environ.get("S3_LOCALSTACK_URL", 'http://localstack:4572')
    return boto3.client(
        's3',
        endpoint_url=s3_localstack_url,
        **_fake_aws_credentials()
    )


def get_sns_client():
    sns_localstack_url = os.environ.get("SNS_LOCALSTACK_URL", 'http://localstack:4575')
    return boto3.client(
        'sns',
        endpoint_url=sns_localstack_url,
        **_fake_aws_credentials()
    )


def get_sqs_client():
    sqs_localstack_url = os.environ.get("SQS_LOCALSTACK_URL", 'http://localstack:4576')
    return boto3.client(
        'sqs',
        endpoint_url=sqs_localstack_url,
        **_fake_aws_credentials()
    )


def get_topic_arn(topic_name):
    return "arn:aws:sns:%s:%s:%s" \
            % (LOCALSTACK_AWS_REGION, LOCALSTACK_DUMMY_AWS_ACCOUNT_ID, topic_name)