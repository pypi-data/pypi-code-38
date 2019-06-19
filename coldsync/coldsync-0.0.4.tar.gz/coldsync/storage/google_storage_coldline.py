from google.cloud import storage

from coldsync.google_storage_wrapper import is_bucket_present, create_bucket, get_all_files, upload_file, \
    download_file, delete_file, list_all_files
from coldsync.storage.base import BaseStorage


class GoogleColdlineStorage(BaseStorage):
    LOCATION = "europe-west3"  # Frakfurt
    STORAGE_CLASS = "COLDLINE"

    def __init__(self, bucket_name):
        self.client = storage.Client()
        self.bucket_name = bucket_name

        if not is_bucket_present(client=self.client, bucket_name=self.bucket_name):
            create_bucket(
                client=self.client, bucket_name=self.bucket_name,
                location=GoogleColdlineStorage.LOCATION,
                storage_class=GoogleColdlineStorage.STORAGE_CLASS
            )

    def get_files(self):
        return get_all_files(client=self.client, bucket_name=self.bucket_name)

    def list_files(self):
        list_all_files(client=self.client, bucket_name=self.bucket_name)

    def upload_file(self, file_path_on_disk, file_path_in_bucket=None):
        upload_file(client=self.client, bucket_name=self.bucket_name, file_name=file_path_on_disk,
                    path_to_blob=file_path_in_bucket)

    def download_file(self, file_path_in_bucket, file_path_on_disk):
        download_file(client=self.client, bucket_name=self.bucket_name, path_to_blob=file_path_in_bucket,
                      output_file_name=file_path_on_disk)

    def delete_file(self, file_path_in_bucket):
        return delete_file(client=self.client, bucket_name=self.bucket_name, path_to_blob=file_path_in_bucket)
