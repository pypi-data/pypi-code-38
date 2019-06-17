# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""A module that provides methods to communicate with the Dataset service."""

import logging
import logging.handlers
import os
import time
import datetime
import json
import azureml.data.constants as constants

from msrest.authentication import BasicTokenAuthentication
from msrest.exceptions import HttpOperationError
from azureml._base_sdk_common.service_discovery import get_service_url
from azureml.core.compute import ComputeTarget
from azureml.core.datastore import Datastore
from azureml._restclient.artifacts_client import ArtifactsClient
from azureml.data.azure_sql_database_datastore import AzureSqlDatabaseDatastore
from azureml.data.azure_postgre_sql_datastore import AzurePostgreSqlDatastore
from azureml.data.azure_storage_datastore import AbstractAzureStorageDatastore
from azureml.data.abstract_datastore import AbstractDatastore
from azureml.data.data_reference import DataReference
from azureml.data.dataset_type_definitions import HistogramCompareMethod
from azureml.core import Dataset
from .dataset_snapshot import DatasetSnapshot
from .dataset_definition import DatasetDefinition
from .dataset_action_run import DatasetActionRun
from azureml._restclient.rest_client import RestClient
from azureml._restclient.models.dataset_dto import DatasetDto
from azureml._restclient.models.dataset_definition_dto import DatasetDefinitionDto
from azureml._restclient.models.dataset_snapshot_request_dto import DatasetSnapshotRequestDto
from azureml._restclient.models.dataset_state_dto import DatasetStateDto
from azureml._restclient.models.dataset_definition_reference import DatasetDefinitionReference
from azureml._restclient.models.action_request_dto import ActionRequestDto
from azureml._restclient.models.action_result_update_dto import ActionResultUpdateDto
from azureml._restclient.models.sql_data_path import SqlDataPath
from azureml._restclient.models.data_path_dto import DataPathDto

from azureml.data._loggerfactory import _LoggerFactory, track

logger = None


def get_logger():
    global logger
    if logger is not None:
        return logger

    logger = _LoggerFactory.get_logger("Dataset")
    return logger


module_logger = logging.getLogger(__name__)


class _DatasetClient:
    """A client that provides methods to communicate with the Dataset service."""

    # the auth token received from _auth.get_authentication_header is prefixed
    # with 'Bearer '. This is used to remove that prefix.
    _bearer_prefix_len = 7

    @staticmethod
    def get(workspace, dataset_name=None, dataset_id=None):
        if dataset_name is None and dataset_id is None:
            raise Exception('Either the dataset_name or the dataset_id is required.')
        dataset = _DatasetClient._get(workspace, dataset_name, dataset_id)
        if dataset_id is not None and dataset_name is not None and (
                dataset_id != dataset.id or dataset_name != dataset.name):
            raise Exception('Specified Datset id and name are not matching.')
        _DatasetClient._log_to_props(dataset, 'get')
        return dataset

    @staticmethod
    def get_definitions(workspace, dataset_id, dataset=None):
        def to_dataset_definition(dto):
            ds = _DatasetClient._dto_to_dataset_definition(workspace, dto, dataset)
            _DatasetClient._log_to_props(ds, 'get_definitions')
            return ds
        client = _DatasetClient._get_client(workspace)
        dataset_definition_dto_objects = client.dataset.get_all_dataset_definitions(
            subscription_id=workspace.subscription_id,
            resource_group_name=workspace.resource_group,
            workspace_name=workspace.name,
            dataset_id=dataset_id)
        dataset_definitions = filter(lambda ds: ds is not None,
                                     map(to_dataset_definition, dataset_definition_dto_objects.value))
        return {df._version_id: df for df in list(dataset_definitions)}

    @staticmethod
    def get_definition(workspace, dataset_id, version_id, action_arguments=None, dataset=None):
        client = _DatasetClient._get_client(workspace, None, None)
        try:
            dataset_definition_dto = client.dataset.get_dataset_definition(
                subscription_id=workspace.subscription_id,
                resource_group_name=workspace.resource_group,
                workspace_name=workspace.name,
                dataset_id=dataset_id,
                version=version_id)
            dataset_def = _DatasetClient._dto_to_dataset_definition(workspace, dataset_definition_dto, dataset)
            _DatasetClient._log_to_props(dataset_def, 'get_definition')
            if (action_arguments is not None and
                'cache-datastore' in action_arguments and
                    'cache-datapath' in action_arguments):
                datastore = workspace.datastores[action_arguments['cache-datastore']]
                return _DatasetClient._add_cache_step(
                    definition=dataset_def,
                    target_datastore=datastore,
                    snapshot_path=action_arguments['cache-datapath'])
            return dataset_def
        except HttpOperationError as err:
            _DatasetClient._handle_exception(err)

    @staticmethod
    def get_dataset_definition(dataset, version_id):
        if version_id is None:
            return _DatasetClient.get(workspace=dataset.workspace, dataset_id=dataset.id).definition
        return _DatasetClient.get_definition(
            workspace=dataset.workspace,
            dataset_id=dataset.id,
            version_id=version_id,
            dataset=dataset)

    @staticmethod
    def get_dataset_definitions(dataset):
        return _DatasetClient.get_definitions(
            workspace=dataset.workspace,
            dataset_id=dataset.id,
            dataset=dataset)

    @staticmethod
    def _get_definition_json(ws, name, version=None, auth=None, host=None):
        module_logger.debug("Getting Dataset Definition JSON: {}".format(name))
        client = _DatasetClient._get_client(ws, auth, host)
        dataset_dto = client.dataset.get_dataset_by_name(
            ws._subscription_id,
            ws._resource_group,
            ws._workspace_name,
            name)
        if version is not None:
            def_dto = client.dataset.get_dataset_definition(
                ws._subscription_id,
                ws._resource_group,
                ws._workspace_name,
                dataset_dto.dataset_id,
                version)
            return def_dto.dataflow
        else:
            return dataset_dto.latest.dataflow

    @staticmethod
    def register(workspace, dataset_name, definition, description, tags, visible, exist_ok, update_if_exists):
        dataset = _DatasetClient._get(ws=workspace, name=dataset_name, throw_error=False)
        if exist_ok and dataset is not None and not update_if_exists:
            return dataset
        elif exist_ok is False and dataset is not None:
            raise Exception("A dataset with name '{0}' is already registered in the workspace".format(dataset_name))
        else:
            module_logger.debug("Registering Dataset: {}".format(dataset_name))
            dataset_definition_dto = _DatasetClient._create_dataset_definition_dto(definition)
            dataset_dto = DatasetDto(
                name=dataset_name,
                latest=dataset_definition_dto,
                description=description,
                tags=tags,
                is_visible=visible)
            client = _DatasetClient._get_client(workspace)
            dataset_dto = client.dataset.register(
                workspace.subscription_id,
                workspace.resource_group,
                workspace.name,
                dataset_dto=dataset_dto,
                if_exists_ok=exist_ok,
                update_definition_if_exists=update_if_exists)
            module_logger.debug("Dataset registration completed.")
            dataset = _DatasetClient._dto_to_dataset(workspace, dataset_dto)
            _DatasetClient._log_to_props(dataset, 'register')
            return dataset

    @staticmethod
    def update(workspace, dataset_id, dataset_name, description, tags, visible):
        client = _DatasetClient._get_client(workspace)
        dataset_dto = client.dataset.get_dataset_by_id(
            workspace._subscription_id,
            workspace._resource_group,
            workspace._workspace_name,
            dataset_id)

        if dataset_name is not None:
            dataset_dto.name = dataset_name
        if description is not None:
            dataset_dto.description = description
        if tags is not None:
            dataset_dto.tags = tags
        if visible is not None:
            dataset_dto.is_visible = visible

        dataset_dto = client.dataset.update_dataset(
            workspace.subscription_id,
            workspace.resource_group,
            workspace.name,
            dataset_id,
            new_dataset_dto=dataset_dto)
        dataset = _DatasetClient._dto_to_dataset(workspace, dataset_dto)
        _DatasetClient._log_to_props(dataset, 'update')
        return dataset

    @staticmethod
    def update_definition(dataset, new_definition, definition_update_message):
        from azureml.dataprep import Dataflow
        if isinstance(new_definition, Dataflow):
            updated_definition = _DatasetClient._get_updated_definition(dataset.definition, new_definition)
        elif isinstance(new_definition, DatasetDefinition):
            updated_definition = new_definition
        else:
            raise ValueError("Provided dataset definition is not valid.")

        if dataset.id is None:
            dataset._definition = updated_definition
            return dataset

        return _DatasetClient.update_registered_dataset_definition(
            dataset,
            updated_definition,
            definition_update_message)

    @staticmethod
    def update_registered_dataset_definition(dataset, updated_definition, definition_update_message):
        workspace = dataset.workspace
        client = _DatasetClient._get_client(workspace)
        updated_definition._notes = definition_update_message
        dataset_definition_dto = _DatasetClient._create_dataset_definition_dto(updated_definition)
        dataset_dto = client.dataset.update_definition(
            workspace.subscription_id,
            workspace.resource_group,
            workspace.name,
            dataset.id,
            dataset_definition_dto)
        dataset = _DatasetClient._dto_to_dataset(workspace, dataset_dto)
        _DatasetClient._log_to_props(dataset, 'update_definition')
        return dataset

    @staticmethod
    def update_path(dataset, path, update_message=None):
        new_definition = _DatasetClient._get_new_definition(dataset, path)
        if dataset.id is None:
            return dataset
        if update_message is None:
            update_message = 'Updated data path'
        return _DatasetClient.update_registered_dataset_definition(dataset, new_definition, update_message)

    @staticmethod
    def create_snapshot(dataset_definition, snapshot_name, compute_target=None,
                        create_data_snapshot=False, target_datastore=None):
        if dataset_definition._dataset_id is None or dataset_definition._workspace is None:
            raise ValueError('Snapshot creation is only supported for registered datasets.')
        workspace = dataset_definition._workspace
        client = _DatasetClient._get_client(workspace)
        compute_target_name = _DatasetClient._get_compute_target_name(compute_target)

        data_store = None
        if target_datastore is not None:
            if isinstance(target_datastore, AbstractDatastore):
                data_store = target_datastore
            elif isinstance(target_datastore, str):
                data_store = workspace.datastores[target_datastore]
                if data_store is None:
                    raise ValueError("Datastore could not be found with name '{}'".format(target_datastore))
            else:
                raise TypeError("Datastore should be either string or AbstractAzureStorageDatastore")

            if not isinstance(data_store, AbstractAzureStorageDatastore):
                raise TypeError("Provided datastore type is not supported for snapshot creation.")

        snapshot_request_dto = DatasetSnapshotRequestDto(
            dataset_id=dataset_definition._dataset_id,
            definition_version=dataset_definition._version_id,
            dataset_snapshot_name=snapshot_name,
            compute_target=compute_target_name,
            create_datasnapshot=create_data_snapshot,
            datastore_name=data_store.name if data_store is not None else None,
            pip_arguments=_DatasetClient._get_pip_arguments())

        try:
            snapshot_dto = client.dataset.create_dataset_snapshot(
                subscription_id=workspace.subscription_id,
                resource_group_name=workspace.resource_group,
                workspace_name=workspace.name,
                dataset_id=dataset_definition._dataset_id,
                request=snapshot_request_dto)
        except HttpOperationError as err:
            _DatasetClient._handle_exception(err)

        if compute_target is None or compute_target == 'local':
            if create_data_snapshot is True:
                dataset_definition = _DatasetClient._add_cache_step(
                    dataset_definition,
                    snapshot_name,
                    target_datastore)
            profile = _DatasetClient._execute_local_profile(dataset_definition, None)
            result_artifacts = _DatasetClient._write_to_artifact_store(
                workspace,
                snapshot_dto.dataset_id,
                snapshot_dto.profile_action_id,
                'profile',
                profile)
            _DatasetClient._update_action_result(
                workspace,
                snapshot_dto.dataset_id,
                snapshot_dto.profile_action_id,
                result_artifacts,
                dataset_definition._get_source_data_hash())
        snapshot = _DatasetClient._dto_to_dataset_snapshot(workspace, snapshot_dto)
        _DatasetClient._log_to_props(snapshot, 'create_snapshot')
        return snapshot

    @staticmethod
    def get_snapshot(workspace, snapshot_name, dataset_id=None, dataset_name=None):
        if dataset_id is None:
            if dataset_name is None:
                raise RuntimeError("Operation is only supported for registered datasets.")
            dataset = _DatasetClient._get(workspace, dataset_name)
            dataset_id = dataset.id
        client = _DatasetClient._get_client(workspace)
        snapshot_dto = client.dataset.get_dataset_snapshot(
            workspace.subscription_id,
            workspace.resource_group,
            workspace.name,
            dataset_id,
            snapshot_name)
        snapshot = _DatasetClient._dto_to_dataset_snapshot(workspace, snapshot_dto)
        _DatasetClient._log_to_props(snapshot, 'get_snapshot')
        return snapshot

    @staticmethod
    def delete_snapshot(workspace, snapshot_name, dataset_id=None, dataset_name=None):
        if dataset_id is None:
            if dataset_name is None:
                raise RuntimeError("Operation is only supported for registered datasets.")
            dataset = _DatasetClient._get(workspace, dataset_name)
            dataset_id = dataset.id
        client = _DatasetClient._get_client(workspace)
        module_logger.debug("Deleting DatasetSnapshot: '{}'".format(snapshot_name))
        client.dataset.delete_dataset_snapshot(
            workspace.subscription_id,
            workspace.resource_group,
            workspace.name,
            dataset_id,
            snapshot_name)
        module_logger.debug("DatasetSnapshot deletion completed.")

    @staticmethod
    def get_all_snapshots(workspace, dataset_id=None, dataset_name=None):
        snapshots = []
        ct = None

        while True:
            dss, ct = _DatasetClient._get_all_snapshots(
                workspace, dataset_id, dataset_name, ct, 100)
            snapshots += dss

            if not ct:
                break

        return snapshots

    @staticmethod
    def generate_profile(dataset, compute_target, workspace, arguments=None, wait_for_completion=False,
                         show_output=True, status_update_frequency=15):
        if workspace is None:
            workspace = dataset.workspace
        compute_target_name = _DatasetClient._get_compute_target_name(compute_target)
        if dataset.id is None and compute_target_name == 'local':
            action_run = DatasetActionRun()
            action_run._result = _DatasetClient._execute_local_profile(dataset.definition, arguments)
            return action_run
        else:
            if workspace is None:
                raise ValueError("Workspace should be provided for remote run of transient(unregistered) datasets.")
            # Use default uuid for transient datasets
            default_dataset_id = '00000000-0000-0000-0000-000000000000'
            dataset_id = dataset.id if dataset.id is not None else default_dataset_id
            action_dto, action_request_dto = _DatasetClient._submit_action(
                compute_target_name=compute_target_name,
                workspace=workspace,
                dataset_id=dataset_id,
                version_id=dataset.definition._version_id,
                action_type='profile',
                arguments=arguments,
                dataflow_json=dataset.definition.to_json() if dataset_id is default_dataset_id else None)
            action_run = DatasetActionRun(
                workspace, dataset_id, action_dto.action_id, action_request_dto)
            if compute_target_name == 'local':
                profile = _DatasetClient._execute_local_profile(dataset.definition, arguments)
                result_artifacts = _DatasetClient._write_to_artifact_store(
                    workspace,
                    action_dto.dataset_id,
                    action_dto.action_id,
                    action_dto.action_type,
                    profile)
                _DatasetClient._update_action_result(
                    workspace,
                    action_dto.dataset_id,
                    action_dto.action_id,
                    result_artifacts,
                    dataset.definition._get_source_data_hash())
            elif wait_for_completion:
                _DatasetClient._wait_for_completion(
                    workspace,
                    action_dto.dataset_id,
                    action_dto.action_id,
                    show_output,
                    status_update_frequency)
            return action_run

    @staticmethod
    def get_profile(workspace, dataset_id, arguments=None, version_id=None, snapshot_name=None, action_id=None):
        if dataset_id is None:
            raise Exception("Get profile is supported only for registered datasets.")
        import azureml.dataprep as dprep
        action_result_dto = _DatasetClient._get_action_result(
            workspace=workspace,
            action_id=action_id,
            dataset_id=dataset_id,
            action_type='profile',
            version_id=version_id,
            snapshot_name=snapshot_name,
            arguments=arguments)
        if _DatasetClient._is_result_available(action_result_dto) is False:
            raise Exception("Profile could not be found for the specified dataset.")
        profile_result_artifact = action_result_dto.result_artifact_ids[0]
        artifacts_client = ArtifactsClient(workspace.service_context)
        [origin, container, path] = profile_result_artifact.split("/", 2)
        profile = artifacts_client.download_artifact_contents_to_string(
            origin, container, path)
        return dprep.DataProfile._from_json(profile)

    @staticmethod
    def get_profile_with_state(dataset, arguments, generate_if_not_exist=True, workspace=None, compute_target=None):
        if dataset.id is None:
            if compute_target is None or compute_target == 'local':
                result = Dataset._client()._execute_local_profile(definition=dataset.definition, arguments=arguments)
            else:
                if workspace is None:
                    raise ValueError("Workspace should be provided for transient datasets")
                action_run = _DatasetClient.generate_profile(dataset, compute_target, workspace, arguments, True)
                result = action_run.get_result()
            result.is_up_to_date = True
            return result

        import azureml.dataprep as dprep
        workspace = workspace if dataset.id is None else dataset.workspace
        action_result_dto = _DatasetClient._get_action_result(
            workspace=workspace,
            dataset_id=dataset.id,
            action_type='profile',
            version_id=dataset.definition._version_id,
            arguments=arguments)
        if not _DatasetClient._is_result_available(action_result_dto) and generate_if_not_exist:
            action_run = _DatasetClient.generate_profile(dataset, compute_target, workspace, arguments, True)
            result = action_run.get_result()
            result.is_up_to_date = True
            return result

        profile_result_artifact = action_result_dto.result_artifact_ids[0]
        artifacts_client = ArtifactsClient(workspace.service_context)
        [origin, container, path] = profile_result_artifact.split("/", 2)
        profile_json = artifacts_client.download_artifact_contents_to_string(origin, container, path)
        profile = dprep.DataProfile._from_json(profile_json)
        profile.is_up_to_date = action_result_dto.is_up_to_date
        return profile

    @staticmethod
    def list(workspace, include_invisible=True):
        Datasets = []
        ct = None
        page_size = 100

        while True:
            dss, ct = _DatasetClient._list(workspace, ct, page_size, include_invisible)
            Datasets += dss

            if not ct:
                break

        return Datasets

    @staticmethod
    def deprecate(workspace, dataset_id, etag, deprecate_by_dataset_id):
        client = _DatasetClient._get_client(workspace, None, None)
        deprecated_by_dto = DatasetDefinitionReference(
            deprecate_by_dataset_id, definition_version=None)
        state_dto = DatasetStateDto('deprecated', deprecated_by_dto, etag)
        client.dataset.update_dataset_state(
            workspace.subscription_id,
            workspace.resource_group,
            workspace.name,
            dataset_id,
            state_dto)

    @staticmethod
    def archive(workspace, dataset_id, etag):
        client = _DatasetClient._get_client(workspace, None, None)
        state_dto = DatasetStateDto(state='archived', etag=etag)
        client.dataset.update_dataset_state(workspace.subscription_id, workspace.resource_group,
                                            workspace.name, dataset_id, state_dto)

    @staticmethod
    def reactivate(workspace, dataset_id, etag):
        client = _DatasetClient._get_client(workspace, None, None)
        state_dto = DatasetStateDto(state='active', etag=etag)
        client.dataset.update_dataset_state(workspace.subscription_id, workspace.resource_group,
                                            workspace.name, dataset_id, state_dto)

    @staticmethod
    def _get_source_path(data_flow):
        "Returns a DataPath or str"

        try:
            first_step = data_flow._steps[0]
            path = None
            if 'datastores' in first_step.arguments:
                path = first_step.arguments['datastores'][0]['path']
            elif 'datastore' in first_step.arguments:
                path = first_step.arguments['datastore']['path']
            elif 'path' in first_step.arguments:
                path = first_step.arguments['path'].resource_details[0].to_pod()['path']
            else:
                pass
            return path
        except Exception:
            return None

    @staticmethod
    def _get_source_file_type(data_flow):
        from .dataset_type_definitions import PromoteHeadersBehavior
        first_step = data_flow._steps[0]
        path = ''
        if 'datastores' in first_step.arguments:
            path = first_step.arguments['datastores'][0]['path']
        elif 'datastore' in first_step.arguments:
            path = first_step.arguments['datastore']['path']
        elif 'path' in first_step.arguments:
            path = first_step.arguments['path'].resource_details[0].to_pod()['path']
        else:
            pass
        root_path, extension = os.path.splitext(path.lower())
        if extension == '.zip':
            return "Zip"
        elif '*' in extension or '*' in root_path or not extension:
            return "Unknown"
        else:
            try:
                if first_step.step_type in {'Microsoft.DPrep.GetDatastoreFilesBlock', 'Microsoft.DPrep.GetFilesBlock'}:
                    parse_step = data_flow._steps[1]
                    if parse_step.step_type == 'Microsoft.DPrep.ParseDelimitedBlock':
                        separator = parse_step.arguments['separator']
                        header_mode = parse_step.arguments['columnHeadersMode']
                        if separator == ',' and header_mode.value == PromoteHeadersBehavior.NO_HEADERS.value:
                            return "GenericCSVNoHeader"
                        elif separator == ',' and header_mode.value != PromoteHeadersBehavior.NO_HEADERS.value:
                            return "GenericCSV"
                        elif separator == '\t' and header_mode.value == PromoteHeadersBehavior.NO_HEADERS.value:
                            return "GenericTSVNoHeader"
                        elif separator == '\t' and header_mode.value != PromoteHeadersBehavior.NO_HEADERS.value:
                            return "GenericTSV"
                        else:
                            return "Unknown"
                    else:
                        return "Unknown"
                else:
                    return "Unknown"
            except Exception:
                return "Unknown"

    @staticmethod
    def from_pandas_dataframe(
            dataframe,
            path=None):

        from azureml.data.data_reference import DataReference
        import azureml.dataprep as dprep
        import os
        import uuid

        local_file_path = None
        dataflow = None

        if isinstance(path, DataReference):
            ds_file_head, ds_file_tail = os.path.split(path.path_on_datastore)
            if ds_file_tail.strip():
                raise Exception(
                    'dataReference path_on_datastore should be relative path for upload.: {}'.format(
                        path.path_on_datastore))
            temp = os.path.join(os.getcwd(), uuid.uuid4().hex, 'temp_dataset_from_pandas')
            local_file_path = _DatasetClient._create_local_file_from_pandas_dataframe(
                local_folder_path=temp, dataframe=dataframe)
            local_file_head, local_file_tail = os.path.split(local_file_path)
            path.datastore.upload(
                src_dir=temp,
                target_path=ds_file_head,
                overwrite=False)
            print("{}{} has been uploaded to {} ".format(
                local_file_head, local_file_tail, ds_file_head))
            ref = path.datastore.path(os.path.join(ds_file_head, local_file_tail))
            dataflow = dprep.read_csv(path=ref)
            return _DatasetClient._get_dataset_from_dataflow(
                dataflow=dataflow,
                file_data_path=ref)
        elif path is not None:
            local_file_path = _DatasetClient._create_local_file_from_pandas_dataframe(
                local_folder_path=path, dataframe=dataframe)
            dataflow = dprep.read_csv(path=local_file_path)
            return _DatasetClient._get_dataset_from_dataflow(
                dataflow=dataflow,
                file_data_path=local_file_path)
        else:
            temp = os.path.join(os.getcwd(), uuid.uuid4().hex, 'temp_dataset_from_pandas')
            local_file_path = _DatasetClient._create_local_file_from_pandas_dataframe(
                local_folder_path=temp, dataframe=dataframe)
            dataflow = dprep.read_csv(path=local_file_path)
            return _DatasetClient._get_dataset_from_dataflow(
                dataflow=dataflow,
                file_data_path=local_file_path)

        if os.path.exists(local_file_path):
            os.remove(local_file_path)

    @staticmethod
    def _create_local_file_from_pandas_dataframe(local_folder_path, dataframe):

        import os
        import uuid
        import shutil

        if os.path.isdir(local_folder_path):
            shutil.rmtree(path=local_folder_path)
        os.makedirs(name=local_folder_path, exist_ok=True)

        local_file_path = os.path.join(local_folder_path, '{}.csv'.format(uuid.uuid4().hex))

        dataframe.to_csv(
            path_or_buf=local_file_path,
            sep=',',
            header=True,
            index=False)
        return local_file_path

    @staticmethod
    def from_delimited_files(
            path,
            separator,
            header,
            encoding,
            quoting,
            infer_column_types,
            skip_rows,
            skip_mode,
            comment,
            include_path,
            archive_options):
        import azureml.dataprep as dprep
        inference_arguments = None
        if infer_column_types:
            inference_arguments = dprep.InferenceArguments(day_first=True)
        dataflow = dprep.read_csv(
            path,
            separator,
            header,
            encoding,
            quoting,
            inference_arguments,
            skip_rows,
            skip_mode,
            comment,
            include_path,
            archive_options)

        file_type = _DatasetClient._get_source_file_type(dataflow)
        # TODO Implement PromoteHeadersBehavior.NoHeaders
        return _DatasetClient._get_dataset_from_dataflow(dataflow=dataflow, file_data_path=path, file_type=file_type)

    @staticmethod
    def auto_read_files(path, include_path):
        import azureml.dataprep as dprep
        dataflow = dprep.auto_read_file(path, include_path)
        file_type = _DatasetClient._get_source_file_type(dataflow)
        return _DatasetClient._get_dataset_from_dataflow(
            dataflow=dataflow,
            file_data_path=path,
            file_type=file_type)

    @staticmethod
    def from_parquet_files(path, include_path):
        import azureml.dataprep as dprep
        dataflow = dprep.read_parquet_file(path, include_path)
        return _DatasetClient._get_dataset_from_dataflow(
            dataflow=dataflow,
            file_data_path=path)

    @staticmethod
    def from_parquet_datasets(path, include_path):
        import azureml.dataprep as dprep
        dataflow = dprep.read_parquet_dataset(path, include_path)
        return _DatasetClient._get_dataset_from_dataflow(
            dataflow=dataflow,
            file_data_path=path)

    @staticmethod
    def from_excel_files(path, sheet_name, use_column_headers, skip_rows, include_path, infer_column_types):
        import azureml.dataprep as dprep
        inference_arguments = None
        if infer_column_types:
            inference_arguments = dprep.InferenceArguments(day_first=True)
        dataflow = dprep.read_excel(
            path, sheet_name, use_column_headers, inference_arguments, skip_rows, include_path)
        dataflow._name = sheet_name
        return _DatasetClient._get_dataset_from_dataflow(
            dataflow=dataflow,
            file_data_path=path)

    @staticmethod
    def from_binary_files(path):
        import azureml.dataprep as dprep
        dataflow = dprep.Dataflow.get_files(path)
        return _DatasetClient._get_dataset_from_dataflow(
            dataflow=dataflow,
            file_data_path=path)

    @staticmethod
    def from_sql_query(data_source, query):
        import azureml.dataprep as dprep
        if isinstance(data_source, AzureSqlDatabaseDatastore):
            dataflow = dprep.read_sql(data_source, query)
        elif isinstance(data_source, AzurePostgreSqlDatastore):
            # TODO: Update the below code once the Dataprep is ready with AzurePostgreSql support.
            dataflow = None
        else:
            raise TypeError("Provided datastore in not supported.")

        sql_data_path = SqlDataPath(sql_query=query)
        return _DatasetClient._get_dataset_from_dataflow(
            dataflow=dataflow,
            sql_data_path=sql_data_path,
            sql_data_store=data_source)

    @staticmethod
    def from_json_files(path, encoding, flatten_nested_arrays, include_path):
        import azureml.dataprep as dprep
        dataflow = dprep.read_json(path, encoding, flatten_nested_arrays, include_path)
        return _DatasetClient._get_dataset_from_dataflow(
            dataflow=dataflow,
            file_data_path=path)

    @staticmethod
    @track(get_logger)
    def to_pandas_dataframe(definition):
        return definition.to_pandas_dataframe()

    @staticmethod
    def head(definition, count=5):
        return definition.head(count)

    @staticmethod
    @track(get_logger)
    def to_spark_dataframe(definition):
        return definition.to_spark_dataframe()

    @staticmethod
    def sample(dataset, sample_strategy, arguments, file_type):
        import azureml.dataprep as dprep
        if dataset.id is None:
            new_dataflow = dataset.definition
        else:
            new_dataflow = dprep.Dataflow.reference(dprep.ExternalReference('dataset://{}/{}/{}/{}'.format(
                dataset.workspace.subscription_id, dataset.workspace.resource_group, dataset.workspace.name,
                dataset.name)))
        if sample_strategy.lower() == 'top_n':
            if 'n' not in arguments:
                raise Exception('n for {} sample strategy is not defined.'.format(sample_strategy))
            new_dataflow = new_dataflow.take(arguments['n'])
        elif sample_strategy.lower() == 'simple_random':
            if 'probability' not in arguments:
                raise Exception('probability for {} sample strategy is not defined.'.format(sample_strategy))
            seed = arguments['seed'] if 'seed' in arguments else None
            new_dataflow = new_dataflow.take_sample(arguments['probability'], seed)
        elif sample_strategy.lower() == 'stratified':
            for argument in ['columns', 'fractions']:
                if argument not in arguments:
                    raise Exception('{} for {} sample strategy is not defined.'.format(argument, sample_strategy))
            seed = arguments['seed'] if 'seed' in arguments else None
            new_dataflow = new_dataflow.take_stratified_sample(arguments['columns'], arguments['fractions'], seed)
        else:
            raise Exception('Sample strategy: {} is not supported.'.format(sample_strategy))

        dataset_definition = DatasetDefinition(dataflow=new_dataflow, file_type=file_type)
        return Dataset(definition=dataset_definition)

    @staticmethod
    def get_datapath(workspace, dataset_id, definition_version):
        if workspace is None:
            raise ValueError("Invalid workspace.")
        if dataset_id is None:
            raise ValueError("Invalid dataset id.")
        if definition_version is None:
            raise ValueError("Invalid Dataset definition version.")
        client = _DatasetClient._get_client(workspace)
        data_path_dto = client.dataset.get_data_path(
            workspace.subscription_id,
            workspace.resource_group,
            workspace.name,
            dataset_id,
            definition_version)
        return data_path_dto

    @staticmethod
    def _get(ws, name=None, id=None, throw_error=True):
        try:
            if ws is None:
                raise ValueError("Workspace should be provided.")

            if name is None and id is None:
                raise ValueError("Either name or id should be provided.")

            module_logger.debug("Getting Dataset: {}".format(name))
            client = _DatasetClient._get_client(ws)

            if(name is not None):
                dataset_dto = client.dataset.get_dataset_by_name(ws._subscription_id, ws._resource_group,
                                                                 ws._workspace_name, name)
            else:
                dataset_dto = client.dataset.get_dataset_by_id(ws._subscription_id, ws._resource_group,
                                                               ws._workspace_name, id)

            module_logger.debug("Received Dataset from the service.")
            return _DatasetClient._dto_to_dataset(ws, dataset_dto)

        except HttpOperationError as err:
            if err.response.status_code == 404 and (throw_error is False):
                return None
            else:
                raise err

    @staticmethod
    def _list(workspace, continuation_token, page_size, include_invisible):
        def to_dataset(dto):
            dataset = _DatasetClient._dto_to_dataset(workspace, dto)
            _DatasetClient._log_to_props(dataset, 'list')
            return dataset
        client = _DatasetClient._get_client(workspace)
        dataset_dto_objects = client.dataset.list(
            subscription_id=workspace.subscription_id,
            resource_group_name=workspace.resource_group,
            workspace_name=workspace.name,
            continuation_token=continuation_token,
            page_size=page_size,
            include_invisible=include_invisible)
        datasets = filter(lambda ds: ds is not None, map(
            to_dataset, dataset_dto_objects.value))
        return list(datasets), dataset_dto_objects.continuation_token

    @staticmethod
    def _get_dataset_from_dataflow(
            dataflow,
            file_data_path=None,
            sql_data_path=None,
            sql_data_store=None,
            file_type="Unknown"):
        data_path = _DatasetClient._get_data_path(file_data_path, sql_data_path, sql_data_store)
        dataset_definition = DatasetDefinition(dataflow=dataflow, data_path=data_path, file_type=file_type)
        return Dataset(definition=dataset_definition)

    @staticmethod
    def _get_data_path(file_data_path=None, sql_data_path=None, sql_data_store=None):
        data_path = DataPathDto()
        if file_data_path is not None:
            if isinstance(file_data_path, str):
                data_path.relative_path = file_data_path
            elif isinstance(file_data_path, DataReference):
                data_path.datastore_name = file_data_path.datastore.name
                data_path.relative_path = file_data_path.path_on_datastore
            else:
                raise TypeError("Path should be either string or azureml.data.data_reference.Datareference")
        elif sql_data_path is not None:
            data_path.sql_data_path = sql_data_path
        else:
            raise ValueError("Path should be provided.")

        if sql_data_store is not None:
            data_path.datastore_name = sql_data_store.name
        return data_path

    @staticmethod
    def _get_new_definition(dataset, data_path):
        dflow = None
        is_dataflow_supported_path = True
        if isinstance(data_path, str):
            data_path = _DatasetClient._get_data_path(file_data_path=data_path)
        elif isinstance(data_path, DataReference):
            if isinstance(data_path.datastore, AzureSqlDatabaseDatastore):
                data_path = _DatasetClient._get_data_path(
                    sql_data_path=data_path.datastore.path_on_compute,
                    sql_data_store=data_path.datastore)
            elif isinstance(data_path.datastore, AzurePostgreSqlDatastore):
                is_dataflow_supported_path = False
                data_path = _DatasetClient._get_data_path(
                    sql_data_path=data_path.datastore.path_on_compute,
                    sql_data_store=data_path.datastore)
            elif isinstance(data_path.datastore, AbstractAzureStorageDatastore):
                data_path = _DatasetClient._get_data_path(file_data_path=data_path)
            else:
                raise RuntimeError("Unsupported datastore.")
        else:
            raise TypeError("Datapath should be either string or azureml.data.data_reference.Datareference")

        if is_dataflow_supported_path:
            dflow = dataset.definition.replace_datasource(data_path)

        dataset._definition = _DatasetClient._get_updated_definition(dataset.definition, dflow)

    @staticmethod
    def _dto_to_dataset(workspace, dataset_dto):
        dataset = Dataset(workspace=workspace, name=dataset_dto.name, id=dataset_dto.dataset_id,
                          definition=_DatasetClient._dto_to_dataset_definition(workspace, dataset_dto.latest))
        dataset._description = dataset_dto.description
        dataset._is_visible = dataset_dto.is_visible
        dataset._default_compute = dataset_dto.default_compute
        dataset._tags = dataset_dto.tags
        dataset._created_time = dataset_dto.created_time
        dataset._modified_time = dataset_dto.modified_time
        dataset._etag = dataset_dto.etag
        state_dto = dataset_dto.dataset_state
        if state_dto is not None:
            dataset._state = state_dto.state
            deprecated_by = state_dto.deprecated_by
            dataset._deprecated_by_dataset_id = deprecated_by.dataset_id if deprecated_by is not None else None
            dataset._deprecated_by_definition = (deprecated_by.definition_version
                                                 if deprecated_by is not None
                                                 else None)
        return dataset

    @staticmethod
    def _dto_to_dataset_definition(workspace, def_dto, dataset=None):
        dataset_definition = None
        if def_dto is not None:
            state_dto = def_dto.dataset_definition_state if def_dto is not None else None
            deprecated_by = state_dto.deprecated_by if state_dto is not None else None
            state = state_dto.state if state_dto is not None else None
            deprecated_by_dataset_id = deprecated_by.dataset_id if deprecated_by is not None else None
            deprecated_by_definition = deprecated_by.definition_version if deprecated_by is not None else None

            dataset_definition = DatasetDefinition(
                workspace=workspace,
                dataset_id=def_dto.dataset_id,
                version_id=def_dto.version_id,
                dataflow_json=def_dto.dataflow,
                notes=def_dto.notes,
                etag=def_dto.etag,
                created_time=def_dto.created_time,
                modified_time=def_dto.modified_time,
                state=state,
                deprecated_by_dataset_id=deprecated_by_dataset_id,
                deprecated_by_definition_version=deprecated_by_definition,
                data_path=def_dto.data_path,
                dataset=dataset,
                file_type=def_dto.file_type)
        return dataset_definition

    @staticmethod
    def _archive_definition(definition):
        workspace = definition._workspace
        client = _DatasetClient._get_client(workspace)
        state_dto = DatasetStateDto(state='archived', etag=definition._etag)
        client.dataset.update_definition_state(workspace.subscription_id, workspace.resource_group, workspace.name,
                                               definition._dataset_id, definition._version_id, state_dto)

    @staticmethod
    def _deprecate_definition(definition, deprecate_by_dataset_id, deprecated_by_definition_version=None):
        workspace = definition._workspace
        client = _DatasetClient._get_client(workspace)
        deprecated_by_dto = DatasetDefinitionReference(
            deprecate_by_dataset_id, deprecated_by_definition_version)
        state_dto = DatasetStateDto(
            'deprecated', deprecated_by_dto, definition._etag)
        client.dataset.update_definition_state(workspace.subscription_id, workspace.resource_group, workspace.name,
                                               definition._dataset_id, definition._version_id, state_dto)
        definition._deprecated_by_dataset_id = deprecate_by_dataset_id
        definition._deprecated_by_definition_version = deprecated_by_definition_version

    @staticmethod
    def _reactivate_definition(definition):
        workspace = definition._workspace
        client = _DatasetClient._get_client(workspace)
        state_dto = DatasetStateDto(state='active', etag=definition._etag)
        client.dataset.update_definition_state(workspace.subscription_id, workspace.resource_group, workspace.name,
                                               definition._dataset_id, definition._version_id, state_dto)

    @staticmethod
    def _add_cache_step(definition, snapshot_name=None, target_datastore=None, snapshot_path=None):
        if target_datastore is None:
            target_datastore = definition._workspace.get_default_datastore()
        if snapshot_path is None:
            if snapshot_name is None:
                raise ValueError("Either snapshot path or snapshot name should be provided.")
            snapshot_path = _DatasetClient._get_snapshot_path(definition._dataset_id, snapshot_name)
        import azureml.dataprep as dprep
        data_reference = target_datastore.path(snapshot_path)
        _, datastore_value = dprep.api._datastore_helper.get_datastore_value(data_reference)
        return definition.add_step(
            'Microsoft.DPrep.WriteDataSetToDatastoreBlock',
            {'datastore': datastore_value._to_pod(), 'columnsToIntern': ['Path']})

    @staticmethod
    # TODO: Remove this method once Web API is ready for data snapshots
    def _get_snapshot_path(dataset_id, snapshot_name):
        return 'DatasetSnapshots/{0}/{1}'.format(dataset_id, snapshot_name)

    @staticmethod
    def _get_all_snapshots(workspace, dataset_id=None, dataset_name=None, continuation_token=None, page_size=None):
        def to_dataset_snapshot(dto):
            snapshot = _DatasetClient._dto_to_dataset_snapshot(workspace, dto)
            _DatasetClient._log_to_props(snapshot, 'get_snapshots')
            return snapshot
        if dataset_id is None:
            if dataset_name is None:
                raise RuntimeError("Operation is only supported for registered datasets.")
            dataset = _DatasetClient._get(workspace, dataset_name)
            dataset_id = dataset.id
        client = _DatasetClient._get_client(workspace, None, None)
        snapshot_dto_objects = client.dataset.get_all_dataset_snapshots(
            workspace.subscription_id,
            workspace.resource_group,
            workspace.name, dataset_id,
            continuation_token,
            page_size)
        dataset_snapshots = filter(lambda ds: ds is not None, map(
            to_dataset_snapshot, snapshot_dto_objects.value))
        return (list(dataset_snapshots), snapshot_dto_objects.continuation_token)

    @staticmethod
    def _dto_to_dataset_snapshot(workspace, snapshot_dto):
        datastore_name = None
        relative_path = None

        if snapshot_dto.data_snapshot_path is not None:
            datastore_name = snapshot_dto.data_snapshot_path.datastore_name
            relative_path = snapshot_dto.data_snapshot_path.relative_path

        dataset_snapshot = DatasetSnapshot(
            workspace,
            snapshot_dto.dataset_snapshot_name,
            snapshot_dto.dataset_id,
            snapshot_dto.definition_version,
            snapshot_dto.created_time,
            snapshot_dto.profile_action_id,
            datastore_name,
            relative_path)
        return dataset_snapshot

    @staticmethod
    def _execute_local_profile(definition, arguments):
        if arguments is None or 'number_of_histogram_bins' not in arguments:
            return definition.get_profile()
        else:
            number_of_histogram_bins = arguments['number_of_histogram_bins']
            return definition.get_profile(number_of_histogram_bins=number_of_histogram_bins)

    @staticmethod
    def _submit_action(
        compute_target_name,
        workspace,
        dataset_id,
        version_id,
        action_type,
        arguments,
        dataflow_json=None,
        dataset_snapshot_name=None
    ):
        action_request_dto = ActionRequestDto(
            action_type=action_type,
            arguments=arguments,
            definition_version=version_id,
            dataflow_json=dataflow_json,
            compute_target=compute_target_name,
            dataset_snapshot_name=dataset_snapshot_name,
            pip_arguments=_DatasetClient._get_pip_arguments())
        client = _DatasetClient._get_client(workspace)
        try:
            action_dto = client.dataset.submit_action(
                workspace.subscription_id,
                workspace.resource_group,
                workspace.name,
                dataset_id,
                action_request_dto)
        except HttpOperationError as err:
            _DatasetClient._handle_exception(err)
        return action_dto, action_request_dto

    @staticmethod
    def _write_to_artifact_store(
        workspace,
        dataset_id,
        action_id,
        action_type,
        data
    ):
        outfile = 'actions/{}/{}_result.json'.format(action_id, action_type)
        os.makedirs(os.path.dirname(outfile))

        result_artifacts = []
        artifacts_client = ArtifactsClient(
            workspace.service_context)
        artifact = artifacts_client.create_empty_artifacts(
            origin='Dataset',
            container=dataset_id,
            paths=[outfile]).artifacts[outfile]
        with open(outfile, 'w') as result_artifact:
            if(isinstance(data, str)):
                result_artifact.write(data)
            else:
                result_artifact.write(data._to_json())
        artifacts_client.upload_files(
            paths=[artifact.path], origin=artifact.origin, container=artifact.container)
        os.remove(outfile)
        result_artifacts.append(artifact.artifact_id)

        return result_artifacts

    @staticmethod
    def _get_compute_target_name(compute_target):
        compute_target_name = 'local'
        if compute_target is not None:
            if isinstance(compute_target, ComputeTarget):
                compute_target_name = compute_target.name
            else:
                compute_target_name = compute_target
        return compute_target_name

    @staticmethod
    def _get_profile(
            workspace,
            dataset_id,
            arguments=None,
            version_id=None,
            snapshot_name=None,
            action_id=None):
        if dataset_id is None:
            raise Exception("Get profile is supported only for registered datasets.")
        import azureml.dataprep as dprep
        action_result_dto = _DatasetClient._get_action_result(
            workspace=workspace,
            action_id=action_id,
            dataset_id=dataset_id,
            action_type='profile',
            version_id=version_id,
            snapshot_name=snapshot_name,
            arguments=arguments)
        if _DatasetClient._is_result_available(action_result_dto) is False:
            raise Exception("Profile could not be found for the specified dataset.")
        profile_result_artifact = action_result_dto.result_artifact_ids[0]
        artifacts_client = ArtifactsClient(workspace.service_context)
        [origin, container, path] = profile_result_artifact.split("/", 2)
        profile = artifacts_client.download_artifact_contents_to_string(
            origin, container, path)
        return dprep.DataProfile._from_json(profile)

    @staticmethod
    def _get_profile_diff_result(
        workspace,
        action_id,
        dataset_id,
        action_request_dto,
    ):
        action_result_dto = _DatasetClient._get_action_result(
            workspace=workspace,
            action_id=action_id,
            dataset_id=dataset_id,
            action_type='diff',
            version_id=None,
            snapshot_name=None,
            arguments=action_request_dto.arguments)

        if _DatasetClient._is_result_available(action_result_dto) is False:
            raise Exception(
                "Diff Result could not be found for the specified dataset.")
        profile_diff_result_artifact = action_result_dto.result_artifact_ids[0]
        artifacts_client = ArtifactsClient(workspace.service_context)
        [origin, container, path] = profile_diff_result_artifact.split("/", 2)
        diff_result = artifacts_client.download_artifact_contents_to_string(
            origin, container, path)
        from ._data_profile_difference_json_helper import _DataProfileDifferenceJsonHelper
        return _DataProfileDifferenceJsonHelper.from_json(diff_result)

    @staticmethod
    def _get_action_result(workspace, dataset_id, action_id=None, action_type='profile',
                           arguments=None, version_id=None, snapshot_name=None):
        if dataset_id is None:
            raise ValueError("Dataset id should be provided.")

        client = _DatasetClient._get_client(workspace, None, None)
        if action_id is not None:
            try:
                action_dto = client.dataset.get_action_by_id(
                    workspace.subscription_id,
                    workspace.resource_group,
                    workspace.name,
                    dataset_id,
                    action_id)
            except HttpOperationError as err:
                _DatasetClient._handle_exception(err)
            if action_dto is None or action_dto.status is None:
                raise Exception(action_type + " action could not be found.")
            elif action_dto.status == "Failed":
                if action_dto.error is None or action_dto.error.error is None:
                    raise Exception(
                        '{} action failed. Dataset id: {}, Action id: {}, error unavailable.'.format(
                            action_dto.action_type, dataset_id, action_id))
                else:
                    raise Exception(
                        '{} action failed. Dataset id: {}, Action id: {}, {}: {}.'.format(
                            action_dto.action_type,
                            dataset_id,
                            action_id,
                            action_dto.error.error.code,
                            action_dto.error.error.message))
            return action_dto
        else:
            action_request_dto = ActionRequestDto(
                action_type=action_type,
                definition_version=version_id,
                dataset_snapshot_name=snapshot_name,
                arguments=arguments or dict())
            try:
                action_result_dto = client.dataset.get_action_result(
                    workspace.subscription_id,
                    workspace.resource_group,
                    workspace.name,
                    dataset_id,
                    action_request_dto)
            except HttpOperationError as err:
                _DatasetClient._handle_exception(err)
            return action_result_dto

    @staticmethod
    def _is_result_available(action_result_dto):
        if action_result_dto is None or action_result_dto.result_artifact_ids is None:
            return False
        return len(action_result_dto.result_artifact_ids) > 0

    @staticmethod
    def _wait_for_completion(workspace, dataset_id, action_id, show_output=True, status_update_frequency=5):
        if workspace is None:
            raise ValueError("Workspace should be provided.")
        if dataset_id is None:
            raise ValueError("Dataset id should be provided.")
        if action_id is None:
            raise ValueError("Action id should be provided.")
        action_status = None
        client = _DatasetClient._get_client(workspace, None, None)
        while action_status != 'Completed' and action_status != 'Failed' and action_status != 'Canceled':
            if action_status is not None:
                time.sleep(status_update_frequency)
            action_dto = client.dataset.get_action_by_id(
                workspace.subscription_id,
                workspace.resource_group,
                workspace.name,
                dataset_id,
                action_id)
            action_status = action_dto.status
            if show_output:
                print('Action status: ' + action_status)
        if action_status == "Failed":
            if action_dto.error is None or action_dto.error.error is None:
                raise Exception(
                    '{} action failed. Dataset id: {}, Action id: {}, error unavailable.'.format(
                        action_dto.action_type, dataset_id, action_id))
            else:
                raise Exception(
                    '{} action failed. Dataset id: {}, Action id: {}, {}: {}.'.format(
                        action_dto.action_type,
                        dataset_id,
                        action_id,
                        action_dto.error.error.code,
                        action_dto.error.error.message))

    @staticmethod
    def _get_snapshot_status(workspace, dataset_id, profile_action_id):
        client = _DatasetClient._get_client(workspace)
        action_dto = client.dataset.get_action_by_id(
            workspace.subscription_id,
            workspace.resource_group,
            workspace.name,
            dataset_id,
            profile_action_id)
        if action_dto is None or action_dto.status is None:
            raise Exception("Profile action could not be found.")
        return action_dto.status

    @staticmethod
    def _get_dataflow(workspace, datastore_name, relative_path):
        if datastore_name is None:
            raise ValueError("Invalid datastore name.")
        if relative_path is None:
            raise ValueError("Invalid path.")
        import azureml.dataprep as dprep
        dstore = Datastore.get(workspace, datastore_name)
        path = dstore.path(relative_path + '/part*')
        dataflow = dprep.api._datastore_helper.datastore_to_dataflow(path)
        return dataflow.add_step('Microsoft.DPrep.ParseDataSetBlock', {})

    @staticmethod
    def _get_action_by_id(workspace, dataset_id, action_id):
        client = _DatasetClient._get_client(workspace)
        return client.dataset.get_action_by_id(
            subscription_id=workspace.subscription_id,
            resource_group_name=workspace.resource_group,
            workspace_name=workspace.name,
            dataset_id=dataset_id,
            action_id=action_id)

    @staticmethod
    def _update_action_result(workspace, dataset_id, action_id, result_artifact_ids, target_data_hash):
        client = _DatasetClient._get_client(workspace)
        result_update_dto = ActionResultUpdateDto(
            result_artifact_ids=result_artifact_ids,
            target_data_hash=target_data_hash)
        client.dataset.update_action_result(
            subscription_id=workspace.subscription_id,
            resource_group_name=workspace.resource_group,
            workspace_name=workspace.name,
            dataset_id=dataset_id,
            action_id=action_id,
            result_update_dto=result_update_dto)

    @staticmethod
    def compare_dataset_profiles(
        lhs_dataset,
        rhs_dataset,
        profile_arguments=dict(),
        compute_target=None,
        include_columns=None,
        exclude_columns=None,
        histogram_compare_method=HistogramCompareMethod.WASSERSTEIN
    ):
        """
        Compare the Profiles of the given two datasets.

        :param lhs_dataset: LHS dataset.
        :type lhs_dataset: Dataset
        :param rhs_dataset: RHS dataset
        :type rhs_dataset: Dataset
        :param compute_target: compute target to perform the profile diff, optional.
        :type compute_target: azureml.core.compute.ComputeTarget or str
        :param include_columns: List of column names to be included in comparison.
        :type include_columns: List[str]
        :param exclude_columns: List of column names to be excluded in comparison.
        :type exclude_columns: List[str]
        :param histogram_compare_method: Enum describing the method, ex: Wasserstein or Energy
        :type histogram_compare_method: azureml.dataprep.api.typedefinitions.HistogramCompareMethod
        :return: Difference of the profiles.
        :rtype: azureml.dataprep.api.typedefinitions.DataProfileDifference
        """
        compute_target_name = _DatasetClient._get_compute_target_name(
            compute_target)
        if(lhs_dataset._id is None or rhs_dataset._id is None):
            raise Exception(
                "For Unregistered datasets use profile.Compare method.")
        else:
            arguments = dict()
            arguments.update({"is_dataset_diff": True})
            arguments.update({"rhs_dataset_id": rhs_dataset.id})
            arguments.update({"rhs_dataset_definition_version": rhs_dataset.definition_version})
            arguments.update({"include_columns": include_columns})
            arguments.update({"exclude_columns": exclude_columns})
            arguments.update({"histogram_compare_method": histogram_compare_method})
            arguments.update({"profile_arguments": profile_arguments})

            action_dto, action_request_dto = _DatasetClient._submit_action(
                compute_target_name=compute_target_name,
                workspace=lhs_dataset._workspace,
                dataset_id=lhs_dataset.id,
                version_id=lhs_dataset._definition._version_id,
                action_type='diff',
                arguments=arguments)

            action_run = DatasetActionRun(
                lhs_dataset.workspace, lhs_dataset.id, action_dto.action_id, action_request_dto)

            if compute_target_name is None or compute_target_name == 'local':
                _DatasetClient._execute_diff_local(
                    lhs_dataset_or_snapshot=lhs_dataset,
                    rhs_dataset_or_snapshot=rhs_dataset,
                    profile_arguments=profile_arguments,
                    include_columns=include_columns,
                    exclude_columns=exclude_columns,
                    histogram_compare_method=histogram_compare_method,
                    action_run=action_run,
                    dataset_id=action_run._dataset_id,
                    action_id=action_run._action_id
                )
                return action_run
            else:
                return action_run

    @staticmethod
    def compare_dataset_snapshot_profiles(
        lhs_dataset_snapshot,
        rhs_dataset_snapshot,
        dataset_snapshot_name,
        compute_target=None,
        include_columns=None,
        exclude_columns=None,
        histogram_compare_method=HistogramCompareMethod.WASSERSTEIN
    ):
        """
        Compare the Profiles of the given two datasets.

        :param lhs_dataset_snapshot: LHS dataset snapshot.
        :type lhs_dataset_snapshot: Datasetsnapshot
        :param rhs_dataset_snapshot: RHS dataset snapshot
        :type rhs_dataset_snapshot: Datasetsnapshot
        :param compute_target: compute target to perform the profile diff, optional.
        :type compute_target: azureml.core.compute.ComputeTarget or str
        :param include_columns: List of column names to be included in comparison.
        :type include_columns: List[str]
        :param exclude_columns: List of column names to be excluded in comparison.
        :type exclude_columns: List[str]
        :param histogram_compare_method: Enum describing the method, ex: Wasserstein or Energy
        :type histogram_compare_method: azureml.dataprep.api.typedefinitions.HistogramCompareMethod
        :return: Difference of the profiles.
        :rtype: azureml.dataprep.api.typedefinitions.DataProfileDifference
        """
        compute_target_name = _DatasetClient._get_compute_target_name(
            compute_target)
        if(lhs_dataset_snapshot._dataset_id is None or rhs_dataset_snapshot._dataset_id is None):
            raise Exception(
                "For Unregistered datasets use profile.Compare method.")
        else:
            arguments = dict()
            arguments.update({"is_dataset_diff": False})
            arguments.update({"rhs_dataset_id": rhs_dataset_snapshot._dataset_id})
            arguments.update({"rhs_dataset_snapsnot_name": rhs_dataset_snapshot._name})
            arguments.update({"include_columns": include_columns})
            arguments.update({"exclude_columns": exclude_columns})
            arguments.update({"histogram_compare_method": histogram_compare_method})
            arguments.update({"profile_arguments": None})

            action_dto, action_request_dto = _DatasetClient._submit_action(
                compute_target_name=compute_target_name,
                workspace=lhs_dataset_snapshot._workspace,
                dataset_id=lhs_dataset_snapshot._dataset_id,
                version_id=lhs_dataset_snapshot._definition_version,
                action_type='diff',
                arguments=arguments,
                dataset_snapshot_name=dataset_snapshot_name)

            action_run = DatasetActionRun(
                workspace=lhs_dataset_snapshot._workspace,
                dataset_id=lhs_dataset_snapshot._dataset_id,
                action_id=action_dto.action_id,
                action_request_dto=action_request_dto)

            if compute_target_name is None or compute_target_name == 'local':
                _DatasetClient._execute_diff_local(
                    lhs_dataset_or_snapshot=lhs_dataset_snapshot,
                    rhs_dataset_or_snapshot=rhs_dataset_snapshot,
                    profile_arguments=None,
                    include_columns=include_columns,
                    exclude_columns=exclude_columns,
                    histogram_compare_method=histogram_compare_method,
                    action_run=action_run,
                    dataset_id=action_run._dataset_id,
                    action_id=action_run._action_id
                )
                return action_run
            else:
                return action_run

    @staticmethod
    def _execute_diff_local(
        lhs_dataset_or_snapshot,
        rhs_dataset_or_snapshot,
        profile_arguments,
        include_columns,
        exclude_columns,
        histogram_compare_method,
        action_run,
        dataset_id,
        action_id
    ):
        lhs_profile = None
        rhs_profile = None

        if isinstance(lhs_dataset_or_snapshot, DatasetDefinition):
            lhs_profile = _DatasetClient._get_profile(
                workspace=lhs_dataset_or_snapshot._workspace,
                dataset_id=dataset_id,
                arguments=profile_arguments,
                version_id=lhs_dataset_or_snapshot._version_id)

            rhs_profile = _DatasetClient._get_profile(
                workspace=rhs_dataset_or_snapshot._workspace,
                dataset_id=dataset_id,
                arguments=profile_arguments,
                version_id=rhs_dataset_or_snapshot._version_id)
        elif isinstance(lhs_dataset_or_snapshot, DatasetSnapshot):
            lhs_profile = lhs_dataset_or_snapshot.get_profile()
            rhs_profile = rhs_dataset_or_snapshot.get_profile()
        else:
            lhs_profile = lhs_dataset_or_snapshot.get_profile(arguments=profile_arguments)
            rhs_profile = rhs_dataset_or_snapshot.get_profile(arguments=profile_arguments)

        import azureml.dataprep as dprep
        histogram_compare_method_dprep = dprep.HistogramCompareMethod(histogram_compare_method.value)
        diff_result = lhs_profile.compare(
            rhs_profile,
            include_columns=include_columns,
            exclude_columns=exclude_columns,
            histogram_compare_method=histogram_compare_method_dprep)
        from ._data_profile_difference_json_helper import _DataProfileDifferenceJsonHelper
        result_json = _DataProfileDifferenceJsonHelper.to_json(diff_result)
        result_artifacts = _DatasetClient._write_to_artifact_store(
            lhs_dataset_or_snapshot._workspace,
            dataset_id,
            action_id,
            'diff',
            result_json)
        _DatasetClient._update_action_result(
            lhs_dataset_or_snapshot._workspace,
            dataset_id,
            action_id,
            result_artifacts,
            datetime.datetime.today().strftime('%Y%m%d%H%M'))
        if action_run is not None:
            action_run._result = diff_result
        return result_artifacts

    @staticmethod
    def execute_diff_action(workspace, action):
        include_columns = None
        exclude_columns = None
        import ast
        try:
            include_columns = ast.literal_eval(action.arguments['include_columns'])
            exclude_columns = ast.literal_eval(action.arguments['exclude_columns'])
        except Exception:
            print("Include and Exclude Columns are None")

        import azureml.dataprep as dprep
        histogram_compare_method = dprep.HistogramCompareMethod(
            ast.literal_eval(action.arguments['histogram_compare_method']))
        profile_arguments_str = action.arguments['profile_arguments']
        profile_arguments = None
        if profile_arguments_str is not None:
            profile_arguments = ast.literal_eval(action.arguments['profile_arguments'])
        lhs_dataset_or_snapshot = None
        rhs_dataset_or_snapshot = None
        is_dataset_diff = ast.literal_eval(action.arguments['is_dataset_diff'])
        if is_dataset_diff:
            lhs_dataset_or_snapshot = _DatasetClient.get_definition(
                workspace,
                action.dataset_id,
                action.definition_version,
                action.arguments)

            rhs_dataset_id = action.arguments['rhs_dataset_id']
            rhs_dataset_definition_version = action.arguments['rhs_dataset_definition_version']
            rhs_dataset_or_snapshot = _DatasetClient.get_definition(
                workspace,
                rhs_dataset_id,
                rhs_dataset_definition_version,
                action.arguments)
        else:
            lhs_dataset_or_snapshot = _DatasetClient.get_snapshot(
                workspace=workspace,
                snapshot_name=action.dataset_snapshot_name,
                dataset_id=action.dataset_id,
                dataset_name=None)

            rhs_dataset_id = action.arguments['rhs_dataset_id']
            rhs_dataset_snapsnot_name = action.arguments['rhs_dataset_snapsnot_name']
            rhs_dataset_or_snapshot = _DatasetClient.get_snapshot(
                workspace=workspace,
                snapshot_name=rhs_dataset_snapsnot_name,
                dataset_id=rhs_dataset_id,
                dataset_name=None)

        return _DatasetClient._execute_diff_local(
            lhs_dataset_or_snapshot=lhs_dataset_or_snapshot,
            rhs_dataset_or_snapshot=rhs_dataset_or_snapshot,
            profile_arguments=profile_arguments,
            include_columns=include_columns,
            exclude_columns=exclude_columns,
            histogram_compare_method=histogram_compare_method,
            action_run=None,
            dataset_id=action.dataset_id,
            action_id=action.action_id
        )

    @staticmethod
    def _create_dataset_definition_dto(definition):
        deprecated_by_dto = None
        if definition._deprecated_by_dataset_id is not None:
            deprecated_by_dto = DatasetDefinitionReference(
                dataset_id=definition._deprecated_by_dataset_id,
                definition_version=definition._deprecated_by_definition)
        state_dto = DatasetStateDto(
            state=definition._state,
            deprecated_by=deprecated_by_dto,
            etag=definition._etag)
        return DatasetDefinitionDto(
            dataset_id=definition._dataset_id,
            version_id=definition._version_id,
            dataset_definition_state=state_dto,
            dataflow=definition.to_json(),
            notes=definition._notes,
            etag=definition._etag,
            data_path=definition._data_path,
            file_type=definition._file_type)

    @staticmethod
    def _get_updated_definition(definition, dataflow, data_path=None):
        if(dataflow is None):
            file_type = definition._file_type
        else:
            file_type = _DatasetClient._get_source_file_type(dataflow)
        return DatasetDefinition(
            workspace=definition._workspace,
            dataset_id=definition._dataset_id,
            version_id=definition._version_id,
            dataflow=dataflow,
            notes=definition._notes,
            etag=definition._etag,
            created_time=definition._created_time,
            modified_time=definition._modified_time,
            state=definition._state,
            deprecated_by_dataset_id=definition._deprecated_by_dataset_id,
            deprecated_by_definition_version=definition._deprecated_by_definition_version,
            data_path=data_path if data_path is not None else definition._data_path,
            dataset=definition._dataset,
            file_type=file_type)

    @staticmethod
    def _get_client(ws, auth=None, host=None):
        host_env = os.environ.get('AZUREML_SERVICE_ENDPOINT')
        auth = auth or ws._auth
        host = host or host_env or get_service_url(
            auth, _DatasetClient._get_workspace_uri_path(
                ws._subscription_id, ws._resource_group, ws._workspace_name), ws._workspace_id)

        return RestClient(credentials=_DatasetClient._get_basic_token_auth(auth), base_url=host)

    @staticmethod
    def _get_basic_token_auth(auth):
        return BasicTokenAuthentication({
            "access_token": _DatasetClient._get_access_token(auth)
        })

    @staticmethod
    def _get_access_token(auth):
        header = auth.get_authentication_header()
        bearer_token = header["Authorization"]

        return bearer_token[_DatasetClient._bearer_prefix_len:]

    @staticmethod
    def _get_workspace_uri_path(subscription_id, resource_group, workspace_name):
        return ("/subscriptions/{}/resourceGroups/{}/providers"
                "/Microsoft.MachineLearningServices"
                "/workspaces/{}").format(subscription_id, resource_group, workspace_name)

    @staticmethod
    def _get_credential_type(account_key, sas_token):
        if account_key:
            return constants.ACCOUNT_KEY
        if sas_token:
            return constants.SAS
        return constants.NONE

    @staticmethod
    def _execute_dataset_action(workspace, dataset_id, action_id, dataflow_json):
        sdk_verion_str = ' '.join(
            [_DatasetClient._get_package_with_version(pkg) for pkg in ['azureml-core', 'azureml-dataprep']])
        module_logger.debug(
            'Action execution started. Action id: {}. SDK versions: {}'.format(action_id, sdk_verion_str))
        action = _DatasetClient._get_action_by_id(workspace, dataset_id, action_id)
        module_logger.debug('Action retrieved. Action id: {}'.format(action_id))
        dflow = None
        import azureml.dataprep as dprep
        if dataflow_json:
            dflow = dprep.Dataflow.from_json(dataflow_json)
        else:
            dflow = _DatasetClient.get_definition(
                workspace,
                action.dataset_id,
                action.definition_version,
                action.arguments)
        module_logger.debug('Dataflow retrieved. Action id: {}'.format(action_id))
        if action.action_type == 'profile':
            result = _DatasetClient._execute_local_profile(dflow, action.arguments)
            result_artifacts = _DatasetClient._write_to_artifact_store(
                workspace,
                dataset_id,
                action.action_id,
                action.action_type,
                result)
            if action.arguments.get('generate_preview', False):
                if 'row_count' not in action.arguments:
                    raise Exception('\'row_count\' is not specified in the arguments')
                result_artifacts.append(_DatasetClient._upload_preview(workspace, action, dflow))
            _DatasetClient._update_action_result(
                workspace,
                dataset_id,
                action_id,
                result_artifacts,
                dflow._get_source_data_hash())
        elif action.action_type == 'inspector':
            result_artifacts = _DatasetClient._write_to_artifact_store(
                workspace,
                dataset_id,
                action.action_id,
                action.action_type,
                dflow._execute_inspector(action.arguments['inspector']).to_pod())
            _DatasetClient._update_action_result(
                workspace,
                dataset_id,
                action_id,
                result_artifacts,
                dflow._get_source_data_hash())
        elif action.action_type == 'diff':
            _DatasetClient.execute_diff_action(workspace, action)
        else:
            raise Exception('Unknown action type: {}'.format(action.action_type))
        module_logger.debug('Action execution completed. Action id: {}'.format(action_id))

    @staticmethod
    def _upload_preview(workspace, action, dataflow):
        artifacts_client = ArtifactsClient(workspace.service_context)
        row_count = int(action.arguments['row_count'])
        root_path = './preview/'
        import azureml.dataprep as dprep
        data_path = dprep.LocalFileOutput(root_path)
        preview_flow = dataflow.take(row_count).write_to_csv(directory_path=data_path)
        preview_flow.run_local()

        success_path = os.path.join(root_path, '_SUCCESS')
        csv_path = os.path.join(root_path, 'part-00000')
        csv_path_renamed = 'actions/{}/preview_result.csv'.format(action.action_id)
        os.rename(csv_path, csv_path_renamed)

        if(os.path.exists(success_path)):
            try:
                artifact = artifacts_client.create_empty_artifacts(
                    origin='Dataset',
                    container=action.dataset_id,
                    paths=[csv_path_renamed]).artifacts[csv_path_renamed]
                artifacts_client.upload_files(
                    paths=[csv_path_renamed],
                    origin=artifact.origin,
                    container=artifact.container)
            except Exception:
                pass
            finally:
                if os.path.isfile(success_path):
                    os.remove(success_path)
                if os.path.isfile(csv_path_renamed):
                    os.remove(csv_path_renamed)
        return artifact.artifact_id

    @staticmethod
    def _handle_exception(err):
        import json
        content = json.loads(err.response.content)
        if err.response.status_code >= 400 and err.response.status_code < 500:
            msg = content['error']['message']
            if 'Response Body' in msg:
                raise Exception("User Error: " + msg[:msg.index('Response Body')])
            else:
                raise Exception("User Error: " + msg)
        elif err.response.status_code >= 500:
            raise Exception("Internal Server Error, operation Id: " + content['correlation']['operation'])
        else:
            raise err

    @staticmethod
    def _get_package_with_version(name):
        package_with_version = name
        try:
            from pkg_resources import get_distribution
            version = get_distribution(name).version
            package_with_version = "{}=={}".format(name, version)
        except Exception:
            pass
        return package_with_version

    @staticmethod
    def _get_index_url(name):
        index_url = None
        try:
            index_url = os.environ.get('{}-INDEX-URL'.format(name.upper()))
        except Exception:
            pass
        return index_url

    @staticmethod
    def _get_pip_arguments():
        pip_arguments = []
        core_package_name = "azureml-core"
        dataprep_package_name = "azureml-dataprep"
        pip_arguments.append(_DatasetClient._get_package_with_version(core_package_name))
        pip_arguments.append(_DatasetClient._get_package_with_version(dataprep_package_name))
        dprep_argument = '--extra-index-url'\
            '=https://dataprepdownloads.azureedge.net/pypi/weekly-rc-932B96D048E011E8B56608/latest/'
        azureml_argument = '--extra-index-url'\
            '=https://azuremlsdktestpypi.azureedge.net/sdk-release/master/588E708E0DF342C4A80BD954289657CF/'
        pip_arguments.append(dprep_argument)
        pip_arguments.append(azureml_argument)
        return pip_arguments

    @staticmethod
    def _log_to_props(dataset, operation, run=None):
        from azureml.core.run import Run, _OfflineRun
        from azureml.data.dataset_definition import DatasetDefinition
        from azureml.data.dataset_snapshot import DatasetSnapshot

        def get_dataset_info(dataset_input):
            if isinstance(dataset_input, Dataset):
                return dataset_input.name, dataset_input.definition_version, None
            if isinstance(dataset_input, DatasetDefinition):
                return dataset_input._dataset.name, dataset_input._version_id, None
            if isinstance(dataset_input, DatasetSnapshot):
                return dataset_input._dataset_name, dataset_input._definition_version, dataset_input.name
            raise ValueError('Unrecognized dataset type. {}'.format(type(dataset_input)))

        try:
            run = run or Run.get_context()
            if dataset is None or not run or isinstance(run, _OfflineRun):
                return

            operation = 'azureml.dataset.' + operation + '.'
            name, definition, snapshot = get_dataset_info(dataset)
            key = operation + ':'.join(filter(lambda _: _, [name, definition, snapshot]))

            if key in run.get_properties():
                module_logger.debug('Skipping dataset logging as {} already exists in properties.'.format(key))
                return

            run.add_properties({
                key: json.dumps({
                    "name": name,
                    "definition": definition or "",
                    "snapshot": snapshot or ""
                })
            })
        except Exception as e:
            module_logger.warning("Unable to log dataset. Exception: {}".format(e))
