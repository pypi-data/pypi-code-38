"""

cross_account_utils (python3)

    Common Secure Token Service (STS) functionality for use
    with AWS' Lambda Service

Author:
    Blake Huber
    Copyright Blake Huber, All Rights Reserved.

License:
    Permission to use, copy, modify, and distribute this software and its
    documentation for any purpose and without fee is hereby granted,
    provided that the above copyright notice appear in all copies and that
    both the copyright notice and this permission notice appear in
    supporting documentation

    Additional terms may be found in the complete license agreement:
    https://bitbucket.org/blakeca00/lambda-library-python/src/master/LICENSE.md

"""

import inspect
import boto3
from botocore.exceptions import ClientError
import loggers
from _version import __version__


# lambda custom log object
logger = loggers.getLogger(__version__)


class AssumeAWSRole():
    """ class def for assuming roles in AWS """
    def __init__(self, account, role_name, profile=None):
        self.role = role_name
        self.account_number = str(account)
        self.profile = profile
        self.credentials = self.assume_role(role_name, self.account_number)
        self.status = {'STATUS': ''}

    def assume_role(self, account, role):
        """
        Summary:
            Assumes a DynamoDB role in 'destination' AWS account
        Args:
            :type account: str
            :param account: AWS account number
            :type role: str
            :param role: IAM role designation used to access AWS resources
                in an account
            :type profile: str
            :param role: profile_name is an IAM user or IAM role name represented
                in the local awscli configuration as a profile entry
        Returns:  dict (Credentials)
        """
        if self.profile:
            session = boto3.Session(profile_name=self.profile)
        else:
            session = boto3.Session()
        sts_client = session.client('sts')

        try:
            # assume role in destination account
            assumed_role = sts_client.assume_role(
                RoleArn="arn:aws:iam::%s:role/%s" % (account, role),
                RoleSessionName="AssumeAWSRoleSession"
            )
            self.status = {'STATUS': 'SUCCESS'}
        except ClientError as e:
            if e.response['Error']['Code'] == 'AccessDenied':
                self.status = {'STATUS': 'AccessDenied'}
                return {}
            else:
                logger.exception("Couldn't assume role %s in account %s (Code: %s Message: %s)" %
                    (self.role, self.account_number, e.response['Error']['Code'],
                     e.response['Error']['Message']))
                self.status = {'STATUS': 'ERROR'}
                return {}
        return assumed_role['Credentials']

    def create_service_client(self, aws_service, credentials=None):
        """
        Summary:
            Creates the appropriate boto3 client for a particular AWS service
        Args:
            :type service: str
            :param service: name of service at Amazon Web Services (AWS),
                e.g. s3, ec2, etc
            :type credentials: sts credentials object
            :param credentials: authentication credentials to resource in AWS
            :type role: str
            :param role: IAM role designation used to access AWS resources
                in an account
        Returns:
            Success | Failure, TYPE: bool
        """
        try:
            if role and account:     # create client for a different AWS account
                if self.status.get('STATUS') == 'SUCCESS':
                    client = boto3.client(
                        aws_service,
                        aws_access_key_id=self.credentials['AccessKeyId'],
                        aws_secret_access_key=self.credentials['SecretAccessKey'],
                        aws_session_token=self.credentials['SessionToken']
                    )
                else:
                    logger.critical('failed to create client using AssumeAWSRole')
                    raise ClientError(
                        '%s: Problem creating client by assuming role %s in account %s' %
                        (inspect.stack()[0][3], str(role), str(account))
                        )
            else:
                return boto3.client(aws_service)    # create client in the current AWS account
        except ClientError as e:
            logger.exception(
                "%s: Problem creating %s client in account %s (Code: %s Message: %s)" %
                (inspect.stack()[0][3], aws_service, self.account_number,
                e.response['Error']['Code'], e.response['Error']['Message']))
            raise
        return client
