"""
Summary.

    S3 put object Class

"""

import boto3
from botocore.exceptions import ClientError
from pyaws.session import boto3_session
from pyaws import logger


class S3FileOperations():
    """
    Summary.

        put, delete, put-acl object operations in Amazon S3
    """

    def __init__(self, bucket, profile=None):
        self.client = boto3_session(service='s3', profile_name=profile)
        self.bucket = bucket

    def put_fileobject(self, key, file, bucket=self.bucket):
        r = self.client.put_object(
                Bucket=bucket, Key=key, Body=file
            )
        return r

    def put_object_acl(self, key, acl, bucket=self.bucket):
        r = self.client.put_object_acl(
                Bucket=bucket,
                Key=key,
                ACL=acl
            )
        return r
