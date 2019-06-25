# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Blob info base class."""

from requests.exceptions import RequestException
from typing import Tuple

import requests


class BaseBlobInfo:
    """Blob info base class."""

    def __init__(self):
        """Initialize Blob Info."""
        self.registry_id = ""
        self.blob_account_name = ""
        self.blob_container_name = ""
        self.blob_relative_path = ""
        self.blob_sas_token = ""

    def get_data_wasbs_path(self) -> str:
        """Prepare spark info, including getting blob metadata, set SPARK configuration, etc."""
        success, blob_account_name, blob_container_name, blob_relative_path, blob_sas_token = \
            self.get_blob_metadata()
        if success:
            self.blob_account_name = blob_account_name
            self.blob_container_name = blob_container_name
            self.blob_relative_path = blob_relative_path
            self.blob_sas_token = blob_sas_token

        # Allow SPARK to read from Blob remotely
        wasbs_path = 'wasbs://%s@%s.blob.core.windows.net/%s' % (
            self.blob_container_name,
            self.blob_account_name,
            self.blob_relative_path)

        return wasbs_path

    def get_blob_metadata(self) -> Tuple[bool, str, str, str, str]:
        """
        Get blob metadata for this public data. A remote call to REST API will be invoked.

        :return: a tuple including success status, blob account name, container name, relative path, and sas token.
        :rtype: Tuple[bool, str, str, str, str]
        """
        failure_from_api = False
        blob_account_name = ''
        blob_container_name = ''
        blob_relative_path = ''
        blob_sas_token = ''
        try:
            request_url = \
                'https://opendatasetwebapi.azurewebsites.net/discoveryapi/OpenDataset/GetDatasetRegistryById?id=%s' % \
                (self.registry_id)
            response = requests.get(request_url)
            response.raise_for_status()
            json_data = response.json()
            assert(json_data['code'] == 1000)

            blob_account_name = json_data['data']['BlobLocation']['AccountName']
            blob_sas_token = json_data['data']['BlobLocation']['SasToken']
            path = json_data['data']['BlobLocation']['Path']
            slash_index = path.find('/')
            if slash_index >= 0:
                blob_container_name = path[:slash_index]
                blob_relative_path = path[(slash_index + 1):]
            else:
                failure_from_api = True
        except RequestException as ex:
            failure_from_api = True
            print('Caught request exception: %s' % (ex))
            print('Hit exception when getting storage info from REST API, falling back to default location...')
        except AssertionError:
            failure_from_api = True
            print('Hit error when getting storage info from REST API, falling back to default location...')
        except ValueError:
            failure_from_api = True
            print('Hit value error when getting storage info from REST API, falling back to default location...')

        return (not failure_from_api), blob_account_name, blob_container_name, blob_relative_path, blob_sas_token
