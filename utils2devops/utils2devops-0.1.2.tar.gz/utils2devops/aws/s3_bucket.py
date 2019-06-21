import boto3

from utils2devops.aws import S3Bucket

"""
Aws configuration iiles should be present:
 ~/.aws/credentials
 ~/.aws/config
"""


def list_s3_bucket(profile_name: str = 'terraform',
                   region_name: str = 'us-east-2') -> [str]:
    """This function list all AWS S3 bucket how can access the profile
    profile_name in the AWS region region_name.

    :param profile_name: The AWS profile name to use.
    :param region_name: The AWS region to use.
    :returns: list of line or empty if nothing.
    :raises: AttributeError, KeyError

    """
    session = boto3.Session(profile_name=profile_name)
    client = session.client(service_name='s3', region_name=region_name)
    resource = boto3.resource(service_name='s3', region_name=region_name)
    functions = client.list_buckets()

    _lines = []
    if 'Buckets' not in functions:
        return _lines
    for func in functions['Buckets']:
        x = S3Bucket(func['Name'])
        x.bucket = func['Name']
        acl = client.get_public_access_block(Bucket=func['Name'])
        # TODO: just a first empty draft, to implement
        x.acl = 'private' \
            if acl['PublicAccessBlockConfiguration']['BlockPublicAcls'] \
            else ''
        conf = resource.BucketVersioning(func["Name"])
        x.versioning = 'true' if conf.status == 'Enabled' else 'false'

        _lines.append(x)

    return _lines


if __name__ == '__main__':
    lines = list_s3_bucket()
    print(*lines)
