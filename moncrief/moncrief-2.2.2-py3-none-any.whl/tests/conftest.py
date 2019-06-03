import os

import boto3 as boto3
import pytest


@pytest.fixture
def lambda_environment():
    client = boto3.Session(profile_name='dev').client('sts')
    lambda_role = 'arn:aws:iam::726075243133:role/worker-leech-dev-2-Oyster-168YECYUUDQMK'
    response = client.assume_role(
        RoleArn=lambda_role,
        RoleSessionName='lambdaTest'
    )
    credentials = response['Credentials']
    os.environ['AWS_ACCESS_KEY_ID'] = credentials['AccessKeyId']
    os.environ['AWS_SECRET_ACCESS_KEY'] = credentials['SecretAccessKey']
    os.environ['AWS_SESSION_TOKEN'] = credentials['SessionToken']
