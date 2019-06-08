import json
import logging
import os

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
script_dir = os.path.dirname(__file__)


class S3Service(object):
    """
    S3 handler to perform S3 related operations
    """

    def __init__(self, profile_name="default", region="us-west-2"):
        self._s3_session = boto3.Session(profile_name=profile_name)
        self._s3_client = self._s3_session.client("s3", region_name=region)
        self._s3_resource = self._s3_session.resource("s3", region_name=region)
        self._region = region

    def create_bucket(self, bucket):
        """
        Create a new bucket in the AWS account

        :param bucket: name of the bucket
        :return: bucket name that is created
        """
        try:
            if self._region == "us-east-1":
                response = self._s3_client.create_bucket(ACL="private", Bucket=bucket)
            else:
                response = self._s3_client.create_bucket(ACL="private", Bucket=bucket,
                                                         CreateBucketConfiguration={"LocationConstraint": self._region})
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                logger.info("BUCKET {0} CREATED".format(bucket))
            return bucket
        except Exception as exception:
            logger.exception(exception)

    def is_bucket_present(self, bucket):
        """
        Check if the bucket exists or not

        :param bucket: bucket name
        :return:
        """
        try:
            self._s3_client.head_bucket(
                Bucket=bucket
            )
            return True
        except ClientError:
            return False

    @staticmethod
    def generate_website_hosting_policy(s3_bucket_name):
        """
        Generate the website hosting policy for the S3 hosting

        :param s3_bucket_name: name of the bucket to be loaded into the policy
        :return: bucket policy data
        """
        policy_file_path = "../resources/s3_policy.json"
        policy_file_abs_path = os.path.join(script_dir, policy_file_path)
        policy_json = open(policy_file_abs_path)
        data = json.load(policy_json)
        data['Statement'][0]['Resource'] = data['Statement'][0]['Resource'].format(s3_bucket_name)
        data = json.dumps(data)
        print(data)
        return data

