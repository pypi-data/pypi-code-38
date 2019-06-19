import boto3
from botocore.exceptions import NoCredentialsError, ClientError
# from botocore.errorfactory import
import logging
import os
import sys
import json

FORMAT = '%(name) %(asctime)-15s  %(levelname)-8s %(message)s'
logging.basicConfig(level=logging.INFO)
logging.getLogger('botocore.credentials').setLevel(logging.WARNING)
logging.getLogger('botocore.vendored.requests.packages.urllib3.connectionpool').setLevel(logging.WARNING)
logger = logging.getLogger(__file__)


class AwsAuthenticationHelper:
    ML_ACCOUNT_ID = '502812207255'
    ML_ROLE_NAME = 'MissingLinkResourceManager'
    ML_ROLE_DESCRIPTION = 'This policy is used in order to grant permissions to MissingLink.ai to manage the resource managers in this aws account'

    @classmethod
    def _get_script_path(cls):
        return os.path.dirname(os.path.realpath(__file__))

    @classmethod
    def get_policy(cls):
        with open(os.path.join(cls._get_script_path(), 'aws_policy.json'), 'r') as f:
            return json.load(f)

    @classmethod
    def get_assume_role_policy(cls):
        with open(os.path.join(cls._get_script_path(), 'aws_sts_assume_policy.json'), 'r') as f:
            return json.load(f)

    @classmethod
    def _set_policy(cls):
        target_arn = 'arn:aws:iam::{}:policy/{}'.format(cls.account_id(), cls.ML_ROLE_NAME)
        try:
            policy = cls.iam().get_policy(PolicyArn=target_arn)
        except cls.iam().exceptions.NoSuchEntityException:
            policy = None

        if policy is None:
            logging.info('Creating policy... ')
            policy = cls.iam().create_policy(
                PolicyName=cls.ML_ROLE_NAME,
                Description=cls.ML_ROLE_DESCRIPTION,
                PolicyDocument=json.dumps(cls.get_policy())
            )

        versions = cls.iam().list_policy_versions(PolicyArn=target_arn)
        for version in versions['Versions']:
            if not version['IsDefaultVersion']:
                logging.info('%s: Removing depricated, non default version: %s', cls.ML_ROLE_NAME, version['VersionId'])
                cls.iam().delete_policy_version(PolicyArn=target_arn, VersionId=version['VersionId'])

        cls.iam().create_policy_version(
            PolicyArn=policy['Policy']['Arn'],
            PolicyDocument=json.dumps(cls.get_policy()),
            SetAsDefault=True
        )
        logger.info('New policy version created')
        return policy

    @classmethod
    def _set_attach_policy(cls, role_policy_arn):
        try:
            role = cls.iam().get_role(RoleName=cls.ML_ROLE_NAME)

        except cls.iam().exceptions.NoSuchEntityException:
            logger.info('Creating role %s', cls.ML_ROLE_NAME)
            role = cls.iam().create_role(
                RoleName=cls.ML_ROLE_NAME,
                Description=cls.ML_ROLE_DESCRIPTION,
                AssumeRolePolicyDocument=json.dumps(cls.get_assume_role_policy()),
            )
        attached_policies = cls.iam().list_role_policies(RoleName=cls.ML_ROLE_NAME)['PolicyNames']

        if cls.ML_ROLE_NAME not in attached_policies:
            logging.info("Attaching policy %s to role %s", role_policy_arn, cls.ML_ROLE_NAME)
            cls.iam().attach_role_policy(PolicyArn=role_policy_arn, RoleName=cls.ML_ROLE_NAME)
        return role

    @classmethod
    def grant_access(cls):
        try:
            policy = cls._set_policy()
            policy_arn = policy['Policy']['Arn']
            res = cls._set_attach_policy(policy_arn)
            return res['Role']['RoleId'], res['Role']['Arn']
        except ClientError as ex:
            if ex.response['Error']['Code'] == 'AccessDenied':
                return None

            raise

    @classmethod
    def client(cls, client_id, aws_access_key_id=None, aws_secret_access_key=None, aws_session_token=None):
        return boto3.client(
            client_id,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token)

    @classmethod
    def sts(cls):
        return cls.client('sts')

    @classmethod
    def iam(cls):
        return cls.client('iam')

    @classmethod
    def whoami(cls):
        return cls.sts().get_caller_identity()

    @classmethod
    def account_id(cls):
        return cls.whoami()['Account']

    @classmethod
    def account_name(cls):
        try:
            aliases = cls.iam().list_account_aliases().get('AccountAliases', [])
            if not aliases:
                return cls.account_id()

            return aliases[0]
        except ClientError:
            return cls.account_id()

    @classmethod
    def is_aws_configured(cls):
        try:
            cls.whoami()
            return True
        except NoCredentialsError:
            return False
