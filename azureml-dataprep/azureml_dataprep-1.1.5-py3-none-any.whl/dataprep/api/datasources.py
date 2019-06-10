# Copyright (c) Microsoft Corporation. All rights reserved.
from .engineapi.typedefinitions import (DataSourceTarget, AzureBlobResourceDetails, DataSourcePropertyValue,
                                        ResourceDetails, LocalResourceDetails, AzureDataLakeResourceDetails,
                                        Secret as SecretId, OutputFilePropertyValue, DatabaseType, DatabaseAuthType,
                                        OutputFileDestination)
from .secretmanager import register_secret, create_secret
from ._oauthToken import get_az_cli_tokens
from typing import TypeVar, List, Callable, cast
from urllib.parse import urlparse
from enum import Enum
import os
import re
import json


Path = TypeVar('Path', str, List[str])
Secret = TypeVar('Secret', str, SecretId)


def _extract_resource_details(path: Path, extractor: Callable[[str], ResourceDetails]) -> List[ResourceDetails]:
    return [extractor(path)] if isinstance(path, str) else path.map(extractor)


def _extract_local_resource_details(path: str) -> ResourceDetails:
    return cast(ResourceDetails, LocalResourceDetails(os.path.abspath(os.path.expanduser(path))))


def _extract_blob_resource_details(path: str) -> ResourceDetails:
    parts_list = urlparse(path)
    path = '{0}://{1}{2}'.format(*parts_list)
    query_string = parts_list.query or None
    if query_string:
        register_secret(value=query_string, id=path)
        resource_details = AzureBlobResourceDetails(path, create_secret(path))
    else:
        resource_details = AzureBlobResourceDetails(path)
    return cast(ResourceDetails, resource_details)


blob_pattern = re.compile(r'^https?://[^/]+\.blob\.core\.windows\.net', re.IGNORECASE)
wasb_pattern = re.compile(r'^wasbs?://', re.IGNORECASE)
adls_pattern = re.compile(r'^adl://[^/]+\.azuredatalake\.net', re.IGNORECASE)


class FileDataSource:
    def __init__(self, value: DataSourcePropertyValue):
        self.underlying_value = value

    @staticmethod
    def datasource_from_str(path: str) -> 'FileDataSource':
        if blob_pattern.match(path) or wasb_pattern.match(path):
            return BlobDataSource(path)
        elif adls_pattern.match(path):
            return DataLakeDataSource(path, 'token')
        else:
            return LocalDataSource(path)


class LocalDataSource(FileDataSource):
    """
    Describes a source of data that is available from local disk.

    :param path: Path to file(s) or folder. Can be absolute or relative.
    """
    def __init__(self, path: Path):
        resource_details = _extract_resource_details(path, _extract_local_resource_details)
        datasource_property = DataSourcePropertyValue(target=DataSourceTarget.LOCAL, resource_details=resource_details)
        super().__init__(datasource_property)


class BlobDataSource(FileDataSource):
    """
    Describes a source of data that is available from Azure Blob Storage.

    :param path: URL of the file(s) or folder in Azure Blob Storage.
    """
    def __init__(self, path: Path):
        resource_details = _extract_resource_details(path, _extract_blob_resource_details)
        datasource_property = DataSourcePropertyValue(target=DataSourceTarget.AZUREBLOBSTORAGE,
                                                      resource_details=resource_details)
        super().__init__(datasource_property)


class DataLakeDataSource(FileDataSource):
    """
    Describes a source of data that is available from Azure Data Lake.

    :param path: URL of the file(s) or folder in Azure Data Lake.
    :param accessToken: (Optional) Access token.
    :param refreshToken: (Optional) Refresh token.
    :param tenant: (Optional) Tenant ID.
    """

    adl_template = 'adl://{}.azuredatalakestore.net/{}'

    def __init__(self, path: Path, accessToken: str = None, refreshToken: str = None, tenant: str = None):
        encoded_token = ''
        if accessToken is None and refreshToken is None:
            access, refresh = get_az_cli_tokens(tenant)
            encoded_token = DataLakeDataSource._encode_token(access, refresh)
        else:
            encoded_token = DataLakeDataSource._encode_token(accessToken, refreshToken)
        resource_details = _extract_resource_details(path, DataLakeDataSource._register_secret(encoded_token))
        datasource_property = DataSourcePropertyValue(target=DataSourceTarget.AZUREDATALAKESTORAGE,
                                                      resource_details=resource_details)
        super().__init__(datasource_property)

    @staticmethod
    def _register_secret(oauthToken: str) -> Callable[[str], ResourceDetails]:
        def _path_to_resource_details(path: str) -> ResourceDetails:
            register_secret(value=oauthToken, id=path)
            resource_details = AzureDataLakeResourceDetails(create_secret(path), path)
            return cast(ResourceDetails, resource_details)
        return _path_to_resource_details

    @staticmethod
    def _encode_token(access_token: str, refresh_token: str) -> str:
        payload = {'accessToken': access_token, 'type': 'oauth'}
        if refresh_token:
            payload['refreshToken'] = refresh_token
        return json.dumps(payload)


class MSSQLDataSource:
    """
    Represents a datasource that points to a Microsoft SQL Database.

    :var server_name: The SQL Server name.
    :vartype server: str
    :var database_name: The database name.
    :vartype database: str
    :var user_name: The username used for logging into the database.
    :vartype user_name: str
    :var password: The password used for logging into the database.
    :vartype password: str
    :var trust_server: Trust the server certificate.
    :vartype trust_server: bool
    """
    def __init__(self,
                 server_name: str,
                 database_name: str,
                 user_name: str,
                 password: Secret,
                 trust_server: bool = True):
        secret = password
        if isinstance(password, str):
            secret = register_secret(value=password, id=user_name)
        self.server = server_name
        self.credentials_type = DatabaseAuthType.SERVER
        self.database = database_name
        self.user_name = user_name
        self.password = secret
        self.trust_server = trust_server
        self.database_type = DatabaseType.MSSQL


class PostgreSQLDataSource:
    """
    Represents a datasource that points to a PostgreSQL Database.

    :var server_name: The SQL Server name.
    :vartype server: str
    :var database_name: The database name.
    :vartype database: str
    :var user_name: The username used for logging into the database.
    :vartype user_name: str
    :var password: The password used for logging into the database.
    :vartype password: str
    """
    def __init__(self,
                 server_name: str,
                 database_name: str,
                 user_name: str,
                 password: Secret):
        secret = password
        if isinstance(password, str):
            secret = register_secret(value=password, id=user_name)
        self.credentials_type = DatabaseAuthType.SERVER
        self.server = server_name
        self.database = database_name
        self.user_name = user_name
        self.password = secret
        self.database_type = DatabaseType.POSTGRESQL


DataSource = TypeVar('DataSource', FileDataSource, MSSQLDataSource, PostgreSQLDataSource)


class FileOutput:
    """
    Base class representing any file output target.
    """
    def __init__(self, value: OutputFilePropertyValue):
        self.underlying_value = value

    @staticmethod
    def file_output_from_str(path: str) -> 'FileOutput':
        """
        Constructs an instance of BlobFileOutput or LocalFileOutput depending on the path provided.
        """
        if blob_pattern.match(path) or wasb_pattern.match(path):
            return BlobFileOutput(path)
        else:
            return LocalFileOutput(path)


class LocalFileOutput(FileOutput):
    """
    Describes local target to write file(s) to.

    :param path: Path where output file(s) will be written to.
    """
    def __init__(self, path: Path):
        resource_details = _extract_resource_details(path, _extract_local_resource_details)
        output_file_value = OutputFilePropertyValue(target=OutputFileDestination.LOCAL,
                                                    resource_details=resource_details)
        super().__init__(output_file_value)


class BlobFileOutput(FileOutput):
    """
    Describes Azure Blob Storage target to write file(s) to.

    :param path: URL of the container where output file(s) will be written to.
    """

    def __init__(self, path: Path):
        resource_details = _extract_resource_details(path, _extract_blob_resource_details)
        output_file_value = OutputFilePropertyValue(target=OutputFileDestination.AZUREBLOB,
                                                    resource_details=resource_details)
        super().__init__(output_file_value)


DataDestination = TypeVar('DataDestination', FileOutput, 'Datastore')
