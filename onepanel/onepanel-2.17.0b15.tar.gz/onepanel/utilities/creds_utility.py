import os
import sys

from onepanel.utilities.gcs_authenticator import GCSAuthenticator
from onepanel.utilities.s3_authenticator import S3Authenticator


class CredsUtility:
    @staticmethod
    def get_credentials(connection, account_uid, entity_type, entity_uid):
        """

        :param connection:
            - Usually from ctx.obj['connection']
        :param account_uid: string
        :param entity_type: string
        :param entity_uid: string
        :return:
        """
        cloud_provider = os.getenv('CLOUD_PROVIDER', 'AWS')
        if cloud_provider == 'GCP':
            gcsauth = GCSAuthenticator(connection)
            creds = gcsauth.get_gcs_credentials(account_uid,entity_type,entity_uid)
            creds['data'] = "test"
        elif cloud_provider == "AWS":
            s3auth = S3Authenticator(connection)
            creds = s3auth.get_s3_credentials(account_uid, entity_type, entity_uid)
        else:
            creds = None
        if creds is None or creds['data'] is None:
            print("Unable to get provider credentials. Exiting.")
            sys.exit(-1)
        return creds