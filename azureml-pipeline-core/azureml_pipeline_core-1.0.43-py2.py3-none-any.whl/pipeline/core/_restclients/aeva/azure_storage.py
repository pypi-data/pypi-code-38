# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""azure_storage.py, module for interacting with Azure for storage."""

import tempfile
import zipfile
import os
from azureml._vendor.azure_storage.blob import BlockBlobService


class AzureStorage(object):
    """Handles interactions with Azure for Uploading/Downloading data."""

    def upload_to_azure(self, blob_name, sas_uri, file_path):
        """
        Upload a file or directory to azure
        :param str blob_name: name of blob to upload to
        :param str sas_uri: sas uri to upload to
        :param str file_path: the path to file or directory to upload
        :return: None
        """
        if not os.path.isdir(file_path):
            self.upload_file(blob_name, sas_uri, file_path)
        else:
            with tempfile.TemporaryDirectory() as temporary:
                zip_file_path = os.path.join(temporary, "directory.zip")
                self.make_zipfile(file_path, zip_file_path)
                self.upload_file(blob_name, sas_uri, zip_file_path)

    @staticmethod
    def upload_file(blob_name, sas_uri, file_path):
        """
        Upload a file to azure
        :param str blob_name: name of blob to upload to
        :param str sas_uri: sas uri to upload to
        :param str file_path: the path to file or zip file to upload
        :return: None
        """
        uri_parts = sas_uri.split('/')
        container_name = uri_parts[3]
        account_name = uri_parts[2].split('.')[0]
        sas_token = sas_uri.split('?', 2)[1]
        blob_service = BlockBlobService(account_name=account_name, sas_token=sas_token)
        stream = open(file_path, "rb") if isinstance(file_path, str) else file_path
        blob_service.create_blob_from_stream(container_name, blob_name, stream)
        stream.close()

    @staticmethod
    def download_from_azure(storage_account_key, blob_uri, file_path):
        """
        Download a blob from azure
        :param str storage_account_key: account key for the storage account
        :param str blob_uri: uri of blob to download
        :param str file_path: the file path to download the blob to
        :return: None
        """
        uri_parts = blob_uri.split('/')
        container_name = uri_parts[3]
        account_name = uri_parts[2].split('.')[0]
        blob_name = blob_uri.split(container_name + '/')[1]
        blob_service = BlockBlobService(account_name=account_name, account_key=storage_account_key)
        blob_service.get_blob_to_path(container_name, blob_name, file_path)

    @staticmethod
    def make_zipfile(base_dir, zip_file_path):
        """
        Make a zip file of a directory
        :param str base_dir: path to directory to zip
        :param str zip_file_path: path of zip file to create
        :return: None
        """
        with zipfile.ZipFile(zip_file_path, "w") as zf:
            for dirpath, dirnames, filenames in os.walk(base_dir):
                relative_dirpath = os.path.relpath(dirpath, base_dir)
                for name in sorted(dirnames):
                    full_path = os.path.normpath(os.path.join(dirpath, name))
                    relative_path = os.path.normpath(os.path.join(relative_dirpath, name))
                    zf.write(full_path, relative_path)
                for name in filenames:
                    full_path = os.path.normpath(os.path.join(dirpath, name))
                    relative_path = os.path.normpath(os.path.join(relative_dirpath, name))
                    if os.path.isfile(full_path):
                        zf.write(full_path, relative_path)
