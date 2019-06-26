#!/usr/bin/env python3

def authenticated_s3(profile):
    """
    Summary:
        Tests authentication status to AWS Account using s3
    Args:
        :profile (str): iam user name from local awscli configuration
    Returns:
        TYPE: bool, True (Authenticated)| False (Unauthenticated)
    """
    try:
        s3_client = boto3_session(service='s3', profile=profile)
        httpstatus = s3_client.list_buckets()['ResponseMetadata']['HTTPStatusCode']
        if httpstatus == 200:
            return True
    except Exception:
        return False
    return False
