import os

from onepanel.utilities.gcp_utility import GCPUtility
from onepanel.utilities.s3.file_sync import FileSynchronizer, ThreadedFileSynchronizer, FileDifference, FileEvent
from onepanel.utilities.s3.authentication import APIProvider, MemoryCachedCredentialsProvider

import onepanel.utilities.s3.wrapper\
    as S3
import onepanel.services as services

# TODO document
class CloudStorageUtility:
    cached_credentials_provider = None

    @staticmethod
    def get_utility(account_uid=None, entity_type=None, entity_uid=None, refresh=False):
        util = None
        cloud_provider = os.getenv('CLOUD_PROVIDER', 'AWS')
        if cloud_provider == 'GCP':  # TODO
            util = GCPUtility()
        elif cloud_provider == "AWS":
            if CloudStorageUtility.cached_credentials_provider is None or refresh:
                connection = services.get_connection()
                endpoint = '{}/accounts/{}/{}/{}/credentials/aws'.format(connection.URL, account_uid,
                                                                         entity_type, entity_uid)
                CloudStorageUtility.cached_credentials_provider = \
                    MemoryCachedCredentialsProvider(APIProvider(connection, endpoint))

            return S3.Wrapper(credentials_provider=CloudStorageUtility.cached_credentials_provider)

    @staticmethod
    def get_file_synchronizer(filepath, s3_prefix, s3_wrapper, master=FileSynchronizer.LOCAL, s3_full_path=None, ignore_file_states=None):
        synchronizer = FileSynchronizer(filepath, s3_prefix, s3_wrapper, master, s3_full_path, ignore_file_states)
        return ThreadedFileSynchronizer(synchronizer)

    @staticmethod
    def sync_files(account_uid, entity_type, entity_uid, filepath, s3_prefix, s3_wrapper=None,
                   master=FileSynchronizer.LOCAL, s3_full_path=None, ignore_file_states=None,
                   quiet=False, include=None, prefix=None, refresh=False):
        if s3_wrapper is None:
            s3_wrapper = CloudStorageUtility.get_utility(account_uid, entity_type, entity_uid, refresh)

        synchronizer = CloudStorageUtility.get_file_synchronizer(filepath, s3_prefix, s3_wrapper, master, s3_full_path, ignore_file_states)

        if not quiet:
            filepath_length = len(filepath)
            if master == FileSynchronizer.LOCAL and filepath[-1] != '/':
                filepath_length += 1

            synchronizer.hooks = [FileSynchronizer.print_status(filepath_length, master)]

        differences = synchronizer.find_difference()

        if len(differences) == 0:
            return 0

        if include is not None:
            differences = FileSynchronizer.filter(differences, include, prefix)

        try:
            synchronizer.synchronize(differences.values())
            synchronizer.shutdown()
        except KeyboardInterrupt as e:
            if master == FileSynchronizer.LOCAL:
                print('\nStopping upload. This may take a few seconds')
            else:
                print('\nStopping download. This may take a few seconds')

            synchronizer.shutdown(False)

        return len(differences.values())
