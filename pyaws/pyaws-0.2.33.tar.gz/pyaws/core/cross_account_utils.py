import inspect
import boto3
from botocore.exceptions import ClientError
import loggers
from _version import __version__


# lambda custom log object
logger = loggers.getLogger(__version__)


class AssumeAWSRole():
    """ class def for assuming roles in AWS """
    def __init__(self, role_name=None, account=None, profile=None):
        self.role = role_name
        if account:
            self.account_number = str(account)
            self.credentials = self.assume_role(str(account), role_name)
        elif profile:
            self.profile = profile
            r = sts_client.get_caller_identity()
            self.account_number = r['Account']
            self.credentials = self.assume_role()
        self.status = {}

    def assume_role(self, account=None, role=None):
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
            sts_client = session.client('sts')
        else:
            sts_client = boto3.client('sts')

        try:
            # assume role in destination account
            if account and role:
                assumed_role = sts_client.assume_role(
                    RoleArn="arn:aws:iam::%s:role/%s" % (account, role),
                    RoleSessionName="AssumeAWSRoleSession"
                )
            else:
                assumed_role = sts_client.assume_role(
                    RoleArn="arn:aws:iam::%s:role/%s" % (self.account_number, self.role),
                    RoleSessionName="AssumeAWSRoleSession"
                )
        except ClientError as e:
            logger.exception(
                "%s: Problem assuming role %s in account %s (Code: %s Message: %s)" %
                (inspect.stack()[0][3], role, account,
                e.response['Error']['Code'], e.response['Error']['Message'])
            )
            if e.response['Error']['Code'] == 'AccessDenied':
                self.status = {'STATUS': 'AccessDenied', 'FLAG': False}
                return {}
            else:
                self.status = {'STATUS': 'ERROR', 'FLAG': False}
                return {}
        self.status = {'STATUS': 'SUCCESS', 'FLAG': True}
        return assumed_role['Credentials']

    def create_service_client(self, aws_service, account=None, role=None):
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
                    self.status = {'STATUS': 'ERROR', 'FLAG': False}
                    return self.status
            else:
                return boto3.client(aws_service)    # create client in the current AWS account
        except ClientError as e:
            logger.exception(
                "%s: Problem creating %s client in account %s (Code: %s Message: %s)" %
                (inspect.stack()[0][3], aws_service, self.account_number,
                e.response['Error']['Code'], e.response['Error']['Message']))
            raise
        return client
