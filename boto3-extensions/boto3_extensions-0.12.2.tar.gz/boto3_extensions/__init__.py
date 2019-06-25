import boto3
import botocore.session
import logging
from logging import NullHandler
from boto3_extensions.arn_patch import patch_session, \
                                   patch_service_context, \
                                   patch_resource_factory, \
                                   patch_resource_meta, \
                                   patch_create_request_parameters
from os import environ, path
from imp import reload

logging.getLogger(__name__).addHandler(NullHandler())
_logger = logging.getLogger(__name__)

dir_path = path.dirname(path.realpath(__file__))
environ['AWS_DATA_PATH'] = '{dir_path}/data/'.format(dir_path=dir_path)
reload(boto3)


def arn_patch_boto3():
    """
    Patch boto3 to support ARNs for all resources
    """
    patch_session()
    patch_service_context()
    patch_resource_factory()
    patch_resource_meta()
    patch_create_request_parameters()
    _logger.info('Patched Boto3 with arn support')


class _CredentialSourcer:
    TYPE = 'boto3_extensions'

    def __init__(self, base_session):
        if not base_session:
            base_session = boto3.Session()
        self._base_session = base_session

    def is_supported(self, source):
        return source == self.TYPE

    def source_credentials(self, *args, **kwargs):
        return self._base_session.get_credentials()


def get_role_session(role_arn,
                     role_session_name=None,
                     base_session=None,
                     **kwargs):

    botocore_session = botocore.session.Session()
    botocore_session.full_config['profiles'][role_arn] = {
        'role_arn': role_arn,
        'credential_source': _CredentialSourcer.TYPE,
        'session_name': role_session_name
    }

    session = boto3.Session(
        profile_name=role_arn, botocore_session=botocore_session, **kwargs)

    session._session.get_component('credential_provider').get_provider(
        'assume-role')._credential_sourcer = _CredentialSourcer(base_session)

    return session


class ConnectionManager:
    '''
    Usage:
        connections = ConnectionManager(region_name='us-east-1')
        session = connections.get_session(role_arn='arn:aws:iam::1234567890:role/test-role', role_session_name='test')

    You can also provide a base session if you prefer:
        connections = ConnectionManager(session=my_boto3_session)

    '''

    def __init__(self, session=None, **kwargs):
        self._base_session = session
        self.default_session_args = kwargs
        self.connections = {}

    def get_session(self, role_arn, role_session_name):

        if (role_arn, role_session_name) not in self.connections:
            session = get_role_session(role_arn, role_session_name,
                                       self._base_session,
                                       **self.default_session_args)
            self.connections[(role_arn, role_session_name)] = session
        return self.connections[(role_arn, role_session_name)]
