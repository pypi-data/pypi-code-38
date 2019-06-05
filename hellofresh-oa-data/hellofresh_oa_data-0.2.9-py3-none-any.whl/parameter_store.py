"""
    parameter_store.py

    Part of the hellofresh_data module meant to
    set up access to AWS' parameter store and
    return values based on the passed in key.
"""

import boto3
from botocore.errorfactory import ClientError

DEFAULT_REGION_NAME = 'us-east-2'

def get_parameter_store_value(for_key):
    """
        Return value for a passed in key
    """
    try:
        client = boto3.client('ssm', region_name=DEFAULT_REGION_NAME)

        response = client.get_parameter(
            Name=for_key,
            WithDecryption=True
        )
        return response.get('Parameter', {}).get('Value')
    except ClientError as err:
        print(err)
