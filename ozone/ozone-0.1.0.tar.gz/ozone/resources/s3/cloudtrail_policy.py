from troposphere import (
    Sub,
    Ref
)

from troposphere.s3 import BucketPolicy

from ozone.filters.arns import s3_bucket as filter_s3bucket
from ozone.resolvers.organizations import (
    find_org_in_tree,
    get_ou_accounts,
    get_all_accounts_in_ou_and_sub
)


def _cloudtrail_service_access_check(bucket_arn):
    statement = {
        "Sid": "AWSCloudTrailAclCheck",
        "Effect": "Allow",
        "Principal": {
            "Service": "cloudtrail.amazonaws.com"
        },
        "Action": "s3:GetBucketAcl",
        "Resource": bucket_arn
    }
    return statement


def _cloudtrail_arns(bucket, **kwargs):
    """
    Returns:
        trail_arns list() of the Resources to allow for CloudTrail
    """
    arns = []
    if 'AccountsIds' in kwargs.keys() and isinstance(kwargs['AccountsIds'], list):
        for account in kwargs['AccountsIds']:
            arns.append(Sub(f'${{{bucket.title}.Arn}}/AWSLogs/{account}/*'))
    elif 'OrganizationUnit' in kwargs.keys():
        ou_info = find_org_in_tree(kwargs['OrganizationUnit'])
        ou_accounts = []
        if 'OuAsRoot' in kwargs.keys() and kwargs['OuAsRoot']:
            ou_accounts_list = get_all_accounts_in_ou_and_sub(ou_info['Id'])
        else:
            ou_accounts_list = get_ou_accounts(ou_info['Id'])
        try:
            assert ou_accounts_list
        except AssertionError:
            raise ValueError(f'No accounts found for {ou_path}')
        for account in ou_accounts_list:
            arns.append(Sub(f'${{{bucket.title}.Arn}}/AWSLogs/{account["Id"]}/*'))
    return arns


def _cloudtrail_accounts_access(bucket, **kwargs):
    statement = {
        "Sid": "AWSCloudTrailWrite20131101",
        "Effect": "Allow",
        "Principal": {
            "Service": "cloudtrail.amazonaws.com"
        },
        "Action": "s3:PutObject",
        "Condition": {
            "StringEquals": {
                "s3:x-amz-acl": "bucket-owner-full-control"
            }
        }
    }
    #         "Resource": "arn:aws:s3:::trail-eu-west-1-ews-productone-prod/AWSLogs/406414658319/*",
    statement['Resource'] = _cloudtrail_arns(bucket, **kwargs)
    return statement


def _cloudtrail_bucket_policy(bucket, **kwargs):
    """
    Args:
        kwargs:
            AccountsIds: List of account Ids to grant access to aws logs path
            OrganizationUnit: str() of the OU name or Path
            OuAsRoot: bool() to define whethere all accounts in OU and sub OU should be used
    Returns:
        bucket_policy dict()
    """
    bucket_arn = filter_s3bucket(bucket)
    assert bucket_arn
    statement = []
    statement.append(_cloudtrail_service_access_check(bucket_arn))
    statement.append(_cloudtrail_accounts_access(bucket, **kwargs))
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": statement
    }
    return bucket_policy


def policy_build(bucket, **kwargs):
    """
    Args:
        kwargs:
            OrganizationUnit: str() of the OU name or Path
            OuAsRoot: bool() to define whethere all accounts in OU and sub OU should be used
    Returns:
        bucket_policy BucketPolicy()
    """
    bucket_policy = BucketPolicy(
        'BucketPolicy',
        Bucket=Ref(bucket),
        PolicyDocument=_cloudtrail_bucket_policy(bucket, **kwargs)
    )
    return bucket_policy

