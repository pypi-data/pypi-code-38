# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for managing the Azure Kubernetes Service Webservices in Azure Machine Learning service."""

import logging
import re
import uuid
from azureml._base_sdk_common.tracking import global_tracking_info_registry
from azureml._model_management._constants import AKS_WEBSERVICE_TYPE
from azureml._model_management._constants import MMS_WORKSPACE_API_VERSION
from azureml._model_management._constants import NAMESPACE_REGEX
from azureml._model_management._constants import WEBSERVICE_SWAGGER_PATH
from azureml._model_management._util import get_requests_session
from azureml._restclient.clientbase import ClientBase
from azureml.core.image import Image
from azureml.core.webservice import Webservice
from azureml.core.webservice.webservice import WebserviceDeploymentConfiguration
from azureml.exceptions import WebserviceException

module_logger = logging.getLogger(__name__)


class AksWebservice(Webservice):
    """Class for Azure Kubernetes Service Webservices."""

    _expected_payload_keys = Webservice._expected_payload_keys + \
        ['appInsightsEnabled', 'authEnabled', 'autoScaler', 'computeName', 'containerResourceRequirements',
         'dataCollection', 'maxConcurrentRequestsPerContainer', 'maxQueueWaitMs', 'numReplicas', 'scoringTimeoutMs',
         'scoringUri', 'livenessProbeRequirements']
    _webservice_type = AKS_WEBSERVICE_TYPE

    def _initialize(self, workspace, obj_dict):
        """Initialize the Webservice instance.

        This is used because the constructor is used as a getter.

        :param workspace:
        :type workspace: azureml.core.workspace.Workspace
        :param obj_dict:
        :type obj_dict: dict
        :return:
        :rtype: None
        """
        # Validate obj_dict with _expected_payload_keys
        AksWebservice._validate_get_payload(obj_dict)

        # Initialize common Webservice attributes
        super(AksWebservice, self)._initialize(workspace, obj_dict)

        # Initialize expected AksWebservice specific attributes
        self.enable_app_insights = obj_dict['appInsightsEnabled']
        self.autoscaler = AutoScaler.deserialize(obj_dict['autoScaler'])
        self.compute_name = obj_dict['computeName']
        self.container_resource_requirements = \
            ContainerResourceRequirements.deserialize(obj_dict['containerResourceRequirements'])
        self.liveness_probe_requirements = \
            LivenessProbeRequirements.deserialize(obj_dict['livenessProbeRequirements'])
        self.data_collection = DataCollection.deserialize(obj_dict['dataCollection'])
        self.max_concurrent_requests_per_container = obj_dict['maxConcurrentRequestsPerContainer']
        self.max_request_wait_time = obj_dict['maxQueueWaitMs']
        self.num_replicas = obj_dict['numReplicas']
        self.scoring_timeout_ms = obj_dict['scoringTimeoutMs']
        self.scoring_uri = obj_dict['scoringUri']

        # Initialize other AKS utility attributes
        self.image = Image.deserialize(workspace, obj_dict['imageDetails']) if 'imageDetails' in obj_dict else None
        self.deployment_status = obj_dict['deploymentStatus'] if 'deploymentStatus' in obj_dict else None
        self.namespace = obj_dict.get('namespace')
        self.swagger_uri = '/'.join(self.scoring_uri.split('/')[:-1]) + WEBSERVICE_SWAGGER_PATH \
            if self.scoring_uri else None

    @staticmethod
    def deploy_configuration(autoscale_enabled=None, autoscale_min_replicas=None, autoscale_max_replicas=None,
                             autoscale_refresh_seconds=None, autoscale_target_utilization=None,
                             collect_model_data=None, auth_enabled=None, cpu_cores=None, memory_gb=None,
                             enable_app_insights=None, scoring_timeout_ms=None, replica_max_concurrent_requests=None,
                             max_request_wait_time=None, num_replicas=None, primary_key=None, secondary_key=None,
                             tags=None, properties=None, description=None, gpu_cores=None, period_seconds=None,
                             initial_delay_seconds=None, timeout_seconds=None, success_threshold=None,
                             failure_threshold=None, namespace=None):
        """Create a configuration object for deploying to an AKS compute target.

        :param autoscale_enabled: Whether or not to enable autoscaling for this Webservice.
            Defaults to True if num_replicas is None
        :type autoscale_enabled: bool
        :param autoscale_min_replicas: The minimum number of containers to use when autoscaling this Webservice.
            Defaults to 1
        :type autoscale_min_replicas: int
        :param autoscale_max_replicas: The maximum number of containers to use when autoscaling this Webservice.
            Defaults to 10
        :type autoscale_max_replicas: int
        :param autoscale_refresh_seconds: How often the autoscaler should attempt to scale this Webservice.
            Defaults to 1
        :type autoscale_refresh_seconds: int
        :param autoscale_target_utilization: The target utilization (in percent out of 100) the autoscaler should
            attempt to maintain for this Webservice. Defaults to 70
        :type autoscale_target_utilization: int
        :param collect_model_data: Whether or not to enable model data collection for this Webservice.
            Defaults to False
        :type collect_model_data: bool
        :param auth_enabled: Whether or not to enable auth for this Webservice. Defaults to True
        :type auth_enabled: bool
        :param cpu_cores: The number of cpu cores to allocate for this Webservice. Can be a decimal. Defaults to 0.1
        :type cpu_cores: float
        :param memory_gb: The amount of memory (in GB) to allocate for this Webservice. Can be a decimal.
            Defaults to 0.5
        :type memory_gb: float
        :param enable_app_insights: Whether or not to enable Application Insights logging for this Webservice.
            Defaults to False
        :type enable_app_insights: bool
        :param scoring_timeout_ms: A timeout to enforce for scoring calls to this Webservice. Defaults to 60000
        :type scoring_timeout_ms: int
        :param replica_max_concurrent_requests: The number of maximum concurrent requests per node to allow for this
            Webservice. Defaults to 1
        :type replica_max_concurrent_requests: int
        :param max_request_wait_time: The maximum amount of time a request will stay in the queue (in milliseconds)
            before returning a 503 error. Defaults to 500
        :type max_request_wait_time: int
        :param num_replicas: The number of containers to allocate for this Webservice. No default, if this parameter
            is not set then the autoscaler is enabled by default.
        :type num_replicas: int
        :param primary_key: A primary auth key to use for this Webservice
        :type primary_key: str
        :param secondary_key: A secondary auth key to use for this Webservice
        :type secondary_key: str
        :param tags: Dictionary of key value tags to give this Webservice
        :type tags: dict[str, str]
        :param properties: Dictionary of key value properties to give this Webservice. These properties cannot
            be changed after deployment, however new key value pairs can be added
        :type properties: dict[str, str]
        :param description: A description to give this Webservice
        :type description: str
        :param gpu_cores: The number of gpu cores to allocate for this Webservice. Default is 1
        :type gpu_cores: int
        :param period_seconds: How often (in seconds) to perform the liveness probe. Default to 10 seconds.
            Minimum value is 1.
        :type period_seconds: int
        :param initial_delay_seconds: Number of seconds after the container has started before liveness probes are
            initiated. Defaults to 310
        :type initial_delay_seconds: int
        :param timeout_seconds: Number of seconds after which the liveness probe times out. Defaults to 2 second.
            Minimum value is 1
        :type timeout_seconds: int
        :param success_threshold: Minimum consecutive successes for the liveness probe to be considered successful
            after having failed. Defaults to 1. Minimum value is 1.
        :type success_threshold: int
        :return: A configuration object to use when
        :param failure_threshold: When a Pod starts and the liveness probe fails, Kubernetes will try failureThreshold
            times before giving up. Defaults to 3. Minimum value is 1.
        :type failure_threshold: int deploying a Webservice object
        :param namespace: The Kubernetes namespace in which to deploy this Webservice: up to 63 lowercase alphanumeric
            ('a'-'z', '0'-'9') and hyphen ('-') characters. The first and last characters cannot be hyphens.
        :type namespace: str
        :rtype: AksServiceDeploymentConfiguration
        :raises: WebserviceException
        """
        config = AksServiceDeploymentConfiguration(autoscale_enabled, autoscale_min_replicas, autoscale_max_replicas,
                                                   autoscale_refresh_seconds, autoscale_target_utilization,
                                                   collect_model_data, auth_enabled, cpu_cores, memory_gb,
                                                   enable_app_insights, scoring_timeout_ms,
                                                   replica_max_concurrent_requests, max_request_wait_time,
                                                   num_replicas, primary_key, secondary_key, tags, properties,
                                                   description, gpu_cores, period_seconds, initial_delay_seconds,
                                                   timeout_seconds, success_threshold, failure_threshold, namespace)
        return config

    @staticmethod
    def _deploy(workspace, name, image, deployment_config, deployment_target):
        """Deploy the Webservice.

        :param workspace:
        :type workspace: azureml.core.workspace.Workspace
        :param name:
        :type name: str
        :param image:
        :type image: azureml.core.image.Image
        :param deployment_config:
        :type deployment_config: AksServiceDeploymentConfiguration | None
        :param deployment_target:
        :type deployment_target: azureml.core.compute.AksCompute
        :return:
        :rtype: AksWebservice
        """
        if not deployment_target:
            raise WebserviceException("Must have a deployment target for an AKS web service.", logger=module_logger)
        if not deployment_config:
            deployment_config = AksWebservice.deploy_configuration()
        elif not isinstance(deployment_config, AksServiceDeploymentConfiguration):
            raise WebserviceException('Error, provided deployment configuration must be of type '
                                      'AksServiceDeploymentConfiguration in order to deploy an AKS service.',
                                      logger=module_logger)
        deployment_config.validate_image(image)
        create_payload = AksWebservice._build_create_payload(name, image, deployment_target, deployment_config)
        return Webservice._deploy_webservice(workspace, name, create_payload, AksWebservice)

    @staticmethod
    def _build_create_payload(name, image, target, config):
        """Construct the payload used to create this Webservice.

        :param name:
        :type name: str
        :param image:
        :type image: azureml.core.image.Image
        :param target:
        :type target: azureml.core.compute.AksCompute
        :param config:
        :type config: azureml.core.compute.AksServiceDeploymentConfiguration
        :return:
        :rtype: dict
        """
        import copy
        from azureml._model_management._util import aks_service_payload_template
        json_payload = copy.deepcopy(aks_service_payload_template)
        json_payload['name'] = name
        json_payload['computeType'] = 'AKS'
        json_payload['computeName'] = target.name
        json_payload['imageId'] = image.id

        properties = config.properties or {}
        properties.update(global_tracking_info_registry.gather_all())
        json_payload['properties'] = properties

        if config.description:
            json_payload['description'] = config.description
        else:
            del (json_payload['description'])
        if config.tags:
            json_payload['kvTags'] = config.tags
        if config.num_replicas:
            json_payload['numReplicas'] = config.num_replicas
        else:
            del (json_payload['numReplicas'])
        if config.collect_model_data is None:
            del (json_payload['dataCollection'])
        else:
            json_payload['dataCollection']['storageEnabled'] = config.collect_model_data
        if config.enable_app_insights is None:
            del (json_payload['appInsightsEnabled'])
        else:
            json_payload['appInsightsEnabled'] = config.enable_app_insights
        if not config.autoscale_enabled:
            del (json_payload['autoScaler'])
        else:
            json_payload['autoScaler']['autoscaleEnabled'] = config.autoscale_enabled
            json_payload['autoScaler']['minReplicas'] = config.autoscale_min_replicas
            json_payload['autoScaler']['maxReplicas'] = config.autoscale_max_replicas
            json_payload['autoScaler']['targetUtilization'] = config.autoscale_target_utilization
            json_payload['autoScaler']['refreshPeriodInSeconds'] = config.autoscale_refresh_seconds
            if 'numReplicas' in json_payload:
                del (json_payload['numReplicas'])
        if config.auth_enabled is None:
            del (json_payload['authEnabled'])
        else:
            json_payload['authEnabled'] = config.auth_enabled
        if config.cpu_cores or config.memory_gb or config.gpu_cores:
            if config.cpu_cores:
                json_payload['containerResourceRequirements']['cpu'] = config.cpu_cores
            else:
                del (json_payload['containerResourceRequirements']['cpu'])
            if config.memory_gb:
                json_payload['containerResourceRequirements']['memoryInGB'] = config.memory_gb
            else:
                del (json_payload['containerResourceRequirements']['memoryInGB'])
            if config.gpu_cores:
                json_payload['containerResourceRequirements']['gpu'] = config.gpu_cores
            else:
                del (json_payload['containerResourceRequirements']['gpu'])
        else:
            del (json_payload['containerResourceRequirements'])

        if config.period_seconds or config.initial_delay_seconds or config.timeout_seconds \
                or config.failure_threshold or config.success_threshold:
            if config.period_seconds:
                json_payload['livenessProbeRequirements']['periodSeconds'] = config.period_seconds
            else:
                del (json_payload['livenessProbeRequirements']['periodSeconds'])
            if config.initial_delay_seconds:
                json_payload['livenessProbeRequirements']['initialDelaySeconds'] = config.initial_delay_seconds
            else:
                del (json_payload['livenessProbeRequirements']['initialDelaySeconds'])
            if config.timeout_seconds:
                json_payload['livenessProbeRequirements']['timeoutSeconds'] = config.timeout_seconds
            else:
                del (json_payload['livenessProbeRequirements']['timeoutSeconds'])
            if config.failure_threshold:
                json_payload['livenessProbeRequirements']['failureThreshold'] = config.failure_threshold
            else:
                del (json_payload['livenessProbeRequirements']['failureThreshold'])
            if config.success_threshold:
                json_payload['livenessProbeRequirements']['successThreshold'] = config.success_threshold
            else:
                del (json_payload['livenessProbeRequirements']['successThreshold'])
        else:
            del (json_payload['livenessProbeRequirements'])

        json_payload['maxConcurrentRequestsPerContainer'] = config.replica_max_concurrent_requests
        if config.max_request_wait_time:
            json_payload['maxQueueWaitMs'] = config.max_request_wait_time
        else:
            del (json_payload['maxQueueWaitMs'])
        if config.namespace:
            json_payload['namespace'] = config.namespace
        else:
            del (json_payload['namespace'])
        if config.primary_key:
            json_payload['keys']['primaryKey'] = config.primary_key
            json_payload['keys']['secondaryKey'] = config.secondary_key
        else:
            del (json_payload['keys'])
        if config.scoring_timeout_ms:
            json_payload['scoringTimeoutMs'] = config.scoring_timeout_ms
        else:
            del (json_payload['scoringTimeoutMs'])

        return json_payload

    def run(self, input_data):
        """Call this Webservice with the provided input.

        :param input_data: The input to call the Webservice with
        :type input_data: varies
        :return: The result of calling the Webservice
        :rtype: dict
        :raises: WebserviceException
        """
        if not self.scoring_uri:
            raise WebserviceException('Error attempting to call webservice, scoring_uri unavailable. '
                                      'This could be due to a failed deployment, or the service is not ready yet.\n'
                                      'Current State: {}\n'
                                      'Errors: {}'.format(self.state, self.error), logger=module_logger)

        resp = ClientBase._execute_func(self._webservice_session.post, self.scoring_uri, data=input_data)

        if resp.status_code == 401:
            if self.auth_enabled:
                service_keys = self.get_keys()
                self._session.headers.update({'Authorization': 'Bearer ' + service_keys[0]})

                resp = ClientBase._execute_func(self._webservice_session.post, self.scoring_uri, data=input_data)

        if resp.status_code == 200:
            return resp.json()
        else:
            raise WebserviceException('Received bad response from service:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content),
                                      logger=module_logger)

    def update(self, image=None, autoscale_enabled=None, autoscale_min_replicas=None, autoscale_max_replicas=None,
               autoscale_refresh_seconds=None, autoscale_target_utilization=None, collect_model_data=None,
               auth_enabled=None, cpu_cores=None, memory_gb=None, enable_app_insights=None, scoring_timeout_ms=None,
               replica_max_concurrent_requests=None, max_request_wait_time=None, num_replicas=None, tags=None,
               properties=None, description=None, models=None, inference_config=None, gpu_cores=None,
               period_seconds=None, initial_delay_seconds=None, timeout_seconds=None, success_threshold=None,
               failure_threshold=None, namespace=None):
        """Update the Webservice with provided properties.

        Values left as None will remain unchanged in this Webservice.

        :param image: A new Image to deploy to the Webservice
        :type image: azureml.core.image.image.Image
        :param autoscale_enabled: Enable or disable autoscaling of this Webservice
        :type autoscale_enabled: bool
        :param autoscale_min_replicas: The minimum number of containers to use when autoscaling this Webservice
        :type autoscale_min_replicas: int
        :param autoscale_max_replicas: The maximum number of containers to use when autoscaling this Webservice
        :type autoscale_max_replicas: int
        :param autoscale_refresh_seconds: How often the autoscaler should attempt to scale this Webservice
        :type autoscale_refresh_seconds: int
        :param autoscale_target_utilization: The target utilization (in percent out of 100) the autoscaler should
            attempt to maintain for this Webservice
        :type autoscale_target_utilization: int
        :param collect_model_data: Enable or disable model data collection for this Webservice
        :type collect_model_data: bool
        :param auth_enabled: Whether or not to enable auth for this Webservice
        :type auth_enabled: bool
        :param cpu_cores: The number of cpu cores to allocate for this Webservice. Can be a decimal
        :type cpu_cores: float
        :param memory_gb: The amount of memory (in GB) to allocate for this Webservice. Can be a decimal
        :type memory_gb: float
        :param enable_app_insights: Whether or not to enable Application Insights logging for this Webservice
        :type enable_app_insights: bool
        :param scoring_timeout_ms: A timeout to enforce for scoring calls to this Webservice
        :type scoring_timeout_ms: int
        :param replica_max_concurrent_requests: The number of maximum concurrent requests per node to allow for this
            Webservice
        :type replica_max_concurrent_requests: int
        :param max_request_wait_time: The maximum amount of time a request will stay in the queue (in milliseconds)
            before returning a 503 error
        :type max_request_wait_time: int
        :param num_replicas: The number of containers to allocate for this Webservice
        :type num_replicas: int
        :param tags: Dictionary of key value tags to give this Webservice. Will replace existing tags.
        :type tags: dict[str, str]
        :param properties: Dictionary of key value properties to add to existing properties dictionary
        :type properties: dict[str, str]
        :param description: A description to give this Webservice
        :type description: str
        :param models: A list of Model objects to package with the updated service
        :type models: :class:`list[azureml.core.model.Model]`
        :param inference_config: An InferenceConfig object used to provide the required model deployment properties.
        :type inference_config: azureml.core.model.InferenceConfig
        :param gpu_cores: The number of gpu cores to allocate for this Webservice
        :type gpu_cores: int
        :param period_seconds: How often (in seconds) to perform the liveness probe. Default to 10 seconds.
            Minimum value is 1.
        :type period_seconds: int
        :param initial_delay_seconds: Number of seconds after the container has started before liveness probes are
            initiated.
        :type initial_delay_seconds: int
        :param timeout_seconds: Number of seconds after which the liveness probe times out. Defaults to 1 second.
            Minimum value is 1.
        :type timeout_seconds: int
        :param success_threshold: Minimum consecutive successes for the liveness probe to be considered successful
            after having failed. Defaults to 1. Minimum value is 1.
        :type success_threshold: int
        :param failure_threshold: When a Pod starts and the liveness probe fails, Kubernetes will try failureThreshold
            times before giving up. Defaults to 3. Minimum value is 1.
        :type failure_threshold: int
        :param namespace: The Kubernetes namespace in which to deploy this Webservice: up to 63 lowercase alphanumeric
            ('a'-'z', '0'-'9') and hyphen ('-') characters. The first and last characters cannot be hyphens.
        :type namespace: str
        :raises: WebserviceException
        """
        if not image and autoscale_enabled is None and not autoscale_min_replicas and not autoscale_max_replicas \
                and not autoscale_refresh_seconds and not autoscale_target_utilization and collect_model_data is None \
                and auth_enabled is None and not cpu_cores and not memory_gb and not gpu_cores \
                and enable_app_insights is None and not scoring_timeout_ms and not replica_max_concurrent_requests \
                and not max_request_wait_time and not num_replicas and tags is None and properties is None \
                and not description and not period_seconds and not initial_delay_seconds and not timeout_seconds \
                and models is None and inference_config is None and not failure_threshold and not success_threshold \
                and not namespace:
            raise WebserviceException('No parameters provided to update.', logger=module_logger)

        headers = {'Content-Type': 'application/json-patch+json'}
        headers.update(self._auth.get_authentication_header())
        params = {'api-version': MMS_WORKSPACE_API_VERSION}

        self._validate_update(image, autoscale_enabled, autoscale_min_replicas, autoscale_max_replicas,
                              autoscale_refresh_seconds, autoscale_target_utilization, collect_model_data, cpu_cores,
                              memory_gb, enable_app_insights, scoring_timeout_ms, replica_max_concurrent_requests,
                              max_request_wait_time, num_replicas, tags, properties, description, models,
                              inference_config, gpu_cores, period_seconds, initial_delay_seconds, timeout_seconds,
                              success_threshold, failure_threshold, namespace)

        if models or inference_config:
            model_objects = self.image.models
            if models:
                model_objects = models
            image_name = "{}-{}".format(self.name, str(uuid.uuid4())[:4])
            image = Image.create(self.workspace, image_name, model_objects, inference_config)
            image.wait_for_creation(True)
            if image.creation_state != 'Succeeded':
                raise WebserviceException('Error occurred creating model package {} for service update. More '
                                          'information can be found here: {}, generated DockerFile can be '
                                          'found here: {}'.format(image.id,
                                                                  image.image_build_log_uri,
                                                                  image.generated_dockerfile_uri),
                                          logger=module_logger)

        properties = properties or {}
        properties.update(global_tracking_info_registry.gather_all())

        patch_list = []
        if image:
            patch_list.append({'op': 'replace', 'path': '/imageId', 'value': image.id})
        if autoscale_enabled is not None:
            patch_list.append({'op': 'replace', 'path': '/autoScaler/autoscaleEnabled', 'value': autoscale_enabled})
        if autoscale_min_replicas:
            patch_list.append({'op': 'replace', 'path': '/autoScaler/minReplicas', 'value': autoscale_min_replicas})
        if autoscale_max_replicas:
            patch_list.append({'op': 'replace', 'path': '/autoScaler/maxReplicas', 'value': autoscale_max_replicas})
        if autoscale_refresh_seconds:
            patch_list.append({'op': 'replace', 'path': '/autoScaler/refreshPeriodInSeconds',
                               'value': autoscale_refresh_seconds})
        if autoscale_target_utilization:
            patch_list.append({'op': 'replace', 'path': '/autoScaler/targetUtilization',
                               'value': autoscale_target_utilization})
        if collect_model_data is not None:
            patch_list.append({'op': 'replace', 'path': '/dataCollection/storageEnabled', 'value': collect_model_data})
        if auth_enabled is not None:
            patch_list.append({'op': 'replace', 'path': '/authEnabled', 'value': auth_enabled})
        if cpu_cores:
            patch_list.append({'op': 'replace', 'path': '/containerResourceRequirements/cpu', 'value': cpu_cores})
        if memory_gb:
            patch_list.append({'op': 'replace', 'path': '/containerResourceRequirements/memoryInGB',
                               'value': memory_gb})
        if gpu_cores:
            patch_list.append({'op': 'replace', 'path': '/containerResourceRequirements/gpu', 'value': gpu_cores})
        if enable_app_insights is not None:
            patch_list.append({'op': 'replace', 'path': '/appInsightsEnabled', 'value': enable_app_insights})
        if scoring_timeout_ms:
            patch_list.append({'op': 'replace', 'path': '/scoringTimeoutMs', 'value': scoring_timeout_ms})
        if replica_max_concurrent_requests:
            patch_list.append({'op': 'replace', 'path': '/maxConcurrentRequestsPerContainer',
                               'value': replica_max_concurrent_requests})
        if max_request_wait_time:
            patch_list.append({'op': 'replace', 'path': '/maxQueueWaitMs',
                               'value': max_request_wait_time})
        if num_replicas:
            patch_list.append({'op': 'replace', 'path': '/numReplicas', 'value': num_replicas})
        if period_seconds:
            patch_list.append({'op': 'replace', 'path': '/livenessProbeRequirements/periodSeconds',
                               'value': period_seconds})
        if initial_delay_seconds:
            patch_list.append({'op': 'replace', 'path': '/livenessProbeRequirements/initialDelaySeconds',
                               'value': initial_delay_seconds})
        if timeout_seconds:
            patch_list.append({'op': 'replace', 'path': '/livenessProbeRequirements/timeoutSeconds',
                               'value': timeout_seconds})
        if success_threshold:
            patch_list.append({'op': 'replace', 'path': '/livenessProbeRequirements/successThreshold',
                               'value': success_threshold})
        if failure_threshold:
            patch_list.append({'op': 'replace', 'path': '/livenessProbeRequirements/failureThreshold',
                               'value': failure_threshold})
        if namespace:
            patch_list.append({'op': 'replace', 'path': '/namespace', 'value': namespace})
        if tags is not None:
            patch_list.append({'op': 'replace', 'path': '/kvTags', 'value': tags})
        if properties is not None:
            for key in properties:
                patch_list.append({'op': 'add', 'path': '/properties/{}'.format(key), 'value': properties[key]})
        if description:
            patch_list.append({'op': 'replace', 'path': '/description', 'value': description})

        resp = ClientBase._execute_func(get_requests_session().patch, self._mms_endpoint, headers=headers,
                                        params=params, json=patch_list)

        if resp.status_code == 200:
            self.update_deployment_state()
        elif resp.status_code == 202:
            if 'Operation-Location' in resp.headers:
                operation_location = resp.headers['Operation-Location']
            else:
                raise WebserviceException('Missing response header key: Operation-Location', logger=module_logger)
            create_operation_status_id = operation_location.split('/')[-1]
            base_url = '/'.join(self._mms_endpoint.split('/')[:-2])
            operation_url = base_url + '/operations/{}'.format(create_operation_status_id)
            self._operation_endpoint = operation_url
            self.update_deployment_state()
        else:
            raise WebserviceException('Received bad response from Model Management Service:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content),
                                      logger=module_logger)

    def _validate_update(self, image, autoscale_enabled, autoscale_min_replicas, autoscale_max_replicas,
                         autoscale_refresh_seconds, autoscale_target_utilization, collect_model_data, cpu_cores,
                         memory_gb, enable_app_insights, scoring_timeout_ms, replica_max_concurrent_requests,
                         max_request_wait_time, num_replicas, tags, properties, description, models,
                         inference_config, gpu_cores, period_seconds, initial_delay_seconds, timeout_seconds,
                         success_threshold, failure_threshold, namespace):
        """Validate the values provided to update the webservice.

        :param image:
        :type image: azureml.core.image.image.Image
        :param autoscale_enabled:
        :type autoscale_enabled: bool
        :param autoscale_min_replicas:
        :type autoscale_min_replicas: int
        :param autoscale_max_replicas:
        :type autoscale_max_replicas: int
        :param autoscale_refresh_seconds:
        :type autoscale_refresh_seconds: int
        :param autoscale_target_utilization:
        :type autoscale_target_utilization: int
        :param collect_model_data:
        :type collect_model_data: bool
        :param cpu_cores:
        :type cpu_cores: float
        :param memory_gb:
        :type memory_gb: float
        :param enable_app_insights:
        :type enable_app_insights: bool
        :param scoring_timeout_ms:
        :type scoring_timeout_ms: int
        :param replica_max_concurrent_requests:
        :type replica_max_concurrent_requests: int
        :param max_request_wait_time: The maximum amount of time a request will stay in the queue (in milliseconds)
            before returning a 503 error
        :type max_request_wait_time: int
        :param num_replicas:
        :type num_replicas: int
        :param tags:
        :type tags: dict[str, str]
        :param properties:
        :type properties: dict[str, str]
        :param description:
        :type description: str
        :param models: A list of Model objects to package with this image. Can be an empty list
        :type models: :class:`list[azureml.core.model.Model]`
        :param inference_config: An InferenceConfig object used to determine required model properties.
        :type inference_config: azureml.core.model.InferenceConfig
        :param: gpu_cores
        :type: int
        :param period_seconds:
        :type period_seconds: int
        :param initial_delay_seconds:
        :type initial_delay_seconds: int
        :param timeout_seconds:
        :type timeout_seconds: int
        :param success_threshold:
        :type success_threshold: int
        :param failure_threshold:
        :type failure_threshold: int
        :param namespace:
        :type namespace: str
        """
        error = ""
        if cpu_cores and cpu_cores <= 0:
            error += 'Error, cpu_cores must be greater than zero.\n'
        if memory_gb and memory_gb <= 0:
            error += 'Error, memory_gb must be greater than zero.\n'
        if gpu_cores and gpu_cores <= 0:
            error += 'Error, gpu_cores must be greater than zero.\n'
        if scoring_timeout_ms and scoring_timeout_ms <= 0:
            error += 'Error, scoring_timeout_ms must be greater than zero.\n'
        if replica_max_concurrent_requests and replica_max_concurrent_requests <= 0:
            error += 'Error, replica_max_concurrent_requests must be greater than zero.\n'
        if max_request_wait_time and max_request_wait_time <= 0:
            error += 'Error, max_request_wait_time must be greater than zero.\n'
        if num_replicas and num_replicas <= 0:
            error += 'Error, num_replicas must be greater than zero.\n'
        if period_seconds and period_seconds <= 0:
            error += 'Error, period_seconds must be greater than zero.\n'
        if timeout_seconds and timeout_seconds <= 0:
            error += 'Error, timeout_seconds must be greater than zero.\n'
        if initial_delay_seconds and initial_delay_seconds <= 0:
            error += 'Error, initial_delay_seconds must be greater than zero.\n'
        if success_threshold and success_threshold <= 0:
            error += 'Error, success_threshold must be greater than zero.\n'
        if failure_threshold and failure_threshold <= 0:
            error += 'Error, failure_threshold must be greater than zero.\n'
        if namespace and not re.match(NAMESPACE_REGEX, namespace):
            error += 'Error, namespace must be a valid Kubernetes namespace. ' \
                     'Regex for validation is ' + NAMESPACE_REGEX + '\n'
        if autoscale_enabled:
            if num_replicas:
                error += 'Error, autoscale enabled and num_replicas provided.\n'
            if autoscale_min_replicas and autoscale_min_replicas <= 0:
                error += 'Error, autoscale_min_replicas must be greater than zero.\n'
            if autoscale_max_replicas and autoscale_max_replicas <= 0:
                error += 'Error, autoscale_max_replicas must be greater than zero.\n'
            if autoscale_min_replicas and autoscale_max_replicas and \
                    autoscale_min_replicas > autoscale_max_replicas:
                error += 'Error, autoscale_min_replicas cannot be greater than autoscale_max_replicas.\n'
            if autoscale_refresh_seconds and autoscale_refresh_seconds <= 0:
                error += 'Error, autoscale_refresh_seconds must be greater than zero.\n'
            if autoscale_target_utilization and autoscale_target_utilization <= 0:
                error += 'Error, autoscale_target_utilization must be greater than zero.\n'
        else:
            if autoscale_enabled is False and not num_replicas:
                error += 'Error, autoscale disabled but num_replicas not provided.\n'
            if autoscale_min_replicas:
                error += 'Error, autoscale_min_replicas provided without enabling autoscaling.\n'
            if autoscale_max_replicas:
                error += 'Error, autoscale_max_replicas provided without enabling autoscaling.\n'
            if autoscale_refresh_seconds:
                error += 'Error, autoscale_refresh_seconds provided without enabling autoscaling.\n'
            if autoscale_target_utilization:
                error += 'Error, autoscale_target_utilization provided without enabling autoscaling.\n'
        if inference_config is None and models:
            error += 'Error, both "models" and "inference_config" inputs must be provided in order ' \
                     'to update any of the parameters in inference_config.\n'

        if error:
            raise WebserviceException(error, logger=module_logger)

    def add_tags(self, tags):
        """Add key value pairs to this Webservice's tags dictionary.

        :param tags: The dictionary of tags to add
        :type tags: dict[str, str]
        :raises: WebserviceException
        """
        updated_tags = self._add_tags(tags)
        self.tags = updated_tags
        self.update(tags=updated_tags)

        print('Image tag add operation complete.')

    def remove_tags(self, tags):
        """Remove the specified keys from this Webservice's dictionary of tags.

        :param tags: The list of keys to remove
        :type tags: :class:`list[str]`
        """
        updated_tags = self._remove_tags(tags)
        self.tags = updated_tags
        self.update(tags=updated_tags)

        print('Image tag remove operation complete.')

    def add_properties(self, properties):
        """Add key value pairs to this Webservice's properties dictionary.

        :param properties: The dictionary of properties to add
        :type properties: dict[str, str]
        """
        updated_properties = self._add_properties(properties)
        self.properties = updated_properties
        self.update(tags=updated_properties)

        print('Image tag add operation complete.')

    def serialize(self):
        """Convert this Webservice into a json serialized dictionary.

        :return: The json representation of this Webservice
        :rtype: dict
        """
        properties = super(AksWebservice, self).serialize()
        autoscaler = self.autoscaler.serialize() if self.autoscaler else None
        container_resource_requirements = self.container_resource_requirements.serialize() \
            if self.container_resource_requirements else None
        liveness_probe_requirements = self.liveness_probe_requirements.serialize() \
            if self.liveness_probe_requirements else None
        data_collection = self.data_collection.serialize() if self.data_collection else None
        image = self.image.serialize() if self.image else None
        aks_properties = {'appInsightsEnabled': self.enable_app_insights, 'authEnabled': self.auth_enabled,
                          'autoScaler': autoscaler, 'computeName': self.compute_name,
                          'containerResourceRequirements': container_resource_requirements,
                          'dataCollection': data_collection, 'imageId': self.image_id,
                          'imageDetails': image,
                          'maxConcurrentRequestsPerContainer': self.max_concurrent_requests_per_container,
                          'maxQueueWaitMs': self.max_request_wait_time,
                          'livenessProbeRequirements': liveness_probe_requirements,
                          'numReplicas': self.num_replicas, 'deploymentStatus': self.deployment_status,
                          'scoringTimeoutMs': self.scoring_timeout_ms, 'scoringUri': self.scoring_uri}
        properties.update(aks_properties)
        return properties


class AutoScaler(object):
    """Class containing details for the autoscaler for AKS Webservices."""

    _expected_payload_keys = ['autoscaleEnabled', 'maxReplicas', 'minReplicas', 'refreshPeriodInSeconds',
                              'targetUtilization']

    def __init__(self, autoscale_enabled, max_replicas, min_replicas, refresh_period_seconds, target_utilization):
        """Initialize the AKS AutoScaler.

        :param autoscale_enabled: Whether the autoscaler is enabled or disabled
        :type autoscale_enabled: bool
        :param max_replicas: The maximum number of containers for the Autoscaler to use
        :type max_replicas: int
        :param min_replicas: The minimum number of containers for the Autoscaler to use
        :type min_replicas: int
        :param refresh_period_seconds: How often the autoscaler should attempt to scale the Webservice
        :type refresh_period_seconds: int
        :param target_utilization: The target utilization (in percent out of 100) the autoscaler should
            attempt to maintain for the Webservice
        :type target_utilization: int
        """
        self.autoscale_enabled = autoscale_enabled
        self.max_replicas = max_replicas
        self.min_replicas = min_replicas
        self.refresh_period_seconds = refresh_period_seconds
        self.target_utilization = target_utilization

    def serialize(self):
        """Convert this AutoScaler into a json serialized dictionary.

        :return: The json representation of this AutoScaler
        :rtype: dict
        """
        return {'autoscaleEnabled': self.autoscale_enabled, 'minReplicas': self.min_replicas,
                'maxReplicas': self.max_replicas, 'refreshPeriodInSeconds': self.refresh_period_seconds,
                'targetUtilization': self.target_utilization}

    @staticmethod
    def deserialize(payload_obj):
        """Convert a json object into a AutoScaler object.

        :param payload_obj: A json object to convert to a AutoScaler object
        :type payload_obj: dict
        :return: The AutoScaler representation of the provided json object
        :rtype: AutoScaler
        """
        for payload_key in AutoScaler._expected_payload_keys:
            if payload_key not in payload_obj:
                raise WebserviceException('Invalid webservice payload, missing {} for autoScaler:\n'
                                          '{}'.format(payload_key, payload_obj), logger=module_logger)

        return AutoScaler(payload_obj['autoscaleEnabled'], payload_obj['maxReplicas'], payload_obj['minReplicas'],
                          payload_obj['refreshPeriodInSeconds'], payload_obj['targetUtilization'])


class ContainerResourceRequirements(object):
    """Class containing details for the resource requirements for each container used by the Webservice."""

    _expected_payload_keys = ['cpu', 'memoryInGB', 'gpu']

    def __init__(self, cpu, memory_in_gb, gpu=None):
        """Initialize the container resource requirements.

        :param cpu: The number of cpu cores to allocate for this Webservice. Can be a decimal
        :type cpu: float
        :param memory_in_gb: The amount of memory (in GB) to allocate for this Webservice. Can be a decimal
        :type memory_in_gb: float
        """
        self.cpu = cpu
        self.memory_in_gb = memory_in_gb
        self.gpu = gpu

    def serialize(self):
        """Convert this ContainerResourceRequirements into a json serialized dictionary.

        :return: The json representation of this ContainerResourceRequirements
        :rtype: dict
        """
        return {'cpu': self.cpu, 'memoryInGB': self.memory_in_gb, 'gpu': self.gpu}

    @staticmethod
    def deserialize(payload_obj):
        """Convert a json object into a ContainerResourceRequirements object.

        :param payload_obj: A json object to convert to a ContainerResourceRequirements object
        :type payload_obj: dict
        :return: The ContainerResourceRequirements representation of the provided json object
        :rtype: azureml.core.webservice.aks.ContainerResourceRequirements
        """
        for payload_key in ContainerResourceRequirements._expected_payload_keys:
            if payload_key not in payload_obj:
                raise WebserviceException('Invalid webservice payload, missing {} for ContainerResourceRequirements:\n'
                                          '{}'.format(payload_key, payload_obj), logger=module_logger)

        return ContainerResourceRequirements(payload_obj['cpu'], payload_obj['memoryInGB'], payload_obj['gpu'])


class LivenessProbeRequirements(object):
    """Class containing details for the liveness probe time requirements for deployments of the webservice."""

    _expected_payload_keys = ['periodSeconds', 'initialDelaySeconds', 'timeoutSeconds',
                              'failureThreshold', 'successThreshold']

    def __init__(self, period_seconds, initial_delay_seconds, timeout_seconds, success_threshold, failure_threshold):
        """Initialize the container resource requirements.

        :param period_seconds: How often (in seconds) to perform the liveness probe. Default to 10 seconds.
            Minimum value is 1.
        :type period_seconds: int
        :param initial_delay_seconds: Number of seconds after the container has started before liveness probes are
            initiated.
        :type initial_delay_seconds: int
        :param timeout_seconds: Number of seconds after which the liveness probe times out. Defaults to 1 second.
            Minimum value is 1.
        :type timeout_seconds: int
        :param failure_threshold: When a Pod starts and the liveness probe fails, Kubernetes will try failureThreshold
            times before giving up. Defaults to 3. Minimum value is 1.
        :type failure_threshold: int
        :param success_threshold: Minimum consecutive successes for the liveness probe to be considered successful
            after having failed. Defaults to 1. Minimum value is 1.
        :type success_threshold: int
        """
        self.period_seconds = period_seconds
        self.timeout_seconds = timeout_seconds
        self.initial_delay_seconds = initial_delay_seconds
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold

    def serialize(self):
        """Convert this LivenessProbeRequirements into a json serialized dictionary.

        :return: The json representation of this LivenessProbeRequirements
        :rtype: dict
        """
        return {'periodSeconds': self.period_seconds, 'initialDelaySeconds': self.initial_delay_seconds,
                'timeoutSeconds': self.timeout_seconds, 'successThreshold': self.success_threshold,
                'failureThreshold': self.failure_threshold}

    @staticmethod
    def deserialize(payload_obj):
        """Convert a json object into a LivenessProbeRequirements object.

        :param payload_obj: A json object to convert to a LivenessProbeRequirements object
        :type payload_obj: dict
        :return: The LivenessProbeRequirements representation of the provided json object
        :rtype: azureml.core.webservice.aks.LivenessProbeRequirements
        """
        if payload_obj is None:
            return LivenessProbeRequirements(period_seconds=10, initial_delay_seconds=310, timeout_seconds=1,
                                             success_threshold=1, failure_threshold=3)
        for payload_key in LivenessProbeRequirements._expected_payload_keys:
            if payload_key not in payload_obj:
                raise WebserviceException('Invalid webservice payload, missing {} for LivenessProbeRequirements:\n'
                                          '{}'.format(payload_key, payload_obj), logger=module_logger)

        return LivenessProbeRequirements(payload_obj['periodSeconds'], payload_obj['initialDelaySeconds'],
                                         payload_obj['timeoutSeconds'], payload_obj['successThreshold'],
                                         payload_obj['failureThreshold'])


class DataCollection(object):
    """Class for managing data collection for an AKS Webservice."""

    _expected_payload_keys = ['eventHubEnabled', 'storageEnabled']

    def __init__(self, event_hub_enabled, storage_enabled):
        """Intialize the DataCollection object.

        :param event_hub_enabled: Whether or not event hub is enabled for the Webservice
        :type event_hub_enabled: bool
        :param storage_enabled: Whether or not data collection storage is enabled for the Webservice
        :type storage_enabled: bool
        """
        self.event_hub_enabled = event_hub_enabled
        self.storage_enabled = storage_enabled

    def serialize(self):
        """Convert this DataCollection into a json serialized dictionary.

        :return: The json representation of this DataCollection
        :rtype: dict
        """
        return {'eventHubEnabled': self.event_hub_enabled, 'storageEnabled': self.storage_enabled}

    @staticmethod
    def deserialize(payload_obj):
        """Convert a json object into a DataCollection object.

        :param payload_obj: A json object to convert to a DataCollection object
        :type payload_obj: dict
        :return: The DataCollection representation of the provided json object
        :rtype: DataCollection
        """
        for payload_key in DataCollection._expected_payload_keys:
            if payload_key not in payload_obj:
                raise WebserviceException('Invalid webservice payload, missing {} for DataCollection:\n'
                                          '{}'.format(payload_key, payload_obj), logger=module_logger)

        return DataCollection(payload_obj['eventHubEnabled'], payload_obj['storageEnabled'])


class AksServiceDeploymentConfiguration(WebserviceDeploymentConfiguration):
    """Service deployment configuration object for services deployed on AKS compute.

    :param autoscale_enabled: Whether or not to enable autoscaling for this Webservice.
        Defaults to True if num_replicas is None
    :type autoscale_enabled: bool
    :param autoscale_min_replicas: The minimum number of containers to use when autoscaling this Webservice.
        Defaults to 1
    :type autoscale_min_replicas: int
    :param autoscale_max_replicas: The maximum number of containers to use when autoscaling this Webservice.
        Defaults to 10
    :type autoscale_max_replicas: int
    :param autoscale_refresh_seconds: How often the autoscaler should attempt to scale this Webservice.
        Defaults to 1
    :type autoscale_refresh_seconds: int
    :param autoscale_target_utilization: The target utilization (in percent out of 100) the autoscaler should
        attempt to maintain for this Webservice. Defaults to 70
    :type autoscale_target_utilization: int
    :param collect_model_data: Whether or not to enable model data collection for this Webservice.
        Defaults to False
    :type collect_model_data: bool
    :param auth_enabled: Whether or not to enable auth for this Webservice. Defaults to True
    :type auth_enabled: bool
    :param cpu_cores: The number of cpu cores to allocate for this Webservice. Can be a decimal. Defaults to 0.1
    :type cpu_cores: float
    :param memory_gb: The amount of memory (in GB) to allocate for this Webservice. Can be a decimal.
        Defaults to 0.5
    :type memory_gb: float
    :param enable_app_insights: Whether or not to enable Application Insights logging for this Webservice.
        Defaults to False
    :type enable_app_insights: bool
    :param scoring_timeout_ms: A timeout to enforce for scoring calls to this Webservice. Defaults to 60000
    :type scoring_timeout_ms: int
    :param replica_max_concurrent_requests: The number of maximum concurrent requests per node to allow for this
        Webservice. Defaults to 1
    :type replica_max_concurrent_requests: int
    :param max_request_wait_time: The maximum amount of time a request will stay in the queue (in milliseconds)
        before returning a 503 error. Defaults to 500
    :type max_request_wait_time: int
    :param num_replicas: The number of containers to allocate for this Webservice. No default, if this parameter
        is not set then the autoscaler is enabled by default.
    :type num_replicas: int
    :param primary_key: A primary auth key to use for this Webservice
    :type primary_key: str
    :param secondary_key: A secondary auth key to use for this Webservice
    :type secondary_key: str
    :param tags: Dictionary of key value tags to give this Webservice
    :type tags: dict[str, str]
    :param properties: Dictionary of key value properties to give this Webservice. These properties cannot
        be changed after deployment, however new key value pairs can be added
    :type properties: dict[str, str]
    :param description: A description to give this Webservice
    :type description: str
    :param gpu_cores: The number of gpu cores to allocate for this Webservice. Default is 1
    :type gpu_cores: int
    :param period_seconds: How often (in seconds) to perform the liveness probe. Default to 10 seconds.
        Minimum value is 1.
    :type period_seconds: int
    :param initial_delay_seconds: Number of seconds after the container has started before liveness probes are
        initiated. Defaults to 310
    :type initial_delay_seconds: int
    :param timeout_seconds: Number of seconds after which the liveness probe times out. Defaults to 2 second.
        Minimum value is 1
    :type timeout_seconds: int
    :param success_threshold: Minimum consecutive successes for the liveness probe to be considered successful
        after having failed. Defaults to 1. Minimum value is 1.
    :type success_threshold: int
    :param failure_threshold: When a Pod starts and the liveness probe fails, Kubernetes will try failureThreshold
        times before giving up. Defaults to 3. Minimum value is 1.
    :type failure_threshold: int
    :param namespace: The Kubernetes namespace in which to deploy this Webservice: up to 63 lowercase alphanumeric
        ('a'-'z', '0'-'9') and hyphen ('-') characters. The first and last characters cannot be hyphens.
    :type namespace: str
    :return: A configuration object to use when deploying a Webservice object.
    """

    def __init__(self, autoscale_enabled, autoscale_min_replicas, autoscale_max_replicas, autoscale_refresh_seconds,
                 autoscale_target_utilization, collect_model_data, auth_enabled, cpu_cores, memory_gb,
                 enable_app_insights, scoring_timeout_ms, replica_max_concurrent_requests, max_request_wait_time,
                 num_replicas, primary_key, secondary_key, tags, properties, description, gpu_cores, period_seconds,
                 initial_delay_seconds, timeout_seconds, success_threshold, failure_threshold, namespace):
        """Initialize a configuration object for deploying to an AKS compute target.

        :param autoscale_enabled: Whether or not to enable autoscaling for this Webservice.
            Defaults to True if num_replicas is None
        :type autoscale_enabled: bool
        :param autoscale_min_replicas: The minimum number of containers to use when autoscaling this Webservice.
            Defaults to 1
        :type autoscale_min_replicas: int
        :param autoscale_max_replicas: The maximum number of containers to use when autoscaling this Webservice.
            Defaults to 10
        :type autoscale_max_replicas: int
        :param autoscale_refresh_seconds: How often the autoscaler should attempt to scale this Webservice.
            Defaults to 1
        :type autoscale_refresh_seconds: int
        :param autoscale_target_utilization: The target utilization (in percent out of 100) the autoscaler should
            attempt to maintain for this Webservice. Defaults to 70
        :type autoscale_target_utilization: int
        :param collect_model_data: Whether or not to enable model data collection for this Webservice.
            Defaults to False
        :type collect_model_data: bool
        :param auth_enabled: Whether or not to enable auth for this Webservice. Defaults to True
        :type auth_enabled: bool
        :param cpu_cores: The number of cpu cores to allocate for this Webservice. Can be a decimal. Defaults to 0.1
        :type cpu_cores: float
        :param memory_gb: The amount of memory (in GB) to allocate for this Webservice. Can be a decimal.
            Defaults to 0.5
        :type memory_gb: float
        :param enable_app_insights: Whether or not to enable Application Insights logging for this Webservice.
            Defaults to False
        :type enable_app_insights: bool
        :param scoring_timeout_ms: A timeout to enforce for scoring calls to this Webservice. Defaults to 60000
        :type scoring_timeout_ms: int
        :param replica_max_concurrent_requests: The number of maximum concurrent requests per node to allow for this
            Webservice. Defaults to 1
        :type replica_max_concurrent_requests: int
        :param max_request_wait_time: The maximum amount of time a request will stay in the queue (in milliseconds)
            before returning a 503 error. Defaults to 500
        :type max_request_wait_time: int
        :param num_replicas: The number of containers to allocate for this Webservice. No default, if this parameter
            is not set then the autoscaler is enabled by default.
        :type num_replicas: int
        :param primary_key: A primary auth key to use for this Webservice
        :type primary_key: str
        :param secondary_key: A secondary auth key to use for this Webservice
        :type secondary_key: str
        :param tags: Dictionary of key value tags to give this Webservice
        :type tags: dict[str, str]
        :param properties: Dictionary of key value properties to give this Webservice. These properties cannot
            be changed after deployment, however new key value pairs can be added
        :type properties: dict[str, str]
        :param description: A description to give this Webservice
        :type description: str
        :param gpu_cores: The number of gpu cores to allocate for this Webservice. Default is 1
        :type gpu_cores: int
        :param period_seconds: How often (in seconds) to perform the liveness probe. Default to 10 seconds.
            Minimum value is 1.
        :type period_seconds: int
        :param initial_delay_seconds: Number of seconds after the container has started before liveness probes are
            initiated. Defaults to 310
        :type initial_delay_seconds: int
        :param timeout_seconds: Number of seconds after which the liveness probe times out. Defaults to 2 second.
            Minimum value is 1
        :type timeout_seconds: int
        :param success_threshold: Minimum consecutive successes for the liveness probe to be considered successful
            after having failed. Defaults to 1. Minimum value is 1.
        :type success_threshold: int
        :param failure_threshold: When a Pod starts and the liveness probe fails, Kubernetes will try failureThreshold
            times before giving up. Defaults to 3. Minimum value is 1.
        :type failure_threshold: int
        :param namespace: The Kubernetes namespace in which to deploy this Webservice: up to 63 lowercase alphanumeric
            ('a'-'z', '0'-'9') and hyphen ('-') characters. The first and last characters cannot be hyphens.
        :type namespace: str
        :return: A configuration object to use when deploying a Webservice object.
        :raises: WebserviceException
        """
        super(AksServiceDeploymentConfiguration, self).__init__(AksWebservice)
        self.autoscale_enabled = autoscale_enabled
        self.autoscale_min_replicas = autoscale_min_replicas
        self.autoscale_max_replicas = autoscale_max_replicas
        self.autoscale_refresh_seconds = autoscale_refresh_seconds
        self.autoscale_target_utilization = autoscale_target_utilization
        self.collect_model_data = collect_model_data
        self.auth_enabled = auth_enabled
        self.cpu_cores = cpu_cores
        self.memory_gb = memory_gb
        self.gpu_cores = gpu_cores
        self.enable_app_insights = enable_app_insights
        self.scoring_timeout_ms = scoring_timeout_ms
        self.replica_max_concurrent_requests = replica_max_concurrent_requests
        self.max_request_wait_time = max_request_wait_time
        self.num_replicas = num_replicas
        self.primary_key = primary_key
        self.secondary_key = secondary_key
        self.period_seconds = period_seconds
        self.initial_delay_seconds = initial_delay_seconds
        self.timeout_seconds = timeout_seconds
        self.success_threshold = success_threshold
        self.failure_threshold = failure_threshold
        self.namespace = namespace
        self.tags = tags
        self.properties = properties
        self.description = description
        self.validate_configuration()

    def validate_configuration(self):
        """Check that the specified configuration values are valid.

        Will raise a WebserviceException if validation fails.

        :raises: WebserviceException
        """
        error = ""
        if self.cpu_cores and self.cpu_cores <= 0:
            error += 'Invalid configuration, cpu_cores must be greater than zero.\n'
        if self.memory_gb and self.memory_gb <= 0:
            error += 'Invalid configuration, memory_gb must be greater than zero.\n'
        if self.gpu_cores and self.gpu_cores <= 0:
            error += 'Invalid configuration, gpu_cores must be greater than zero.\n'
        if self.period_seconds and self.period_seconds <= 0:
            error += 'Invalid configuration, period_seconds must be greater than zero.\n'
        if self.initial_delay_seconds and self.initial_delay_seconds <= 0:
            error += 'Invalid configuration, initial_delay_seconds must be greater than zero.\n'
        if self.timeout_seconds and self.timeout_seconds <= 0:
            error += 'Invalid configuration, timeout_seconds must be greater than zero.\n'
        if self.success_threshold and self.success_threshold <= 0:
            error += 'Invalid configuration, success_threshold must be greater than zero.\n'
        if self.failure_threshold and self.failure_threshold <= 0:
            error += 'Invalid configuration, failure_threshold must be greater than zero.\n'
        if self.namespace and not re.match(NAMESPACE_REGEX, self.namespace):
            error += 'Invalid configuration, namespace must be a valid Kubernetes namespace. ' \
                     'Regex for validation is ' + NAMESPACE_REGEX + '\n'
        if self.scoring_timeout_ms and self.scoring_timeout_ms <= 0:
            error += 'Invalid configuration, scoring_timeout_ms must be greater than zero.\n'
        if self.replica_max_concurrent_requests and self.replica_max_concurrent_requests <= 0:
            error += 'Invalid configuration, replica_max_concurrent_requests must be greater than zero.\n'
        if self.max_request_wait_time and self.max_request_wait_time <= 0:
            error += 'Invalid configuration, max_request_wait_time must be greater than zero.\n'
        if self.num_replicas and self.num_replicas <= 0:
            error += 'Invalid configuration, num_replicas must be greater than zero.\n'
        if self.autoscale_enabled:
            if self.num_replicas:
                error += 'Invalid configuration, autoscale enabled and num_replicas provided.\n'
            if self.autoscale_min_replicas and self.autoscale_min_replicas <= 0:
                error += 'Invalid configuration, autoscale_min_replicas must be greater than zero.\n'
            if self.autoscale_max_replicas and self.autoscale_max_replicas <= 0:
                error += 'Invalid configuration, autoscale_max_replicas must be greater than zero.\n'
            if self.autoscale_min_replicas and self.autoscale_max_replicas and \
                    self.autoscale_min_replicas > self.autoscale_max_replicas:
                error += 'Invalid configuration, autoscale_min_replicas cannot be greater than ' \
                         'autoscale_max_replicas.\n'
            if self.autoscale_refresh_seconds and self.autoscale_refresh_seconds <= 0:
                error += 'Invalid configuration, autoscale_refresh_seconds must be greater than zero.\n'
            if self.autoscale_target_utilization and self.autoscale_target_utilization <= 0:
                error += 'Invalid configuration, autoscale_target_utilization must be greater than zero.\n'
        else:
            if self.autoscale_enabled is False and not self.num_replicas:
                error += 'Invalid configuration, autoscale disabled but num_replicas not provided.\n'
            if self.autoscale_min_replicas:
                error += 'Invalid configuration, autoscale_min_replicas provided without enabling autoscaling.\n'
            if self.autoscale_max_replicas:
                error += 'Invalid configuration, autoscale_max_replicas provided without enabling autoscaling.\n'
            if self.autoscale_refresh_seconds:
                error += 'Invalid configuration, autoscale_refresh_seconds provided without enabling autoscaling.\n'
            if self.autoscale_target_utilization:
                error += 'Invalid configuration, autoscale_target_utilization provided without enabling autoscaling.\n'

        if error:
            raise WebserviceException(error, logger=module_logger)
