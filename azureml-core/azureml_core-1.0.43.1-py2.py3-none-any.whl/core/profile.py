# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains class for retrieving a cloud representation of a Profile object associated with a Workspace."""
import json
import logging
import requests
import sys
import time
from azureml.exceptions import WebserviceException
from azureml._model_management._constants import MMS_SYNC_TIMEOUT_SECONDS
from azureml._model_management._constants import MMS_WORKSPACE_API_VERSION
from azureml._model_management._constants import PROFILE_RECOMMENDED_CPU_KEY, PROFILE_RECOMMENDED_MEMORY_KEY
from azureml._model_management._util import _get_mms_url
from dateutil.parser import parse

module_logger = logging.getLogger(__name__)


class ModelProfile():
    """
    ModelProfile object that contains the results of a profiling run.

    :param workspace: The workspace object containing the image to retrieve
    :type workspace: azureml.core.workspace.Workspace
    :param image_id: ID of the image associated with the profile name
    :type image_id: str
    :param name: The name of the profile to retrieve.
    :type name: str
    :param description: Field for profile description
    :type description: str
    :param input_data: The input data used for profiling
    :type input_data: varies
    :param tags: Dictionary of mutable tags
    :type tags: dict[str, str]
    :param properties: Dictionary of appendable properties
    :type properties: dict[str, str]
    :param recommended_memory: The memory recommendation result from profiling in GB
    :type recommended_memory: float
    :param recommended_cpu: The cpu recommendation result from profiling in cores
    :type recommended_cpu: float
    :param recommended_memory_latency: The 90th percentile latency of requests while profiling with
        recommended memory value
    :type recommended_memory_latency: float
    :param recommneded_cpu_latency: The 90th percentile latency of requests while profiling with
        recommended cpu value
    :type recommended_cpu_latency: float
    :param profile_result_url: URL to profiling results
    :type profile_result_url: str
    :param error_logs: URL to profiling error logs
    :type error_logs: str
    :rtype: azureml.core.profile.ModelProfile
    :raises: WebserviceException
    """

    _expected_payload_keys = ['name', 'description', 'imageId', 'inputData', 'createdTime', 'kvTags', 'properties']

    def __init__(self, workspace, image_id, name, description=None, input_data=None, tags=None, properties=None,
                 recommended_memory=None, recommended_cpu=None, recommended_memory_latency=None,
                 recommended_cpu_latency=None, profile_result_url=None, error=None, error_logs=None):
        """Initialize the ModelProfile object.

        :param workspace: The workspace object containing the image to retrieve
        :type workspace: azureml.core.workspace.Workspace
        :param image_id: ID of the image associated with the profile name
        :type image_id: str
        :param name: The name of the profile to retrieve.
        :type name: str
        :param description: Field for profile description
        :type description: str
        :param input_data: The input data used for profiling
        :type input_data: varies
        :param tags: Dictionary of mutable tags
        :type tags: dict[str, str]
        :param properties: Dictionary of appendable properties
        :type properties: dict[str, str]
        :param recommended_memory: The memory recommendation result from profiling in GB
        :type recommended_memory: float
        :param recommended_cpu: The cpu recommendation result from profiling in cores
        :type recommended_cpu: float
        :param recommended_memory_latency: The 90th percentile latency of requests while profiling with
            recommended memory value
        :type recommended_memory_latency: float
        :param recommneded_cpu_latency: The 90th percentile latency of requests while profiling with
            recommended cpu value
        :type recommended_cpu_latency: float
        :param profile_result_url: URL to profiling results
        :type profile_result_url: str
        :param error_logs: URL to profiling error logs
        :type error_logs: str
        :rtype: azureml.core.profile.ModelProfile
        :raises: WebserviceException
        """
        self.description = description
        self.input_data = input_data
        self.tags = tags
        self.properties = properties
        self.recommended_memory = recommended_memory
        self.recommended_cpu = recommended_cpu
        self.recommended_memory_latency = recommended_memory_latency
        self.recommended_cpu_latency = recommended_cpu_latency
        self.profile_result_url = profile_result_url
        self.error = error
        self.error_logs = error_logs

        if workspace and image_id and name:
            get_response_payload = self._get(workspace, image_id, name)
            if get_response_payload:
                self._validate_get_payload(get_response_payload)
                self._initialize(workspace, get_response_payload)
            else:
                error_message = 'ModelProfileNotFound: ModelProfile with '
                if name:
                    error_message += 'name {}'.format(tags)
                if image_id:
                    error_message += ', Model package {}'.format(image_id)
                error_message += ' not found in provided workspace'
                raise WebserviceException(error_message)

    def __repr__(self):
        """Return the string representation of the Image object.

        :return: String representation of the Image object
        :rtype: str
        """
        return "{}(workspace={}, name={}, image_id={}, tags={}, properties={})".format(self.__class__.__name__,
                                                                                       self.workspace.__repr__(),
                                                                                       self.name,
                                                                                       self.image_id,
                                                                                       self.tags,
                                                                                       self.properties)

    def _initialize(self, workspace, obj_dict):
        """Initialize the Profile instance.

        This is used because the constructor is used as a getter.

        :param workspace:
        :type workspace: azureml.core.workspace.Workspace
        :param obj_dict:
        :type obj_dict: dict
        :return:
        :rtype: None
        """
        created_time = parse(obj_dict['createdTime'])
        self.created_time = created_time
        self.name = obj_dict['name']
        self.description = obj_dict['description']
        self.image_id = obj_dict['imageId']
        self.input_data = obj_dict['inputData']
        self.tags = obj_dict['kvTags']
        self.properties = obj_dict['properties']
        self.state = obj_dict['state']
        self.workspace = workspace
        self._auth = workspace._auth
        self.recommended_memory = obj_dict.get("recommendedMemoryInGB")
        self.recommended_cpu = obj_dict.get("recommendedCpu")
        self.recommended_memory_latency = obj_dict.get("recommendedMemoryLatencyInMs")
        self.recommended_cpu_latency = obj_dict.get("recommendedCpuLatencyInMs")
        self.profile_result_url = obj_dict.get("profileRunResult")
        self.error = obj_dict.get("error")
        self.error_logs = obj_dict.get("profilingErrorLogs")
        self._mms_endpoint = _get_mms_url(workspace) + '/images/{0}/profiles/{1}'.format(self.image_id, self.name)

    @staticmethod
    def _get(workspace, image_id, name):
        """Retrieve the Profile object from the cloud.

        :param workspace:
        :type workspace: workspace: azureml.core.workspace.Workspace
        :param image_id: ID of the Image used for profiling
        :type image_id: str
        :param name: Name of the profiling run
        :type name: str
        :return:
        :rtype: dict
        """
        headers = workspace._auth.get_authentication_header()
        params = {'api-version': MMS_WORKSPACE_API_VERSION, 'orderBy': 'CreatedAtDesc', 'count': 1}
        base_url = _get_mms_url(workspace)
        profile_url = '{0}/images/{1}/profiles/{2}'.format(base_url, image_id, name)

        resp = requests.get(profile_url, headers=headers, params=params)
        if resp.status_code == 200:
            content = resp.content
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            profile_payload = json.loads(content)
            return profile_payload
        elif resp.status_code == 404:
            return None
        else:
            raise WebserviceException('Received bad response from Model Management Service:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content))

    @classmethod
    def _validate_get_payload(cls, payload):
        """Validate the returned ModelProfile payload.

        :param payload:
        :type payload: dict
        :return:
        :rtype: None
        """
        for payload_key in ModelProfile._expected_payload_keys:
            if payload_key not in payload:
                raise WebserviceException('Invalid model profile payload, missing {} for model profile:\n'
                                          '{}'.format(payload_key, payload))

    def wait_for_profiling(self, show_output=False):
        """Wait for the model to finish profiling.

        :param show_output: Boolean option to print more verbose output. Defaults to False
        :type show_output: bool
        """
        operation_state, error = self._get_operation_state(MMS_WORKSPACE_API_VERSION)
        current_state = operation_state
        if show_output:
            sys.stdout.write('{}'.format(current_state))
            sys.stdout.flush()
        while operation_state != 'Cancelled' and operation_state != 'Succeeded' and operation_state != 'Failed' \
                and operation_state != 'TimedOut':
            time.sleep(5)
            operation_state, error = self._get_operation_state(MMS_WORKSPACE_API_VERSION)
            if show_output:
                sys.stdout.write('.')
                if operation_state != current_state:
                    sys.stdout.write('\n{}'.format(operation_state))
                    current_state = operation_state
                sys.stdout.flush()
        module_logger.info('Model profiling operation finished for model package '
                           '{}, operation "{}"'.format(self.image_id, operation_state))
        if operation_state == 'Failed':
            if error and 'statusCode' in error and 'message' in error:
                module_logger.info('Model profiling failed with\n'
                                   'StatusCode: {}\n'
                                   'Message: {}'.format(error['statusCode'], error['message']))
            else:
                module_logger.info('Model profiling failed, unexpected error response:\n'
                                   '{}'.format(error))
        self.update_creation_state()

    def _get_operation_state(self, api_version):
        """Get the current async operation state for the Profile.

        :param api_version:
        :type api_version: str
        :return:
        :rtype: (str, dict)
        """
        headers = {'Content-Type': 'application/json'}
        headers.update(self._auth.get_authentication_header())
        params = {'api-version': api_version}

        resp = requests.get(self._operation_endpoint, headers=headers, params=params, timeout=MMS_SYNC_TIMEOUT_SECONDS)
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            raise WebserviceException('Received bad response from Resource Provider:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content))
        content = resp.content
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        content = json.loads(content)
        state = content['state']
        error = content['error'] if 'error' in content else None
        return state, error

    def update_creation_state(self):
        """Refresh the current state of the in-memory object.

        Perform an in-place update of the properties of the object based on the current state of the
        corresponding cloud object. Primarily useful for manual polling of creation state.

        :raises: WeberviceException
        """
        headers = {'Content-Type': 'application/json'}
        headers.update(self._auth.get_authentication_header())
        params = {'api-version': MMS_WORKSPACE_API_VERSION}

        resp = requests.get(self._mms_endpoint, headers=headers, params=params, timeout=MMS_SYNC_TIMEOUT_SECONDS)

        if resp.status_code == 200:
            profile = ModelProfile(self.workspace, image_id=self.image_id, name=self.name)
            for key in profile.__dict__.keys():
                if key is not "_operation_endpoint":
                    self.__dict__[key] = profile.__dict__[key]
        elif resp.status_code == 404:
            raise WebserviceException('Error: profile {} not found:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(self.name, resp.status_code, resp.headers, resp.content))
        else:
            raise WebserviceException('Received bad response from Model Management Service:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content))

    def get_results(self):
        """Return the recommended resource requirements from the profiling run to the user.

        :return: Dictionary of recommended resource requirements
        :rtype: dict[str, float]
        """
        if self.recommended_cpu is None or self.recommended_memory is None:
            raise WebserviceException('The profile with name {} and model package {} has not completed '
                                      'yet.'.format(self.name, self.image_id))
        else:
            return {PROFILE_RECOMMENDED_CPU_KEY: self.recommended_cpu,
                    PROFILE_RECOMMENDED_MEMORY_KEY: self.recommended_memory}

    def serialize(self):
        """Convert this Profile into a json serialized dictionary.

        :return: The json representation of this Profile
        :rtype: dict
        """
        created_time = self.created_time.isoformat() if self.created_time else None

        return {'name': self.name, 'createdTime': created_time, 'description': self.description,
                'inputData': self.input_data, 'tags': self.tags, 'properties': self.properties,
                'recommendedMemoryInGB': self.recommended_memory, 'recommendedCpu': self.recommended_cpu,
                'recommendedMemoryLatencyInMs': self.recommended_memory_latency,
                'recommendedCpuLatencyInMs': self.recommended_cpu_latency,
                'profileRunResult': self.profile_result_url, "state": self.state,
                'error': self.error, 'profilingErrorLogs': self.error_logs}
