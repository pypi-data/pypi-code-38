import json
import os

from google.cloud.exceptions import NotFound, GoogleCloudError
from google.cloud import storage
from google.oauth2 import service_account

from onepanel.utilities.gcp_cs.authentication import Provider
from onepanel.utilities.gcp_utility import GCPUtility


class Wrapper:
    @staticmethod
    def is_error_expired_token(error):
        """
        :param error:
        :type error ClientError
        :return:
        """

        return error.response['Error']['Code'] == 'ExpiredToken'

    def __init__(self, bucket_name=None, credentials_provider=None, retry=3):
        """
        :param bucket_name: GCP CS Bucket name
        :param credentials_provider: Provides credentials for requests.
        :type credentials_provider: onepanel.utilities.gcp_cs.authentication.Provider
        """
        if bucket_name is None:
            bucket_name = os.getenv('DATASET_BUCKET', 'onepanel-datasets')

        if credentials_provider is None:
            credentials_provider = Provider()

        self.bucket_name = bucket_name
        self.credentials_provider = credentials_provider
        self.gcp_cs = None
        self.reset_client()
        self.retry = retry
        self.retries = 0

    def create_client(self):
        json_str = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON_STR', '')
        if not json_str:
            print("Google credentials cannot be empty! Check the environment variable: {env_var}.".format(
                env_var='GOOGLE_APPLICATION_CREDENTIALS_JSON_STR'))
            exit(-1)

        service_account_info = json.loads(json_str)
        credentials = service_account.Credentials.from_service_account_info(service_account_info)
        storage_client = storage.Client("onepanelio", credentials)
        if not self.credentials_provider.loads_credentials():
            return storage_client

        credentials = self.credentials_provider.credentials()

        return storage_client

    def reset_client(self):
        self.gcp_cs = self.create_client()

    def list_files(self, prefix):
        files = {}
        gcp_utility = GCPUtility()
        bucket = gcp_utility.storageClient.get_bucket(gcp_utility.get_dataset_bucket_name())
        blobs = bucket.list_blobs(prefix=prefix)
        for blob in blobs:
            files[blob.name] = blob

        # Skip the file that has the same name as the prefix.
        if prefix in files:
            del files[prefix]

        self.retries = 0
        return files

    def upload_file(self, filepath, key):
        # Normalize s3 path if we're on windows
        key = key.replace('\\', '/')

        try:
            gcp_utility = GCPUtility()
            bucket = gcp_utility.storageClient.get_bucket(gcp_utility.get_dataset_bucket_name())
            blob = bucket.blob(key)
            blob.upload_from_filename(filepath)
            self.retries = 0
            return True
        except GoogleCloudError:
            if self.retries < self.retry:
                self.retries += 1
                self.reset_client()
                return self.upload_file(filepath, key)

            raise
        except FileNotFoundError as fileNotFoundError:
            # Do nothing
            return

    def download_file(self, local_path, key):
        gcp_utility = GCPUtility()
        bucket = gcp_utility.storageClient.get_bucket(gcp_utility.get_dataset_bucket_name())
        blob = bucket.blob(key)
        try:
            # Create the directory locally if it doesn't exist yet.
            dirname = os.path.dirname(local_path)
            os.makedirs(dirname, exist_ok=True)
            blob.download_to_filename(local_path)
        except NotFound:
            if self.retries < self.retry:
                self.retries += 1
                self.reset_client()
                return self.download_file(local_path, key)

            raise

    def delete_file(self, key):
        key = key.replace('\\', '/')

        try:
            gcp_utility = GCPUtility()
            bucket = gcp_utility.storageClient.get_bucket(gcp_utility.get_dataset_bucket_name())
            bucket.delete_blob(blob_name=key)

            self.retries = 0
            return True
        except NotFound:
            if self.retries < self.retry:
                self.retries += 1
                self.reset_client()
                return self.delete_file(key)

            raise

    def copy_file(self, source_key, destination_key):
        # Normalize s3 path if we're on windows
        source_key = source_key.replace('\\', '/')
        destination_key = destination_key.replace('\\', '/')
        gcp_utility = GCPUtility()
        bucket = gcp_utility.storageClient.get_bucket(gcp_utility.get_dataset_bucket_name())
        blob = bucket.blob(source_key)
        copied_blob = bucket.copy_blob(blob=blob, destination_bucket=bucket, new_name=destination_key)

    def move_file(self, source_key, destination_key):
        # We do a try here in case copy fails, in which case we don't try delete.
        try:
            self.copy_file(source_key, destination_key)
            self.delete_file(source_key)
        except BaseException:
            raise
