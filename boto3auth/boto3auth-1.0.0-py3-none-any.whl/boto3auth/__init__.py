#!/usr/bin/env python3
"""Main module for boto3auth."""

import boto3


def auth(resource, type='resource', region='us-east-1',
         account_id=False, role=False):
    """Return client/service for selected resource."""
    sess = boto3.Session()
    if account_id and role:
        sts = boto3.client('sts')
        creds = sts.assume_role(
            RoleArn=role,
            RoleSessionName='boto3auth',
        )
        sess = boto3.Session(
            aws_access_key_id=creds['Credentials']['AccessKeyId'],
            aws_secret_access_key=creds['Credentials']['SecretAccessKey'],
            aws_session_token=creds['Credentials']['SessionToken']
        )
    if type == 'client':
        return sess.client(resource, region_name=region)
    return sess.resource(resource, region_name=region)
