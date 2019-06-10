# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains class for retrieving a cloud representation of a Model object associated with a Workspace."""
import copy
import json
import logging
import os
import shutil
import tarfile
import tempfile
import uuid
from collections import OrderedDict
from datetime import datetime
from operator import attrgetter

import requests
from azureml.core.dataset import Dataset
from azureml.data.dataset_snapshot import DatasetSnapshot

from azureml.core.experiment import Experiment
from azureml.core.run import get_run

from azureml.exceptions import (WebserviceException, RunEnvironmentException, ModelNotFoundException)
from azureml._model_management._constants import DATASET_SNAPSHOT_ID_FORMAT
from azureml._model_management._constants import MMS_SYNC_TIMEOUT_SECONDS
from azureml._model_management._constants import MMS_WORKSPACE_API_VERSION
from azureml._model_management._constants import WEBAPI_IMAGE_FLAVOR
from azureml._model_management._constants import ARCHITECTURE_AMD64
from azureml._model_management._constants import CUSTOM_BASE_IMAGE_SUPPORTED_RUNTIMES
from azureml._model_management._util import _get_mms_url
from azureml._model_management._util import get_paginated_results
from azureml._model_management._util import model_payload_template
from azureml._model_management._util import add_sdk_to_requirements
from azureml._model_management._util import upload_dependency
from azureml._model_management._util import wrap_execution_script_with_source_directory
from azureml._model_management._util import joinPath
from azureml._model_management._util import validate_entry_script_name
from azureml._model_management._util import check_duplicate_properties
from azureml._model_management._util import get_requests_session
from azureml._model_management._util import webservice_name_validation

from azureml._restclient.clientbase import ClientBase
from azureml._restclient.artifacts_client import ArtifactsClient
from azureml._restclient.assets_client import AssetsClient
from dateutil.parser import parse

from azureml._file_utils import download_file
from azureml._model_management._util import validate_path_exists_or_throw
from azureml._model_management._constants import SUPPORTED_RUNTIMES
from azureml._model_management._constants import UNDOCUMENTED_RUNTIMES

from azureml.core.profile import ModelProfile

module_logger = logging.getLogger(__name__)
MODELS_DIR = "azureml-models"


class Model(object):
    """Class for AzureML models.

    Model constructor is used to retrieve a cloud representation of a Model object associated with the provided
    workspace. Must provide either name or ID.

    :param workspace: The workspace object containing the Model to retrieve
    :type workspace: azureml.core.workspace.Workspace
    :param name: Will retrieve the latest model with the corresponding name, if it exists
    :type name: str
    :param id: Will retrieve the model with the corresponding ID, if it exists
    :type id: str
    :param tags: Optional, will filter based on the provided list, searching by either 'key' or '[key, value]'.
        Ex. ['key', ['key2', 'key2 value']]
    :type tags: :class:`list`
    :param properties: Optional, will filter based on the provided list, searching by either 'key' or
        '[key, value]'. Ex. ['key', ['key2', 'key2 value']]
    :type properties: :class:`list`
    :param version: When provided along with name, will get the specific version of the specified named model,
        if it exists
    :type version: int
    :param run_id: Optional, will filter based on the provided ID.
    :type run_id: str
    """

    _expected_payload_keys = ['createdTime', 'description', 'id', 'mimeType', 'name', 'kvTags',
                              'properties', 'unpack', 'url', 'version', 'experimentName', 'runId', 'datasets']

    def __init__(self, workspace, name=None, id=None, tags=None, properties=None, version=None,
                 run_id=None, model_framework=None):
        """Model constructor.

        The Model constructor is used to retrieve a cloud representation of a Model object associated with the provided
        workspace. Must provide either name or ID.

        :param workspace: The workspace object containing the Model to retrieve
        :type workspace: azureml.core.workspace.Workspace
        :param name: Will retrieve the latest model with the corresponding name, if it exists
        :type name: str
        :param id: Will retrieve the model with the corresponding ID, if it exists
        :type id: str
        :param tags: Optional, will filter based on the provided list, searching by either 'key' or '[key, value]'.
            Ex. ['key', ['key2', 'key2 value']]
        :type tags: :class:`list`
        :param properties: Optional, will filter based on the provided list, searching by either 'key' or
            '[key, value]'. Ex. ['key', ['key2', 'key2 value']]
        :type properties: :class:`list`
        :param version: When provided along with name, will get the specific version of the specified named model,
            if it exists
        :type version: int
        :param run_id: Optional, will filter based on the provided ID.
        :type run_id: str
        :param model_framework: Will retrieve the models with the corresponding frameworks
        :type model_framework: str
        :return: A model object, if one is found in the provided workspace
        :rtype: azureml.core.Model
        :raises: ModelNotFoundException
        """
        self.created_time = None
        self.description = None
        self.id = None
        self.mime_type = None
        self.name = None
        self.model_framework = None
        self.tags = None
        self.properties = None
        self.unpack = None
        self.url = None
        self.version = None
        self.workspace = None
        self.experiment_name = None
        self.run_id = None
        self.run = None
        self.datasets = {}
        self._auth = None
        self._mms_endpoint = None

        if workspace:
            get_response_payload = self._get(workspace, name, id, tags, properties, version, model_framework, run_id)
            if get_response_payload:
                self._validate_get_payload(get_response_payload)
                self._initialize(workspace, get_response_payload)
            else:
                error_message = 'ModelNotFound: Model with '
                if id:
                    error_message += 'ID {}'.format(id)
                else:
                    error_message += 'name {}'.format(name)
                if tags:
                    error_message += ', tags {}'.format(tags)
                if properties:
                    error_message += ', properties {}'.format(properties)
                if version:
                    error_message += ', version {}'.format(version)
                if model_framework:
                    error_message += ', framework {}'.format(model_framework)
                if run_id:
                    error_message += ', Run ID {}'.format(run_id)
                error_message += ' not found in provided workspace'

                raise WebserviceException(error_message)

    def _initialize(self, workspace, obj_dict):
        """Initialize the Model instance.

        This is used because the constructor is used as a getter.

        :param workspace:
        :type workspace: azureml.core.workspace.Workspace
        :param obj_dict:
        :type obj_dict: dict
        :return:
        :rtype: None
        """
        created_time = parse(obj_dict['createdTime'])
        model_id = obj_dict['id']
        self.created_time = created_time
        self.description = obj_dict['description']
        self.id = model_id
        self.mime_type = obj_dict['mimeType']
        self.name = obj_dict['name']
        self.model_framework = obj_dict['framework']
        self.model_framework_version = obj_dict['frameworkVersion']
        self.tags = obj_dict['kvTags']
        self.properties = obj_dict['properties']
        self.unpack = obj_dict['unpack']
        self.url = obj_dict['url']
        self.version = obj_dict['version']
        self.workspace = workspace
        self.experiment_name = obj_dict['experimentName']
        self.run_id = obj_dict['runId']
        self._auth = workspace._auth
        self._mms_endpoint = _get_mms_url(workspace) + '/models/{}'.format(model_id)
        self.parent_id = obj_dict.get('parentModelId')

        if self.experiment_name and self.run_id:
            try:
                experiment = Experiment(workspace, self.experiment_name)
                run = get_run(experiment, self.run_id)
                self.run = run
            except Exception:
                pass

        for dataset_reference in obj_dict['datasets']:
            dataset_scenario = dataset_reference['name']
            dataset_id = dataset_reference['id']
            if '/datasetSnapshotName' in dataset_id:
                snapshot_pieces = dataset_id.split('/')
                dataset_id = snapshot_pieces[2]
                snapshot_name = snapshot_pieces[4]
                try:
                    dataset_snapshot = DatasetSnapshot.get(workspace, snapshot_name, dataset_id=dataset_id)
                    self.datasets.setdefault(dataset_scenario, []).append(dataset_snapshot)
                except Exception as e:
                    module_logger.warning('Unable to retrieve DatasetSnapshot with name {} and DatasetID {} due to '
                                          'the following exception.\n'
                                          '{}'.format(snapshot_name, dataset_id, e))
            else:
                try:
                    dataset = Dataset.get(workspace, id=dataset_id)
                    self.datasets.setdefault(dataset_scenario, []).append(dataset)
                except Exception as e:
                    module_logger.warning('Unable to retrieve Dataset with ID {} due to the following exception.\n'
                                          '{}'.format(dataset_id, e))

    @staticmethod
    def _get(workspace, name=None, id=None, tags=None, properties=None, version=None,
             model_framework=None, run_id=None):
        """Retrieve the Model object from the cloud.

        :param workspace:
        :type workspace: workspace: azureml.core.workspace.Workspace
        :param name:
        :type name: str
        :param id:
        :type id: str
        :param tags:
        :type tags: :class:`list`
        :param properties:
        :type properties: :class:`list`
        :param version:
        :type version: int
        :param run_id:
        :type run_id: str
        :return:
        :rtype: dict
        """
        if not id and not name:
            raise WebserviceException('Error, one of id or name must be provided.', logger=module_logger)

        headers = workspace._auth.get_authentication_header()
        params = {'api-version': MMS_WORKSPACE_API_VERSION, 'orderBy': 'CreatedAtDesc', 'count': 1}
        base_url = _get_mms_url(workspace)
        mms_url = base_url + '/models'

        if id:
            mms_url += '/{}'.format(id)
        else:
            params['name'] = name
        if tags:
            tags_query = ""
            for tag in tags:
                if type(tag) is list:
                    tags_query = tags_query + tag[0] + "=" + tag[1] + ","
                else:
                    tags_query = tags_query + tag + ","
            tags_query = tags_query[:-1]
            params['tags'] = tags_query
        if properties:
            properties_query = ""
            for prop in properties:
                if type(prop) is list:
                    properties_query = properties_query + prop[0] + "=" + prop[1] + ","
                else:
                    properties_query = properties_query + prop + ","
            properties_query = properties_query[:-1]
            params['properties'] = properties_query
        if version:
            params['version'] = version
        if model_framework:
            params['modelFramework'] = model_framework
        if run_id:
            params['runId'] = run_id

        resp = ClientBase._execute_func(get_requests_session().get, mms_url, headers=headers, params=params)
        if resp.status_code == 200:
            content = resp.content
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            model_payload = json.loads(content)
            if id:
                return model_payload
            else:
                paginated_results = get_paginated_results(model_payload, headers)
                if paginated_results:
                    return paginated_results[0]
                else:
                    return None
        elif resp.status_code == 404:
            return None
        else:
            raise WebserviceException('Received bad response from Model Management Service:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content),
                                      logger=module_logger)

    @staticmethod
    def register(workspace, model_path, model_name, tags=None, properties=None, description=None,
                 datasets=None, model_framework=None, model_framework_version=None, root_dir=None):
        """Register a model with the provided workspace.

        :param workspace: The workspace to register the model under
        :type workspace: workspace: azureml.core.workspace.Workspace
        :param model_path: String or list of strings which points to the relative path on the local file system where
            the model assets are located. This can be a direct pointer to a single model file, a list of pointers to
            individual files, in which case they will be bundled together, or a pointer to a single folder, in which
            case the folder will be taken with everything that it contains. All paths provided must be relative paths,
            and must be at or below the current working directory, or the root_dir if specified.
        :type model_path: str or :class:`list[str]`
        :param model_name: The name to register the model with
        :type model_name: str
        :param tags: Dictionary of key value tags to give the model
        :type tags: dict[str, str]
        :param properties: Dictionary of key value properties to give the model. These properties cannot
            be changed after model creation, however new key value pairs can be added
        :type properties: dict[str, str]
        :param description: A text description of the model
        :type description: str
        :param datasets: A list of tuples representing a pairing of dataset purpose to Dataset or DatasetSnapshot
            object. The Dataset or Dataset snapshot should be registered with the Workspace prior to this call.
        :type datasets: :class:`list[tuple[str, Dataset | DatasetSnapshot]]`
        :param model_framework: The framework of the registered model
        :type model_framework: str
        :param model_framework_version: The framework version of the registered model
        :type model_framework_version: str
        :param root_dir: The path to a directory to use as the root for the model path. If provided, the model_path
            parameter will be resolved from the specified directory.
        :return: The registered model object
        :rtype: azureml.core.Model
        """
        if model_framework is None and model_framework_version is not None:
            raise WebserviceException("Model framework version cannot be provided without a valid framework",
                                      logger=module_logger)

        Model._validate_model_path(model_path, root_dir)

        cwd = os.getcwd()
        if root_dir:
            os.chdir(root_dir)

        try:
            aggregate_dir = None
            if type(model_path) is list:
                aggregate_dir = tempfile.TemporaryDirectory()
                for file in model_path:
                    file = file.rstrip(os.sep)
                    cur_path = ''
                    for dir in os.path.dirname(file).split(os.sep):
                        new_path = os.path.join(cur_path, dir)
                        target_path = os.path.join(aggregate_dir.name, new_path)
                        if not os.path.isdir(target_path):
                            os.mkdir(target_path)
                        cur_path = new_path
                    shutil.copy2(file, os.path.join(aggregate_dir.name, cur_path))
                model_path = aggregate_dir.name
                arcname = model_name
            else:
                model_path = model_path.rstrip(os.sep)
                arcname = os.path.basename(model_path)

            artifact_client = ArtifactsClient(workspace.service_context)
            asset_client = AssetsClient(workspace.service_context)

            tar_name = model_name + '.tar.gz'
            tmpdir = tempfile.TemporaryDirectory()
            model_tar_path = os.path.join(tmpdir.name, tar_name)
            dependency_tar = tarfile.open(model_tar_path, 'w:gz')
            dependency_tar.add(model_path, arcname=arcname)
            dependency_tar.close()

            origin = 'LocalUpload'
            container = '{}-{}'.format(datetime.now().strftime('%y%m%dT%H%M%S'), str(uuid.uuid4())[:8])
            artifact_client.upload_artifact_from_path(model_tar_path, origin, container, tar_name)
            prefix_values = [{'prefix': '{}/{}/{}'.format(origin, container, tar_name)}]
            create_asset_result = asset_client.create_asset(model_name, prefix_values, None)
            asset = create_asset_result.content
            if isinstance(asset, bytes):
                asset = asset.decode('utf-8')
            asset_dict = json.loads(asset)
            asset_id = asset_dict['id']
            print('Registering model {}'.format(model_name))
            model = Model._register_with_asset(workspace, model_name, asset_id, tags, properties, description,
                                               datasets=datasets, model_framework=model_framework,
                                               model_framework_version=model_framework_version, unpack=True)

            if aggregate_dir:
                aggregate_dir.cleanup()
            if tmpdir:
                tmpdir.cleanup()
        finally:
            os.chdir(cwd)

        return model

    @staticmethod
    def _validate_model_path(model_path, root_dir=None):
        """Validate that the provided model path exists.

        :param model_path:
        :type model_path: str or :class:`list[str]`
        :param root_dir:
        :type root_dir: str
        :raises: WebserviceException
        """
        if not root_dir:
            root_dir = os.getcwd()

        paths_to_check = []
        if type(model_path) is list:
            paths_to_check.extend(model_path)
        else:
            paths_to_check.append(model_path)

        for path in paths_to_check:
            if os.path.isabs(path):
                raise WebserviceException('Error, provided path "{}" cannot be an absolute path. Please provide a '
                                          'path relative that is at or below the current working directory, or the '
                                          'root_dir if specified.'.format(path))
            if '..' in path:
                raise WebserviceException('Error, provided path "{}" must be at or below the current working '
                                          'directory, or the root_dir if specified.'.format(path))
            if not os.path.exists(os.path.normpath(os.path.join(root_dir, path))):
                raise WebserviceException('Error, provided model path "{}" cannot be found in directory '
                                          '"{}".'.format(path, root_dir))

    @staticmethod
    def get_model_path(model_name, version=None, _workspace=None):
        """Return path to model.

        | The function will search for the model in the following locations
        | If version is None:
        | 1) download from remote to cache
        | 2) load from cache `azureml-models/$MODEL_NAME/$LATEST_VERSION/`
        | 3) ./$MODEL_NAME

        | If version is not None:
        | 1) load from cache `azureml-models/$MODEL_NAME/$LATEST_VERSION/`
        | 2) download from remote to cache

        :param model_name: The name of the model to retrieve
        :type model_name: str
        :param version: The version of the model to retrieve, defaults to the latest version
        :type version: int
        :param _workspace: The workspace to retrieve a model from. Can't use remotely
        :type _workspace: azureml.core.workspace.Workspace
        :return: The path on disk to the model
        :rtype: str
        :raises: ModelNotFoundException
        """
        if version is not None and not isinstance(version, int):
            raise WebserviceException("version should be an int", logger=module_logger)
        # check if in preauthenticated env
        active_workspace = _workspace
        try:
            # get workspace from submitted run
            from azureml.core.run import Run
            run = Run.get_context(allow_offline=False)
            module_logger.debug("Run is {}".format(run))
            experiment = run.experiment
            module_logger.debug("RH is {}".format(experiment))
            active_workspace = experiment.workspace
        except RunEnvironmentException as ee:
            message = "RunEnvironmentException: {}".format(ee)
            module_logger.debug(message)

        if version is not None:
            try:
                return Model._get_model_path_local(model_name, version)
            except ModelNotFoundException as ee:
                module_logger.debug("Model not find in local")
                if active_workspace is not None:
                    module_logger.debug("Getting model from remote")
                    return Model._get_model_path_remote(model_name, version, active_workspace)
                raise WebserviceException(ee.message, logger=module_logger)
        else:
            if active_workspace is not None:
                return Model._get_model_path_remote(model_name, version, active_workspace)
            else:
                return Model._get_model_path_local(model_name, version)

    @staticmethod
    def _get_model_path_local(model_name, version=None):
        """Get the local path to the Model.

        :param model_name:
        :type model_name: str
        :param version:
        :type version: int
        :return:
        :rtype: str
        """
        if version is not None and not isinstance(version, int):
            raise WebserviceException("version should be an int", logger=module_logger)
        if model_name is None:
            raise WebserviceException("model_name is None", logger=module_logger)

        candidate_model_path = os.path.join(MODELS_DIR, model_name)
        # Probing azureml-models/<name>
        if not os.path.exists(candidate_model_path):
            return Model._get_model_path_local_from_root(model_name)
        else:
            # Probing azureml-models/<name> exists, probing version
            if version is None:
                latest_version = Model._get_latest_version(os.listdir(os.path.join(MODELS_DIR, model_name)))
                module_logger.debug("version is None. Latest version is {}".format(latest_version))
            else:
                latest_version = version
                module_logger.debug("Using passed in version {}".format(latest_version))

            candidate_model_path = os.path.join(candidate_model_path, str(latest_version))
            # Probing azureml-models/<name>/<version> exists
            if not os.path.exists(candidate_model_path):
                return Model._get_model_path_local_from_root(model_name)
            else:
                # Checking one file system node
                file_system_entries = os.listdir(candidate_model_path)
                if len(file_system_entries) != 1:
                    raise WebserviceException("Dir {} can contain only 1 file or folder. "
                                              "Found {}".format(candidate_model_path, file_system_entries),
                                              logger=module_logger)

                candidate_model_path = os.path.join(candidate_model_path, file_system_entries[0])
                module_logger.debug("Found model path at {}".format(candidate_model_path))
                return candidate_model_path

    @staticmethod
    def _get_model_path_local_from_root(model_name):
        """Get the path to the Model from the root of the directory.

        :param model_name:
        :type model_name: str
        :return:
        :rtype: str
        """
        paths_in_scope = Model._paths_in_scope(MODELS_DIR)
        module_logger.debug("Checking root for {} because candidate dir {} had {} nodes: {}".format(
            model_name, MODELS_DIR, len(paths_in_scope), "\n".join(paths_in_scope)))

        candidate_model_path = model_name
        if os.path.exists(candidate_model_path):
            return candidate_model_path
        raise ModelNotFoundException("Model not found in cache or in root at ./{}. For more info,"
                                     "set logging level to DEBUG.".format(candidate_model_path))

    @staticmethod
    def _paths_in_scope(dir):
        """Get a list of paths in the provided directory.

        :param dir:
        :type dir: str
        :return:
        :rtype: :class:`list[str]`
        """
        paths_in_scope = []
        for root, dirs, files in os.walk(dir):
            for file in files:
                paths_in_scope.append(os.path.join(root, file))
        return paths_in_scope

    @staticmethod
    def _get_last_path_segment(path):
        """Get the last segment of the path.

        :param path:
        :type path: str
        :return:
        :rtype: str
        """
        last_segment = os.path.normpath(path).split(os.sep)[-1]
        module_logger.debug("Last segment of {} is {}".format(path, last_segment))
        return last_segment

    @staticmethod
    def _get_strip_prefix(prefix_id):
        """Get the prefix to strip from the path.

        :param prefix_id:
        :type prefix_id: str
        :return:
        :rtype: str
        """
        path = prefix_id.split("/", 2)[-1]
        module_logger.debug("prefix id {} has path {}".format(prefix_id, path))
        path_to_strip = os.path.dirname(path)
        module_logger.debug("prefix to strip from path {} is {}".format(path, path_to_strip))
        return path_to_strip

    def _get_asset(self):
        from azureml._restclient.assets_client import AssetsClient
        asset_id = self.url[len("aml://asset/"):]
        client = AssetsClient(self.workspace.service_context)
        asset = client.get_asset_by_id(asset_id)
        return asset

    def _get_sas_to_relative_download_path_map(self, asset):
        artifacts_client = ArtifactsClient(self.workspace.service_context)
        sas_to_relative_download_path = OrderedDict()
        for artifact in asset.artifacts:
            module_logger.debug("Asset has artifact {}".format(artifact))
            if artifact.id is not None:
                # download by id
                artifact_id = artifact.id
                module_logger.debug("Artifact has id {}".format(artifact_id))
                (path, sas) = artifacts_client.get_file_by_artifact_id(artifact_id)
                sas_to_relative_download_path[sas] = Model._get_last_path_segment(path)
            else:
                # download by prefix
                prefix_id = artifact.prefix
                module_logger.debug("Artifact has prefix id {}".format(prefix_id))
                paths = artifacts_client.get_files_by_artifact_prefix_id(prefix_id)
                prefix_to_strip = Model._get_strip_prefix(prefix_id)
                for path, sas in paths:
                    path = os.path.relpath(path, prefix_to_strip)  # same as stripping prefix from path per AK
                    sas_to_relative_download_path[sas] = path

        if len(sas_to_relative_download_path) == 0:
            raise WebserviceException("No files to download. Did you upload files?", logger=module_logger)
        module_logger.debug("sas_to_download_path map is {}".format(sas_to_relative_download_path))
        return sas_to_relative_download_path

    def _download_model_files(self, sas_to_relative_download_path, target_dir, exist_ok):
        for sas, path in sas_to_relative_download_path.items():
            target_path = os.path.join(target_dir, path)
            if not exist_ok and os.path.exists(target_path):
                raise WebserviceException("File already exists. To overwrite, set exist_ok to True. "
                                          "{}".format(target_path), logger=module_logger)
            sas_to_relative_download_path[sas] = target_path
            download_file(sas, target_path, stream=True)

        if self.unpack:
            # handle packed model
            tar_path = list(sas_to_relative_download_path.values())[0]
            file_paths = self._handle_packed_model_file(tar_path, target_dir, exist_ok)
        else:
            # handle unpacked model
            file_paths = sas_to_relative_download_path.values()
        return file_paths

    def _handle_packed_model_file(self, tar_path, target_dir, exist_ok):
        module_logger.debug("Unpacking model {}".format(tar_path))
        if not os.path.exists(tar_path):
            raise WebserviceException("tar file not found at {}. Paths in scope:\n"
                                      "{}".format(tar_path, "\n".join(Model._paths_in_scope(MODELS_DIR))),
                                      logger=module_logger)
        with tarfile.open(tar_path) as tar:
            if not exist_ok:
                for tar_file_path in tar.getnames():
                    candidate_path = os.path.join(target_dir, tar_file_path)
                    if os.path.exists(candidate_path):
                        raise WebserviceException("File already exists. To overwrite, set exist_ok to True. "
                                                  "{}".format(candidate_path), logger=module_logger)
            tar.extractall(path=target_dir)
            tar_paths = tar.getnames()
        file_paths = [os.path.join(target_dir, os.path.commonprefix(tar_paths))]
        if os.path.exists(tar_path):
            os.remove(tar_path)
        else:
            module_logger.warning("tar_path to unpack is already deleted: {}".format(tar_path))
        return file_paths

    def download(self, target_dir=".", exist_ok=False, exists_ok=None):
        """Download model to target_dir of local file system.

        :param target_dir: Path to directory for where to download the model. Defaults to "."
        :type target_dir: str
        :param exist_ok: Boolean to replace downloaded dir/files if exists. Defaults to False
        :type exist_ok: bool
        :param exists_ok:
        :type exists_ok:
        :return: string path to file or folder of model
        :rtype: str
        """
        if exists_ok is not None:
            if exist_ok is not None:
                raise WebserviceException("Both exists_ok and exist_ok are set. Please use exist_ok only.",
                                          logger=module_logger)
            module_logger.warning("exists_ok is deprecated. Please use exist_ok")
            exist_ok = exists_ok

        # use model to get asset
        asset = self._get_asset()

        # use asset.artifacts to get files to download
        sas_to_relative_download_path = self._get_sas_to_relative_download_path_map(asset)

        # download files using sas
        file_paths = self._download_model_files(sas_to_relative_download_path, target_dir, exist_ok)
        if len(file_paths) == 0:
            raise WebserviceException("Illegal state. Unpack={}, Paths in target_dir is "
                                      "{}".format(self.unpack, file_paths), logger=module_logger)
        model_path = os.path.commonpath(file_paths)
        return model_path

    @staticmethod
    def _get_model_path_remote(model_name, version, workspace):
        """Retrieve the remote path to the Model.

        :param model_name:
        :type model_name: str
        :param version:
        :type version: int
        :param workspace:
        :type workspace: azureml.core.workspace.Workspace
        :return:
        :rtype: str
        """
        if version is not None and not isinstance(version, int):
            raise WebserviceException("version should be an int", logger=module_logger)
        # model -> asset
        from azureml.core.workspace import Workspace
        assert isinstance(workspace, Workspace)

        try:
            model = Model(workspace=workspace, name=model_name, version=version)
        except WebserviceException as e:
            if 'ModelNotFound' in e.message:
                models = Model.list(workspace)
                model_infos = sorted(["{}/{}".format(model.name, model.version) for model in models])
                raise ModelNotFoundException("Model/Version {}/{} not found in workspace. "
                                             "{}".format(model_name, version, model_infos), logger=module_logger)
            else:
                raise WebserviceException(e.message, logger=module_logger)

        # downloading
        version = model.version
        module_logger.debug("Found model version {}".format(version))
        target_dir = os.path.join(MODELS_DIR, model_name, str(version))
        model_path = model.download(target_dir, exist_ok=True)
        if not os.path.exists(model_path):
            items = os.listdir(target_dir)
            raise ModelNotFoundException("Expected model path does not exist: {}. Found items in dir: "
                                         "{}".format(model_path, str(items)), logger=module_logger)
        return model_path

    @staticmethod
    def _register_with_asset(workspace, model_name, asset_id, tags=None, properties=None, description=None,
                             experiment_name=None, run_id=None, datasets=None, model_framework=None,
                             model_framework_version=None, unpack=False):
        """Register the asset as a Model.

        :param workspace:
        :type workspace: azureml.core.workspace.Workspace
        :param model_name:
        :type model_name: str
        :param asset_id:
        :type asset_id: str
        :param tags:
        :type tags: dict[str, str]
        :param properties:
        :type properties: dict[str, str]
        :param description:
        :type description: str
        :param experiment_name:
        :type experiment_name: str
        :param run_id:
        :type run_id: str
        :param datasets:
        :type datasets: list[tuple[str, Dataset | DatasetSnapshot]]
        :param model_framework:
        :type model_framework: str
        :param model_framework_version:
        :type model_framework_version: str
        :param unpack:
        :type unpack: bool
        :return:
        :rtype: azureml.core.model.Model
        """
        if model_framework is None and model_framework_version is not None:
            raise WebserviceException("Model framework version cannot be provided without a valid framework",
                                      logger=module_logger)

        headers = {'Content-Type': 'application/json'}
        headers.update(workspace._auth.get_authentication_header())
        params = {'api-version': MMS_WORKSPACE_API_VERSION}
        mms_host = _get_mms_url(workspace)
        model_url = mms_host + '/models'

        json_payload = copy.deepcopy(model_payload_template)
        json_payload['name'] = model_name
        json_payload['url'] = 'aml://asset/{}'.format(asset_id)
        json_payload['experimentName'] = experiment_name
        json_payload['runId'] = run_id
        json_payload['unpack'] = unpack
        if tags:
            try:
                if not isinstance(tags, dict):
                    raise WebserviceException("Tags must be a dict", logger=module_logger)
                tags = json.loads(json.dumps(tags))
            except ValueError:
                raise WebserviceException('Error with JSON serialization for tags, '
                                          'be sure they are properly formatted.', logger=module_logger)
            json_payload['kvTags'] = tags
        if properties:
            try:
                if not isinstance(properties, dict):
                    raise WebserviceException("Properties must be a dict", logger=module_logger)
                properties = json.loads(json.dumps(properties))
            except ValueError:
                raise WebserviceException('Error with JSON serialization for properties, '
                                          'be sure they are properly formatted.', logger=module_logger)
            json_payload['properties'] = properties
        if description:
            json_payload['description'] = description

        if datasets:
            datasets_payload = []
            for dataset_pair in datasets:
                dataset_scenario = dataset_pair[0]
                dataset = dataset_pair[1]
                if type(dataset) is Dataset:
                    if not dataset.id:
                        raise WebserviceException('Unable to register Model with provided Dataset with ID "None". '
                                                  'This likely means that the Dataset is unregistered. Please '
                                                  'register the Dataset and try again.', logger=module_logger)
                    datasets_payload.append({'name': dataset_scenario, 'id': dataset.id})
                elif type(dataset) is DatasetSnapshot:
                    datasets_payload.append({'name': dataset_scenario, 'id': DATASET_SNAPSHOT_ID_FORMAT.format(
                        dataset_id=dataset.dataset_id, dataset_snapshot_name=dataset.name)})
                else:
                    raise WebserviceException('Invalid dataset of type {} passed, must be of type Dataset or '
                                              'DatasetSnapshot'.format(type(dataset)), logger=module_logger)

            json_payload['datasets'] = datasets_payload

        if model_framework:
            json_payload['framework'] = model_framework
        if model_framework_version:
            json_payload['frameworkVersion'] = model_framework_version

        try:
            resp = ClientBase._execute_func(get_requests_session().post, model_url, params=params, headers=headers,
                                            json=json_payload)
            resp.raise_for_status()
        except requests.ConnectionError:
            raise WebserviceException('Error connecting to {}.'.format(model_url), logger=module_logger)
        except requests.exceptions.HTTPError:
            raise WebserviceException('Received bad response from Model Management Service:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content),
                                      logger=module_logger)

        content = resp.content
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        model_dict = json.loads(content)

        return Model.deserialize(workspace, model_dict)

    @staticmethod
    def _get_latest_version(versions):
        """Get the latest version of the provided model versions.

        :param versions:
        :type versions: :class:`list[int]`
        :return:
        :rtype: int
        """
        if not len(versions) > 0:
            raise WebserviceException("versions is empty", logger=module_logger)
        versions = [int(version) for version in versions]
        version = max(versions)
        return version

    @staticmethod
    def list(workspace, name=None, tags=None, properties=None, run_id=None, latest=False):
        """Retrieve a list of all models associated with the provided workspace, with optional filters.

        :param workspace: The workspace object to retrieve models from
        :type workspace: azureml.core.workspace.Workspace
        :param name: If provided, will only return models with the specified name, if any
        :type name: str
        :param tags: Will filter based on the provided list, by either 'key' or '[key, value]'.
            Ex. ['key', ['key2', 'key2 value']]
        :type tags: :class:`list`
        :param properties: Will filter based on the provided list, by either 'key' or '[key, value]'.
            Ex. ['key', ['key2', 'key2 value']]
        :type properties: :class:`list`
        :param run_id: Will filter based on the provided run ID.
        :type run_id: str
        :param latest: If true, will only return models with the latest version.
        :type latest: bool
        :return: A list of models, optionally filtered
        :rtype: :class:`list[azureml.core.model.Model]`
        :raises: WebserviceException
        """
        headers = workspace._auth.get_authentication_header()
        params = {'api-version': MMS_WORKSPACE_API_VERSION}
        base_url = _get_mms_url(workspace)
        mms_url = base_url + '/models'

        if name:
            params['name'] = name
        if tags:
            tags_query = ""
            for tag in tags:
                if type(tag) is list:
                    tags_query = tags_query + tag[0] + "=" + tag[1] + ","
                else:
                    tags_query = tags_query + tag + ","
            tags_query = tags_query[:-1]
            params['tags'] = tags_query
        if properties:
            properties_query = ""
            for prop in properties:
                if type(prop) is list:
                    properties_query = properties_query + prop[0] + "=" + prop[1] + ","
                else:
                    properties_query = properties_query + prop + ","
            properties_query = properties_query[:-1]
            params['properties'] = properties_query
        if run_id:
            params['runId'] = run_id

        try:
            resp = ClientBase._execute_func(get_requests_session().get, mms_url, headers=headers, params=params)
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            raise WebserviceException('Received bad response from Model Management Service:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content),
                                      logger=module_logger)

        content = resp.content
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        model_payload = json.loads(content)
        paginated_results = get_paginated_results(model_payload, headers)
        models = [Model.deserialize(workspace, model_dict) for model_dict in paginated_results]
        if latest:
            grouped_models = {}
            for model in models:
                if model.name in grouped_models:
                    grouped_models[model.name].append(model)
                else:
                    grouped_models[model.name] = [model]

            return [max(grouped_models[name], key=attrgetter('version')) for name in grouped_models]
        else:
            return models

    def serialize(self):
        """Convert this Model into a json serialized dictionary.

        :return: The json representation of this Model
        :rtype: dict
        """
        created_time = self.created_time.isoformat() if self.created_time else None
        datasets = {}
        for dataset_scenario, dataset_list in self.datasets.items():
            for dataset in dataset_list:
                datasets.setdefault(dataset_scenario, []).append(dataset.__str__())
        return {'createdTime': created_time,
                'description': self.description,
                'id': self.id,
                'mimeType': self.mime_type,
                'name': self.name,
                'framework': self.model_framework,
                'frameworkVersion': self.model_framework_version,
                'tags': self.tags,
                'properties': self.properties,
                'unpack': self.unpack,
                'url': self.url,
                'version': self.version,
                'experimentName': self.experiment_name,
                'runId': self.run_id,
                'runDetails': self.run.__str__(),
                'datasets': datasets}

    @staticmethod
    def deserialize(workspace, model_payload):
        """Convert a json object into a Model object.

        Will fail if the provided workspace is not the workspace the model is registered under.

        :param workspace: The workspace object the model is registered under
        :type workspace: azureml.core.workspace.Workspace
        :param model_payload: A json object to convert to a Model object
        :type model_payload: dict
        :return: The Model representation of the provided json object
        :rtype: azureml.core.Model
        """
        Model._validate_get_payload(model_payload)
        model = Model(None)
        model._initialize(workspace, model_payload)
        return model

    def update(self, tags):
        """Perform an inplace update of the model.

        :param tags: A dictionary of tags to update the model with. With replace what currently exists
        :type tags: dict[str, str]
        :raises: WebserviceException
        """
        headers = {'Content-Type': 'application/json-patch+json'}
        headers.update(self._auth.get_authentication_header())
        params = {'api-version': MMS_WORKSPACE_API_VERSION}

        patch_list = []
        self.tags = tags
        patch_list.append({'op': 'replace', 'path': '/kvTags', 'value': self.tags})

        resp = ClientBase._execute_func(get_requests_session().patch, self._mms_endpoint, headers=headers,
                                        params=params, json=patch_list, timeout=MMS_SYNC_TIMEOUT_SECONDS)

        if resp.status_code >= 400:
            raise WebserviceException('Received bad response from Model Management Service:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content),
                                      logger=module_logger)

    def update_tags_properties(self, add_tags=None, remove_tags=None, add_properties=None):
        """Perform an update of the model's tags and properties.

        :param add_tags: A dictionary of tags to add
        :type add_tags: dict[str, str]
        :param remove_tags: A list of tag names to remove
        :type remove_tags: :class:`list[str]`
        :param add_properties: A dictionary of properties to add
        :type add_properties: dict[str, str]
        :raises: WebserviceException
        """
        check_duplicate_properties(self.properties, add_properties)

        headers = {'Content-Type': 'application/json-patch+json'}
        headers.update(self._auth.get_authentication_header())
        params = {'api-version': MMS_WORKSPACE_API_VERSION}

        patch_list = []

        # handle tags update, if a tag is in both add_tags and remove_tags,
        # the expected behavior is undefined. So it doesn't matter how we solve such confliction.
        tag_update = False

        # handle add_tags
        if add_tags is not None:
            tag_update = True
            if self.tags is None:
                self.tags = copy.deepcopy(add_tags)
            else:
                for key in add_tags:
                    if key in self.tags:
                        print("Replacing tag {} -> {} with {} -> {}".format(key, self.tags[key],
                                                                            key, add_tags[key]))
                    self.tags[key] = add_tags[key]

        # handle remove_tags
        if remove_tags is not None:
            if self.tags is None:
                print('Model has no tags to remove.')
            else:
                tag_update = True
                if not isinstance(remove_tags, list):
                    remove_tags = [remove_tags]
                for key in remove_tags:
                    if key in self.tags:
                        del self.tags[key]
                    else:
                        print('Tag with key {} not found.'.format(key))

        # add add "tag replace" op when there's tag update
        if tag_update:
            patch_list.append({'op': 'replace', 'path': '/kvTags', 'value': self.tags})

        # handle add_properties
        if add_properties is not None:
            if self.properties is None:
                self.properties = copy.deepcopy(add_properties)
            else:
                for key in add_properties:
                    self.properties[key] = add_properties[key]

            patch_list.append({'op': 'add', 'path': '/properties', 'value': self.properties})

        # only call MMS REST API where patch_list is not empty
        if not patch_list:
            return

        resp = ClientBase._execute_func(get_requests_session().patch, self._mms_endpoint, headers=headers,
                                        params=params, json=patch_list, timeout=MMS_SYNC_TIMEOUT_SECONDS)

        if resp.status_code >= 400:
            raise WebserviceException('Received bad response from Model Management Service:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content),
                                      logger=module_logger)

    def add_tags(self, tags):
        """Add key value pairs to this model's tags dictionary.

        :param tags: The dictionary of tags to add
        :type tags: dict[str, str]
        :raises: WebserviceException
        """
        self.update_tags_properties(add_tags=tags)
        print('Model tag add operation complete.')

    def remove_tags(self, tags):
        """Remove the specified keys from this model's dictionary of tags.

        :param tags: The list of keys to remove
        :type tags: :class:`list[str]`
        """
        self.update_tags_properties(remove_tags=tags)
        print('Model tag remove operation complete.')

    def add_properties(self, properties):
        """Add key value pairs to this model's properties dictionary.

        :param properties: The dictionary of properties to add
        :type properties: dict[str, str]
        """
        self.update_tags_properties(add_properties=properties)
        print('Model properties add operation complete.')

    def add_dataset_references(self, datasets):
        """
        Associate the provided datasets with this Model.

        :param datasets: A list of tuples representing a pairing of dataset purpose to Dataset object
        :type datasets: :class:`list[(str, Dataset | DatasetSnapshot)]`
        :raises: WebserviceException
        """
        headers = {'Content-Type': 'application/json-patch+json'}
        headers.update(self._auth.get_authentication_header())
        params = {'api-version': MMS_WORKSPACE_API_VERSION}

        dataset_dicts = []
        for dataset_pair in datasets:
            dataset_scenario = dataset_pair[0]
            dataset = dataset_pair[1]
            if type(dataset) is Dataset:
                dataset_dicts.append({'name': dataset_scenario, 'id': dataset.id})
            elif type(dataset) is DatasetSnapshot:
                dataset_dicts.append({'name': dataset_scenario, 'id': DATASET_SNAPSHOT_ID_FORMAT.format(
                    dataset_id=dataset.dataset_id, dataset_snapshot_name=dataset.name)})
            else:
                raise WebserviceException('Invalid dataset of type {} passed, must be of type Dataset or '
                                          'DatasetSnapshot'.format(type(dataset)), logger=module_logger)

        patch_list = [{'op': 'add', 'path': '/datasets', 'value': dataset_dicts}]

        resp = ClientBase._execute_func(get_requests_session().patch, self._mms_endpoint, headers=headers,
                                        params=params, json=patch_list, timeout=MMS_SYNC_TIMEOUT_SECONDS)

        if resp.status_code >= 400:
            raise WebserviceException('Received bad response from Model Management Service:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content),
                                      logger=module_logger)

        for dataset_pair in datasets:
            dataset_scenario = dataset_pair[0]
            dataset = dataset_pair[1]

            self.datasets.setdefault(dataset_scenario, []).append(dataset)

    def delete(self):
        """Delete this model from its associated workspace.

        :raises: WebserviceException
        """
        headers = self._auth.get_authentication_header()
        params = {'api-version': MMS_WORKSPACE_API_VERSION}

        resp = ClientBase._execute_func(get_requests_session().delete, self._mms_endpoint, headers=headers,
                                        params=params)

        if resp.status_code >= 400:
            raise WebserviceException('Received bad response from Model Management Service:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content),
                                      logger=module_logger)

    @staticmethod
    def _validate_get_payload(payload):
        """Validate the returned model payload.

        :param payload:
        :type payload: dict
        :return:
        :rtype: None
        """
        for payload_key in Model._expected_payload_keys:
            if payload_key not in payload:
                raise WebserviceException('Invalid model payload, missing {} for model:\n'
                                          '{}'.format(payload_key, payload), logger=module_logger)

    @staticmethod
    def deploy(workspace, name, models, inference_config, deployment_config=None, deployment_target=None):
        """Deploy a Webservice from zero or more model objects.

        This function is similar to :func:`deploy`, but does not :func:`azureml.core.model.Model.register` the
        models. Use this function if you have model objects that are already registered. This will create an image
        in the process, associated with the specified Workspace.

        :param workspace: A Workspace object to associate the Webservice with
        :type workspace: azureml.core.workspace.Workspace
        :param name: The name to give the deployed service. Must be unique to the workspace, only consist of lowercase
            letters, numbers, or dashes, start with a letter, and be between 3 and 32 characters long.
        :type name: str
        :param models: A list of model objects. Can be an empty list.
        :type models: :class:`list[azureml.core.model.Model]`
        :param inference_config: An InferenceConfig object used to determine required model properties.
        :type inference_config: azureml.core.model.InferenceConfig
        :param deployment_config: A WebserviceDeploymentConfiguration used to configure the webservice. If one is not
            provided, an empty configuration object will be used based on the desired target.
        :type deployment_config: WebserviceDeploymentConfiguration
        :param deployment_target: A ComputeTarget to deploy the Webservice to. As Azure Container Instances has
            no associated ComputeTarget, leave this parameter as None to deploy to Azure Container Instances.
        :type deployment_target: azureml.core.compute.ComputeTarget
        :return: A Webservice object corresponding to the deployed webservice
        :rtype: azureml.core.webservice.webservice.Webservice
        :raises: WebserviceException
        """
        from azureml.core.webservice import Webservice
        from azureml.core.webservice.local import LocalWebserviceDeploymentConfiguration

        webservice_name_validation(name)

        if deployment_config and (type(deployment_config) is LocalWebserviceDeploymentConfiguration):
            service = deployment_config._webservice_type._deploy(workspace, name, models,
                                                                 inference_config._convert_to_image_conf_for_local(),
                                                                 deployment_config)
            return service
        else:
            return Webservice.deploy_from_model(workspace, name, models, inference_config,
                                                deployment_config, deployment_target)

    @staticmethod
    def profile(workspace, profile_name, models, inference_config, input_data):
        """Profiles this model to get resource requirement recommendations.

        :param workspace: A Workspace object in which to profile the model
        :type workspace: azureml.core.workspace.Workspace
        :param profile_name: The name of the profiling run
        :type profile_name: str
        :param models: A list of model objects. Can be an empty list.
        :type models: :class:`list[azureml.core.model.Model]`
        :param inference_config: An InferenceConfig object used to determine required model properties.
        :type inference_config: azureml.core.model.InferenceConfig
        :param input_data: The input data for profiling
        :type input_data: str
        :rtype: azureml.core.image.Image
        :raises: azureml.exceptions.WebserviceException
        """
        from azureml.core.image import Image
        image = Image.create(workspace, profile_name, models, inference_config)
        image.wait_for_creation(True)
        if image.creation_state != 'Succeeded':
            raise WebserviceException('Error occurred creating model package {} for profiling. More information can '
                                      'be found here: {}, generated DockerFile can be found here: {}'.format(
                                          image.id,
                                          image.image_build_log_uri,
                                          image.generated_dockerfile_uri), logger=module_logger)

        headers = {'Content-Type': 'application/json'}
        headers.update(workspace._auth.get_authentication_header())
        params = {'api-version': MMS_WORKSPACE_API_VERSION}
        base_endpoint = _get_mms_url(workspace)
        profile_url = '{0}/images/{1}/profiles'.format(base_endpoint, image.id)

        json_payload = inference_config.build_profile_payload(profile_name, input_data)

        module_logger.info('Profiling model')
        resp = ClientBase._execute_func(get_requests_session().post, profile_url, params=params, headers=headers,
                                        json=json_payload)
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            raise WebserviceException('Received bad response from Model Management Service:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content),
                                      logger=module_logger)
        if resp.status_code >= 400:
            raise WebserviceException('Error occurred profiling model:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content),
                                      logger=module_logger)

        if 'Operation-Location' in resp.headers:
            operation_location = resp.headers['Operation-Location']
        else:
            raise WebserviceException('Missing response header key: Operation-Location', logger=module_logger)

        create_operation_status_id = operation_location.split('/')[-1]
        operation_url = base_endpoint + '/operations/{}'.format(create_operation_status_id)
        operation_headers = workspace._auth.get_authentication_header()

        operation_resp = ClientBase._execute_func(get_requests_session().get, operation_url, params=params,
                                                  headers=operation_headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
        try:
            operation_resp.raise_for_status()
        except requests.Timeout:
            raise WebserviceException('Error, request to {} timed out.'.format(operation_url), logger=module_logger)
        except requests.exceptions.HTTPError:
            raise WebserviceException('Received bad response from Model Management Service:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(operation_resp.status_code,
                                                           operation_resp.headers,
                                                           operation_resp.content), logger=module_logger)

        content = operation_resp.content
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        operation_content = json.loads(content)
        if 'resourceLocation' in operation_content:
            profiling_name = operation_content['resourceLocation'].split('/')[-1]
        else:
            raise WebserviceException('Invalid operation payload, missing resourceLocation:\n'
                                      '{}'.format(operation_content), logger=module_logger)

        profile = ModelProfile(workspace, image.id, profiling_name)
        profile._operation_endpoint = operation_url
        return profile

    class Framework(object):
        """Well known constants for supported framework types."""

        CUSTOM = "Custom"
        TFKERAS = "TfKeras"
        SCIKITLEARN = "ScikitLearn"


class InferenceConfig(object):
    """
    Model deployment config specific to model deployments - requires entry_script and runtime.

    :param entry_script: Path to local file that contains the code to run for the image
    :type entry_script: str
    :param runtime: Which runtime to use for the image. Current supported runtimes are 'spark-py' and 'python'
    :type runtime: str
    :param conda_file: Path to local file containing a conda environment definition to use for the image
    :type conda_file: str
    :param extra_docker_file_steps: Path to local file containing additional Docker steps to run when setting up image
    :type extra_docker_file_steps: str
    :param source_directory: paths to folders that contains all files to create the image
    :type source_directory: : str
    :param enable_gpu: Whether or not to enable GPU support in the image. The GPU image must be used on Microsoft
        Azure Services only such as ACI, AML Compute, Azure VMs, and AKS. Defaults to False
    :type enable_gpu: bool
    :param description: A description to give this image
    :type description: str
    :param base_image: A custom image to be used as base image. If no base image is given then the base image
        will be used based off of given runtime parameter.
    :type base_image: str
    :param base_image_registry: Image registry that contains the base image.
    :type base_image_registry: azureml.core.container_registry.ContainerRegistry
    """

    def __init__(self, entry_script, runtime, conda_file=None, extra_docker_file_steps=None,
                 source_directory=None, enable_gpu=None, description=None,
                 base_image=None, base_image_registry=None):
        """Initialize the config object.

        :param entry_script: Path to local file that contains the code to run for the image
        :type entry_script: str
        :param runtime: Which runtime to use for the image. Current supported runtimes are 'spark-py' and 'python'
        :type runtime: str
        :param conda_file: Path to local file containing a conda environment definition to use for the image
        :type conda_file: str
        :param extra_docker_file_steps: Path to local file containing extra Docker steps to run when setting up image
        :type extra_docker_file_steps: str
        :param source_directory: paths to folders that contains all files to create the image
        :type source_directory: : str
        :param enable_gpu: Whether or not to enable GPU support in the image. The GPU image must be used on Microsoft
            Azure Services only such as ACI, AML Compute, Azure VMs, and AKS. Defaults to False
        :type enable_gpu: bool
        :param description: A description to give this image
        :type description: str
        :param base_image: A custom image to be used as base image. If no base image is given then the base image
            will be used based off of given runtime parameter.
        :type base_image: str
        :param base_image_registry: Image registry that contains the base image.
        :type base_image_registry: azureml.core.container_registry.ContainerRegistry
        :raises: azureml.exceptions.WebserviceException
        """
        self.entry_script = entry_script
        self.runtime = runtime
        self.conda_file = conda_file
        self.extra_docker_file_steps = extra_docker_file_steps
        self.source_directory = source_directory
        self.enable_gpu = enable_gpu
        self.description = description
        self.base_image = base_image
        self.base_image_registry = base_image_registry

        self.validate_configuration()

    def _convert_to_image_conf_for_local(self):
        """ONLY FOR LOCAL DEPLOYMENT USE.

        Return an image configuration class using the attributes of this Inference config class.

        :return: ContainerImage configuration class
        :rtype: azureml.core.image.container.ContainerImageConfig
        """
        dependencies = []
        if self.source_directory:
            dependencies = [self.source_directory] if self.source_directory else []

        from azureml.core.image.container import ContainerImageConfig
        return ContainerImageConfig(joinPath(self.source_directory, self.entry_script),
                                    self.runtime,
                                    joinPath(self.source_directory, self.conda_file),
                                    joinPath(self.source_directory, self.extra_docker_file_steps),
                                    None, dependencies, self.enable_gpu, None, None,
                                    self.description, self.base_image, self.base_image_registry, True)

    def validate_configuration(self):
        """Check that the specified configuration values are valid.

        Will raise a WebserviceException if validation fails.

        :raises: WebserviceException
        """
        if self.source_directory:
            self.source_directory = os.path.realpath(self.source_directory)
            validate_path_exists_or_throw(self.source_directory, "source directory")

        validate_path_exists_or_throw(joinPath(self.source_directory, self.entry_script), "entry_script")

        script_name, script_extension = os.path.splitext(os.path.basename(self.entry_script))
        if script_extension != '.py':
            raise WebserviceException('Invalid driver type. Currently only Python drivers are supported.',
                                      logger=module_logger)
        validate_entry_script_name(script_name)

        if self.runtime and (self.runtime.lower() not in SUPPORTED_RUNTIMES.keys()):
            runtimes = '|'.join(x for x in SUPPORTED_RUNTIMES.keys() if x not in UNDOCUMENTED_RUNTIMES)
            raise WebserviceException('Provided runtime not supported. '
                                      'Possible runtimes are: {}'.format(runtimes),
                                      logger=module_logger)

        if self.conda_file:
            validate_path_exists_or_throw(joinPath(self.source_directory, self.conda_file), "Conda file")

        if self.extra_docker_file_steps:
            validate_path_exists_or_throw(joinPath(self.source_directory, self.extra_docker_file_steps),
                                          "extra docker file steps")

    def build_create_payload(self, workspace, name, model_ids):
        """Build the creation payload for the Container image.

        :param workspace: The workspace object to create the image in
        :type workspace: azureml.core.workspace.Workspace
        :param name: The name of the image
        :type name: str
        :param model_ids: A list of model IDs to package into the image
        :type model_ids: :class:`list[str]`
        :return: Container image creation payload
        :rtype: dict
        :raises: azureml.exceptions.WebserviceException
        """
        import copy
        from azureml._model_management._util import image_payload_template
        json_payload = copy.deepcopy(image_payload_template)
        json_payload['name'] = name
        json_payload['imageFlavor'] = WEBAPI_IMAGE_FLAVOR
        json_payload['description'] = self.description
        json_payload['targetRuntime']['runtimeType'] = SUPPORTED_RUNTIMES[self.runtime.lower()]
        json_payload['targetRuntime']['targetArchitecture'] = ARCHITECTURE_AMD64

        if self.enable_gpu:
            json_payload['targetRuntime']['properties']['installCuda'] = self.enable_gpu
        requirements = add_sdk_to_requirements()
        (json_payload['targetRuntime']['properties']['pipRequirements'], _) = \
            upload_dependency(workspace, requirements)
        if self.conda_file:
            conda_file = self.conda_file.rstrip(os.sep)
            conda_file = joinPath(self.source_directory, self.conda_file)
            (json_payload['targetRuntime']['properties']['condaEnvFile'], _) = \
                upload_dependency(workspace, conda_file)
        if self.extra_docker_file_steps:
            extra_docker_file_steps = self.extra_docker_file_steps.rstrip(os.sep)
            extra_docker_file_steps = joinPath(self.source_directory, self.extra_docker_file_steps)
            (json_payload['dockerFileUri'], _) = upload_dependency(workspace, extra_docker_file_steps)

        if model_ids:
            json_payload['modelIds'] = model_ids

        self.entry_script = self.entry_script.rstrip(os.sep)

        driver_mime_type = 'application/x-python'
        scoring_base_name = ''
        script_location = os.path.basename(self.entry_script)

        if self.source_directory:
            scoring_base_name = os.path.basename(self.source_directory)
            script_location = self.entry_script

        wrapped_execution_script = wrap_execution_script_with_source_directory(scoring_base_name,
                                                                               script_location,
                                                                               True)

        (driver_package_location, _) = upload_dependency(workspace, wrapped_execution_script)
        json_payload['assets'].append({'id': 'driver', 'url': driver_package_location, 'mimeType': driver_mime_type})

        if self.source_directory:
            (artifact_url, artifact_id) = upload_dependency(workspace, self.source_directory,
                                                            True, os.path.basename(self.source_directory))
            json_payload['assets'].append({'mimeType': 'application/octet-stream', 'id': artifact_id,
                                           'url': artifact_url, 'unpack': True})
        else:
            (artifact_url, artifact_id) = upload_dependency(workspace, self.entry_script)
            json_payload['assets'].append({'mimeType': 'application/octet-stream',
                                           'id': artifact_id,
                                           'url': artifact_url})

        self._add_base_image_to_payload(json_payload)

        return json_payload

    def _add_base_image_to_payload(self, json_payload):
        if self.base_image:
            if not self.runtime.lower() in CUSTOM_BASE_IMAGE_SUPPORTED_RUNTIMES.keys():
                runtimes = '|'.join(CUSTOM_BASE_IMAGE_SUPPORTED_RUNTIMES.keys())
                raise WebserviceException('Custom base image is not supported for {} run time. '
                                          'Supported runtimes are: {}'.format(self.runtime, runtimes),
                                          logger=module_logger)
            json_payload['baseImage'] = self.base_image
            json_payload['targetRuntime']['runtimeType'] = CUSTOM_BASE_IMAGE_SUPPORTED_RUNTIMES[self.runtime.lower()]

            if self.base_image_registry is not None:
                if self.base_image_registry.address and \
                        self.base_image_registry.username and \
                        self.base_image_registry.password:
                            json_payload['baseImageRegistryInfo'] = {'location': self.base_image_registry.address,
                                                                     'user': self.base_image_registry.username,
                                                                     'password': self.base_image_registry.password}
                elif self.base_image_registry.address or \
                        self.base_image_registry.username or \
                        self.base_image_registry.password:
                            raise WebserviceException('Address, Username and Password '
                                                      'must be provided for base image registry', logger=module_logger)

    def build_profile_payload(self, profile_name, input_data):
        """Build the profiling payload for the Model package.

        :param profile_name: The name of the profile
        :type profile_name: str
        :param input_data: The input data for profiling
        :type input_data: str
        :return: Model profile payload
        :rtype: dict
        :raises: azureml.exceptions.WebserviceException
        """
        import copy
        from azureml._model_management._util import profile_payload_template
        json_payload = copy.deepcopy(profile_payload_template)
        json_payload['name'] = profile_name
        json_payload['description'] = self.description
        json_payload['inputData'] = input_data
        return json_payload
