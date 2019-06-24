from typedconfig_awssource import IniS3ConfigSource, DynamoDbConfigSource, SecretsManagerConfigSource
import os
import boto3
import botocore.exceptions
from moto import mock_s3, mock_dynamodb2, mock_secretsmanager
from unittest.mock import patch
import pytest
from typedconfig.source import ConfigSource
from typedconfig_awssource.__version__ import __version__


# Note - patching these credentials is a workaround until another release of moto is made
aws_cred_patch = patch.dict(os.environ, {
    "AWS_ACCESS_KEY_ID": "foobar_key",
    "AWS_SECRET_ACCESS_KEY": "foobar_secret",
    "AWS_DEFAULT_REGION": 'eu-west-1'
})


def do_assertions(source: ConfigSource):
    v = source.get_config_value('s', 'a')
    assert '1' == v

    v = source.get_config_value('t', 'a')
    assert v is None

    v = source.get_config_value('s', 'c')
    assert v is None


@mock_secretsmanager
@aws_cred_patch
def test_secrets_manager_config_source():
    client = boto3.client('secretsmanager')
    client.create_secret(
        Name='project/s',
        SecretString='{"a": "1"}'
    )

    source = SecretsManagerConfigSource(secret_name_prefix='project')
    do_assertions(source)


@mock_s3
@aws_cred_patch
def test_ini_s3_config_source():
    client = boto3.client('s3')
    client.create_bucket(Bucket='test-bucket')
    client.put_object(Bucket='test-bucket', Key='test-key', Body="""
[s]
a = 1
""")

    source = IniS3ConfigSource('test-bucket', 'test-key')
    do_assertions(source)


@mock_s3
@aws_cred_patch
def test_ini_s3_config_source_no_bucket_must_exist_false():
    source = IniS3ConfigSource('test-bucket', 'test-key', must_exist=False)
    v = source.get_config_value('s', 'a')
    assert v is None


@mock_s3
@aws_cred_patch
def test_ini_s3_config_source_no_bucket_must_exist_true():
    with pytest.raises(botocore.exceptions.ClientError):
        source = IniS3ConfigSource('test-bucket', 'test-key', must_exist=True)


@mock_dynamodb2
@aws_cred_patch
def test_dynamodb_config_source():
    client = boto3.client('dynamodb')
    client.create_table(
        TableName='test-table',
        AttributeDefinitions=[
            {
                'AttributeName': 'section',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'key',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'value',
                'AttributeType': 'S'
            }
        ],
        KeySchema=[
            {
                'AttributeName': 'section',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'key',
                'KeyType': 'RANGE'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )

    client.put_item(
        TableName='test-table',
        Item={
            'section': {
                'S': 's'
            },
            'key': {
                'S': 'a'
            },
            'value': {
                'S': '1'
            }
        }
    )

    source = DynamoDbConfigSource(
        table_name='test-table',
        section_attribute_name='section',
        key_attribute_name='key',
        value_attribute_name='value')

    do_assertions(source)


def test_version():
    assert type(__version__) is str
