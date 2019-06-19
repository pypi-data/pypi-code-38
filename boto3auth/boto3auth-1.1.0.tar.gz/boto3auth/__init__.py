#!/usr/bin/env python3
"""Main module for boto3auth."""

import boto3


class Boto3Auth:
    """Class for authentication to boto3."""

    def __init__(self, region='us-east-1',
                 account_id=False, role=False, sts=None):
        """Set initial properties."""
        self.account_id = account_id
        self.region = region
        self.role = role
        self.sts = sts

    def auth(self, resource, type='resource'):
        """Return client/service for selected resource."""
        sess = boto3.Session()
        if self.account_id and self.role:
            if not self.sts:
                self.creds()
            sess = boto3.Session(
                aws_access_key_id=self.sts['Credentials']['AccessKeyId'],
                aws_secret_access_key=self.sts['Credentials']
                                              ['SecretAccessKey'],
                aws_session_token=self.sts['Credentials']['SessionToken']
            )
        if type == 'client':
            return sess.client(resource, region_name=self.region)
        return sess.resource(resource, region_name=self.region)

    def creds(self):
        """Assume role into acccount and set credentials."""
        if not self.account_id or not self.role:
            return

        sts = boto3.client('sts')
        arn = 'arn:aws:iam::' + self.account_id + ':role/' + self.role
        self.sts = sts.assume_role(
            RoleArn=arn,
            RoleSessionName='boto3auth'
        )
