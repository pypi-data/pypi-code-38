# Copyright (c) Microsoft Corporation. All rights reserved.
from .datasources import DataLakeDataSource
from ... import dataprep
from typing import TypeVar, List
import json

DEFAULT_SAS_DURATION = 30  # this aligns with our SAS generation in the UI BlobStorageManager.ts
AML_INSTALLED = True
try:
    from azureml.data.abstract_datastore import AbstractDatastore
    from azureml.data.azure_storage_datastore import AzureFileDatastore, AzureBlobDatastore
    from azureml.data.azure_data_lake_datastore import AzureDataLakeDatastore, AzureDataLakeGen2Datastore
    from azureml.data.azure_sql_database_datastore import AzureSqlDatabaseDatastore
    from azureml.data.azure_postgre_sql_datastore import AzurePostgreSqlDatastore
    from azureml.data.data_reference import DataReference
    from azureml.data.datapath import DataPath
except ImportError:
    AML_INSTALLED = False


Datastore = TypeVar('Datastore', 'AbstractDatastore', 'DataReference', 'DataPath')
Datastores = TypeVar('Datastores', Datastore, List[Datastore])


def datastore_to_dataflow(data_source: Datastores) -> 'dataprep.Dataflow':
    from .dataflow import Dataflow
    from .engineapi.api import get_engine_api

    def construct_df(datastore_values):
        if type(datastore_values) is not list:
            datastore_values = [datastore_values]
        df = Dataflow(get_engine_api())
        return df.add_step('Microsoft.DPrep.GetDatastoreFilesBlock', {
                               'datastores': [datastore_value._to_pod() for datastore_value in datastore_values]
                           })

    if type(data_source) is list:
        datastore_values = []
        for source in data_source:
            datastore, datastore_value = get_datastore_value(source)
            if not _is_fs_datastore(datastore):
                raise NotSupportedDatastoreTypeError(datastore)
            datastore_values.append(datastore_value)
        return construct_df(datastore_values)

    datastore, datastore_value = get_datastore_value(data_source)
    if _is_fs_datastore(datastore):
        return construct_df(datastore_value)

    if isinstance(datastore, AzureSqlDatabaseDatastore) or isinstance(datastore, AzurePostgreSqlDatastore):
        df = Dataflow(get_engine_api())
        return df.add_step('Microsoft.DPrep.ReadDatastoreSqlBlock', {
                               'datastore': datastore_value._to_pod()
                           })

    raise NotSupportedDatastoreTypeError(datastore)


def get_datastore_value(data_source: Datastore) -> ('AbstractDatastore', 'dataprep.api.dataflow.DatastoreValue'):
    from .dataflow import DatastoreValue
    _ensure_imported()

    datastore = None
    path_on_storage = ''

    if isinstance(data_source, AbstractDatastore):
        datastore = data_source
    elif isinstance(data_source, DataReference):
        datastore = data_source.datastore
        path_on_storage = data_source.path_on_datastore or path_on_storage
    elif isinstance(data_source, DataPath):
        datastore = data_source._datastore
        path_on_storage = data_source.path_on_datastore or path_on_storage

    _ensure_supported(datastore)
    path_on_storage = path_on_storage.lstrip('/')

    workspace = datastore.workspace
    _set_auth_type(workspace)
    return (datastore, DatastoreValue(
        subscription=workspace.subscription_id,
        resource_group=workspace.resource_group,
        workspace_name=workspace.name,
        datastore_name=datastore.name,
        path=path_on_storage
    ))


def login():
    from azureml.core.authentication import InteractiveLoginAuthentication
    auth = InteractiveLoginAuthentication()
    auth.get_authentication_header()


def _ensure_imported():
    if not AML_INSTALLED:
        raise ImportError('Unable to import Azure Machine Learning SDK. In order to use datastore, please make ' \
                          + 'sure the Azure Machine Learning SDK is installed.')


def _ensure_supported(datastore: 'AbstractDatastore'):
    if _is_fs_datastore(datastore) or isinstance(datastore, AzureSqlDatabaseDatastore) \
            or isinstance(datastore, AzurePostgreSqlDatastore):
        return
    raise NotSupportedDatastoreTypeError(datastore)


def _set_auth_type(workspace: 'Workspace'):
    from .engineapi.api import get_engine_api
    from .engineapi.typedefinitions import SetAmlAuthMessageArgument, AuthType
    from azureml.core.authentication import ServicePrincipalAuthentication

    if isinstance(workspace._auth, ServicePrincipalAuthentication):
        auth = {
            'tenantId': workspace._auth._tenant_id,
            'servicePrincipalId': workspace._auth._service_principal_id,
            'password': workspace._auth._service_principal_password
        }
        get_engine_api().set_aml_auth(SetAmlAuthMessageArgument(AuthType.SERVICEPRINCIPAL, json.dumps(auth)))
    else:
        get_engine_api().set_aml_auth(SetAmlAuthMessageArgument(AuthType.DERIVED, ''))


def _all(items, predicate):
    return len(list(filter(lambda ds: not predicate(ds), items))) == 0


def _is_datapath(data_path) -> bool:
    _ensure_imported()
    return isinstance(data_path, DataReference) or \
            isinstance(data_path, AbstractDatastore) or \
            isinstance(data_path, DataPath)


def _is_datapaths(data_paths) -> bool:
    _ensure_imported()
    return type(data_paths) is list and _all(data_paths, _is_datapath)


def _is_fs_datastore(datastore: 'AbstractDatastore') -> bool:
    _ensure_imported()
    return isinstance(datastore, AzureBlobDatastore) or \
            isinstance(datastore, AzureFileDatastore) or \
            isinstance(datastore, AzureDataLakeDatastore) or \
            isinstance(datastore, AzureDataLakeGen2Datastore)


class NotSupportedDatastoreTypeError(Exception):
    def __init__(self, datastore: 'AbstractDatastore'):
        super().__init__('Datastore "{}"\'s type "{}" is not supported.'.format(datastore.name, datastore.datastore_type))
        self.datastore = datastore
