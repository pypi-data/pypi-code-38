"""
Module containing AWS dependent configuration sources
"""
import boto3
import json
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Optional
from typedconfig.config import ConfigSource
from typedconfig.source import AbstractIniConfigSource
from configparser import ConfigParser


class DynamoDbConfigSource(ConfigSource):
    def __init__(self, table_name: str,
                 section_attribute_name: str='section',
                 key_attribute_name: str='key',
                 value_attribute_name: str='value'):
        self.table_name = table_name
        self.section_attribute_name = section_attribute_name
        self.key_attribute_name = key_attribute_name
        self.value_attribute_name = value_attribute_name
        self._client = boto3.client('dynamodb')

    def get_config_value(self, section_name: str, key_name: str) -> Optional[str]:
        response = self._client.get_item(
            TableName=self.table_name,
            Key={
                self.section_attribute_name: {
                    'S': section_name
                },
                self.key_attribute_name: {
                    'S': key_name
                }
            }
        )
        if 'Item' not in response:
            return None

        # Not this will error is the appropriate field are not found
        # inside 'Item'. This is expected behaviour since the table
        # has been set up wrongly if these things aren't present
        return response['Item'][self.value_attribute_name]['S']


class IniS3ConfigSource(AbstractIniConfigSource):
    def __init__(self, bucket: str, key: str, encoding: str='utf-8', must_exist=True):
        config = ConfigParser()

        try:
            s3 = boto3.resource('s3')
            obj = s3.Object(bucket, key)
            byte_string = obj.get()['Body'].read()
            decoded_string = byte_string.decode(encoding)
            config.read_string(decoded_string)
        except (ClientError, NoCredentialsError):
            if must_exist:
                raise
        super().__init__(config)


class SecretsManagerConfigSource(ConfigSource):
    def __init__(self, secret_name_prefix: str):
        assert type(secret_name_prefix) is str
        assert len(secret_name_prefix) > 0
        # Create a Secrets Manager client
        self._client = boto3.client('secretsmanager')
        self._secret_name_prefix = secret_name_prefix

    def get_config_value(self, section_name: str, key_name: str) -> Optional[str]:
        secret_name = self._secret_name_prefix + "/" + section_name
        try:
            response = self._client.get_secret_value(SecretId=secret_name)
        except self._client.exceptions.ResourceNotFoundException:
            return None

        section_contents = json.loads(response['SecretString'])
        return section_contents.get(key_name, None)
