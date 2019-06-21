#
# from: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/secrets-manager.html#example
# modified by: Alain Ivars
#

import boto3
from botocore.exceptions import ClientError


def get_aws_secret(region_name, secret_name):
    """
    Get Aws secret
    :param region_name:
    :param secret_name:
    :return:
    """
    endpoint_url = "https://secretsmanager." + \
                   region_name + ".amazonaws.com"

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name,
        endpoint_url=endpoint_url
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print("The requested secret " + secret_name + " was not found")
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            print("The request was invalid due to:", e)
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            print("The request had invalid params:", e)
    else:
        # Secrets Manager decrypts the secret value using the associated KMS CMK
        # Depending on whether the secret was a string or binary,
        # only one of these fields will be populated
        # if 'SecretString' in get_secret_value_response:
        #     text_secret_data = get_secret_value_response['SecretString']
        # else:
        #     binary_secret_data = get_secret_value_response['SecretBinary']

        # Your code goes here.
        return get_secret_value_response
        # APPNAME_USERNAME_PASSWD = get_secret_value_response.get(
        #     'APPNAME_USERNAME_PASSWD')
        # default_value = hashing.hash_value(
        #     "the hash of something impossible to discover")
        # USERS["my_user"] = APPNAME_USERNAME_PASSWD if APPNAME_USERNAME_PASSWD \
        #     else os.getenv('APPNAME_USERNAME_PASSWD', default_value)
