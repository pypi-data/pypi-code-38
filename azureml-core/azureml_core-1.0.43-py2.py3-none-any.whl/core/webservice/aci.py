# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for managing Azure Container Instances Webservices in Azure Machine Learning service."""

import logging
import uuid
from azureml._base_sdk_common.tracking import global_tracking_info_registry
from azureml._model_management._constants import MMS_WORKSPACE_API_VERSION
from azureml._model_management._constants import MMS_SYNC_TIMEOUT_SECONDS
from azureml._model_management._constants import ACI_WEBSERVICE_TYPE
from azureml._model_management._constants import WEBSERVICE_SWAGGER_PATH
from azureml._model_management._util import get_requests_session
from azureml._restclient.clientbase import ClientBase
from azureml.core.image import Image
from azureml.core.webservice import Webservice
from azureml.core.webservice.webservice import WebserviceDeploymentConfiguration
from azureml.exceptions import WebserviceException

module_logger = logging.getLogger(__name__)


class AciWebservice(Webservice):
    """Class for Azure Container Instances Webservices."""

    _expected_payload_keys = Webservice._expected_payload_keys + \
        ['appInsightsEnabled', 'authEnabled', 'cname', 'containerResourceRequirements',
         'location', 'publicIp', 'scoringUri', 'sslCertificate', 'sslEnabled', 'sslKey']
    _webservice_type = ACI_WEBSERVICE_TYPE

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
        AciWebservice._validate_get_payload(obj_dict)

        # Initialize common Webservice attributes
        super(AciWebservice, self)._initialize(workspace, obj_dict)

        # Initialize expected ACI specific attributes
        self.enable_app_insights = obj_dict['appInsightsEnabled']
        self.cname = obj_dict['cname']
        self.container_resource_requirements = \
            ContainerResourceRequirements.deserialize(obj_dict['containerResourceRequirements'])
        self.location = obj_dict['location']
        self.public_ip = obj_dict['publicIp']
        self.scoring_uri = obj_dict['scoringUri']
        self.ssl_certificate = obj_dict['sslCertificate']
        self.ssl_enabled = obj_dict['sslEnabled']
        self.ssl_key = obj_dict['sslKey']
        self.public_fqdn = obj_dict.get('publicFqdn')

        # Initialize other ACI utility attributes
        self.image = Image.deserialize(workspace, obj_dict['imageDetails']) if 'imageDetails' in obj_dict else None
        self.swagger_uri = '/'.join(self.scoring_uri.split('/')[:-1]) + WEBSERVICE_SWAGGER_PATH \
            if self.scoring_uri else None

    @staticmethod
    def deploy_configuration(cpu_cores=None, memory_gb=None, tags=None, properties=None, description=None,
                             location=None, auth_enabled=None, ssl_enabled=None, enable_app_insights=None,
                             ssl_cert_pem_file=None, ssl_key_pem_file=None, ssl_cname=None, dns_name_label=None):
        """Create a configuration object for deploying an ACI Webservice.

        :param cpu_cores: The number of cpu cores to allocate for this Webservice. Can be a decimal. Defaults to 0.1
        :type cpu_cores: float
        :param memory_gb: The amount of memory (in GB) to allocate for this Webservice. Can be a decimal.
            Defaults to 0.5
        :type memory_gb: float
        :param tags: Dictionary of key value tags to give this Webservice
        :type tags: dict[str, str]
        :param properties: Dictionary of key value properties to give this Webservice. These properties cannot
            be changed after deployment, however new key value pairs can be added
        :type properties: dict[str, str]
        :param description: A description to give this Webservice
        :type description: str
        :param location: The Azure region to deploy this Webservice to. If not specified the Workspace location will
            be used. More details on available regions can be found here:
            https://azure.microsoft.com/en-us/global-infrastructure/services/?regions=all&products=container-instances
        :type location: str
        :param auth_enabled: Whether or not to enable auth for this Webservice. Defaults to False
        :type auth_enabled: bool
        :param ssl_enabled: Whether or not to enable SSL for this Webservice. Defaults to False
        :type ssl_enabled: bool
        :param enable_app_insights: Whether or not to enable AppInsights for this Webservice. Defaults to False
        :type enable_app_insights: bool
        :param ssl_cert_pem_file: The cert file needed if SSL is enabled
        :type ssl_cert_pem_file: str
        :param ssl_key_pem_file: The key file needed if SSL is enabled
        :type ssl_key_pem_file: str
        :param ssl_cname: The cname for if SSL is enabled
        :type ssl_cname: str
        :param dns_name_label: The dns name label for the scoring endpoint.
            If not specified a unique dns name label will be generated for the scoring endpoint.
        :type dns_name_label: str
        :return: A configuration object to use when deploying a Webservice object
        :rtype: AciServiceDeploymentConfiguration
        :raises: WebserviceException
        """
        config = AciServiceDeploymentConfiguration(cpu_cores, memory_gb, tags, properties, description, location,
                                                   auth_enabled, ssl_enabled, enable_app_insights, ssl_cert_pem_file,
                                                   ssl_key_pem_file, ssl_cname, dns_name_label)
        return config

    @staticmethod
    def _deploy(workspace, name, image, deployment_config):
        """Deploy the Webservice.

        :param workspace:
        :type workspace: azureml.core.workspace.Workspace
        :param name:
        :type name: str
        :param image:
        :type image: azureml.core.image.Image
        :param deployment_config:
        :type deployment_config: AciServiceDeploymentConfiguration | None
        :return:
        :rtype: AciWebservice
        """
        if not deployment_config:
            deployment_config = AciWebservice.deploy_configuration()
        elif not isinstance(deployment_config, AciServiceDeploymentConfiguration):
            raise WebserviceException('Error, provided deployment configuration must be of type '
                                      'AciServiceDeploymentConfiguration in order to deploy an ACI service.',
                                      logger=module_logger)
        deployment_config.validate_image(image)
        create_payload = AciWebservice._build_create_payload(name, image, deployment_config)
        return Webservice._deploy_webservice(workspace, name, create_payload, AciWebservice)

    @staticmethod
    def _build_create_payload(name, image, deploy_config):
        """Construct the payload used to create this Webservice.

        :param name:
        :type name: str
        :param image:
        :type image: azureml.core.image.Image
        :param deploy_config:
        :type deploy_config: azureml.core.compute.AciServiceDeploymentConfiguration
        :return:
        :rtype: dict
        """
        import copy
        from azureml._model_management._util import aci_service_payload_template
        json_payload = copy.deepcopy(aci_service_payload_template)
        json_payload['name'] = name
        json_payload['imageId'] = image.id
        json_payload['kvTags'] = deploy_config.tags
        json_payload['description'] = deploy_config.description
        json_payload['containerResourceRequirements']['cpu'] = deploy_config.cpu_cores
        json_payload['containerResourceRequirements']['memoryInGB'] = deploy_config.memory_gb
        json_payload['location'] = deploy_config.location

        properties = deploy_config.properties or {}
        properties.update(global_tracking_info_registry.gather_all())
        json_payload['properties'] = properties

        if deploy_config.auth_enabled is None:
            del (json_payload['authEnabled'])
        else:
            json_payload['authEnabled'] = deploy_config.auth_enabled
        if deploy_config.ssl_enabled is None:
            del (json_payload['sslEnabled'])
        else:
            json_payload['sslEnabled'] = deploy_config.ssl_enabled
        if deploy_config.enable_app_insights is None:
            del (json_payload['appInsightsEnabled'])
        else:
            json_payload['appInsightsEnabled'] = deploy_config.enable_app_insights
        if deploy_config.dns_name_label:
            json_payload['dnsNameLabel'] = deploy_config.dns_name_label
        else:
            del (json_payload['dnsNameLabel'])
        try:
            with open(deploy_config.ssl_cert_pem_file, 'r') as cert_file:
                cert_data = cert_file.read()
            json_payload['sslCertificate'] = cert_data
        except Exception:
            del (json_payload['sslCertificate'])
        try:
            with open(deploy_config.ssl_key_pem_file, 'r') as key_file:
                key_data = key_file.read()
            json_payload['sslKey'] = key_data
        except Exception:
            del (json_payload['sslKey'])
        if deploy_config.ssl_cname is None:
            del (json_payload['cname'])
        else:
            json_payload['cname'] = deploy_config.ssl_cname

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

    def update(self, image=None, tags=None, properties=None, description=None, auth_enabled=None, ssl_enabled=None,
               ssl_cert_pem_file=None, ssl_key_pem_file=None, ssl_cname=None, enable_app_insights=None, models=None,
               inference_config=None):
        """Update the Webservice with provided properties.

        Values left as None will remain unchanged in this Webservice.

        :param image: A new Image to deploy to the Webservice
        :type image: azureml.core.image.Image
        :param tags: Dictionary of key value tags to give this Webservice. Will replace existing tags.
        :type tags: dict[str, str]
        :param properties: Dictionary of key value properties to add to existing properties dictionary
        :type properties: dict[str, str]
        :param description: A description to give this Webservice
        :type description: str
        :param auth_enabled: Enable or disable auth for this Webservice
        :type auth_enabled: bool
        :param ssl_enabled: Whether or not to enable SSL for this Webservice
        :type ssl_enabled: bool
        :param ssl_cert_pem_file: The cert file needed if SSL is enabled
        :type ssl_cert_pem_file: str
        :param ssl_key_pem_file: The key file needed if SSL is enabled
        :type ssl_key_pem_file: str
        :param ssl_cname: The cname for if SSL is enabled
        :type ssl_cname: str
        :param enable_app_insights: Whether or not to enable AppInsights for this Webservice
        :type enable_app_insights: bool
        :param models: A list of Model objects to package into the updated service
        :type models: :class:`list[azureml.core.model.Model]`
        :param inference_config: An InferenceConfig object used to provide the required model deployment properties.
        :type inference_config: azureml.core.model.InferenceConfig
        :return:
        :rtype: None
        """
        if not image and tags is None and properties is None and not description and auth_enabled is None \
           and ssl_enabled is None and not ssl_cert_pem_file and not ssl_key_pem_file and not ssl_cname \
           and enable_app_insights is None and models is None and inference_config is None:
            raise WebserviceException('No parameters provided to update.', logger=module_logger)

        cert_data = ""
        key_data = ""
        if ssl_enabled or (ssl_enabled is None and self.ssl_enabled):
            if not ssl_cert_pem_file or not ssl_key_pem_file or not ssl_cname:
                raise WebserviceException('SSL is enabled, you must provide a SSL certificate, key, and cname.',
                                          logger=module_logger)
            else:
                try:
                    with open(ssl_cert_pem_file, 'r') as cert_file:
                        cert_data = cert_file.read()
                    with open(ssl_key_pem_file, 'r') as key_file:
                        key_data = key_file.read()
                except (IOError, OSError) as exc:
                    raise WebserviceException("Error while reading ssl information:\n{}".format(exc),
                                              logger=module_logger)
        if inference_config is None and models:
            raise WebserviceException('Error, both "models" and "inference_config" inputs must be provided in order '
                                      'to update the models on the service.', logger=module_logger)

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

        headers = {'Content-Type': 'application/json-patch+json'}
        headers.update(self._auth.get_authentication_header())
        params = {'api-version': MMS_WORKSPACE_API_VERSION}

        properties = properties or {}
        properties.update(global_tracking_info_registry.gather_all())

        patch_list = []
        if image:
            patch_list.append({'op': 'replace', 'path': '/imageId', 'value': image.id})
        if tags is not None:
            patch_list.append({'op': 'replace', 'path': '/kvTags', 'value': tags})
        if properties is not None:
            for key in properties:
                patch_list.append({'op': 'add', 'path': '/properties/{}'.format(key), 'value': properties[key]})
        if description:
            patch_list.append({'op': 'replace', 'path': '/description', 'value': description})
        if auth_enabled is not None:
            patch_list.append({'op': 'replace', 'path': '/authEnabled', 'value': auth_enabled})
        if ssl_enabled is not None:
            patch_list.append({'op': 'replace', 'path': '/sslEnabled', 'value': ssl_enabled})
        if ssl_cert_pem_file and ssl_enabled or ssl_cert_pem_file and self.ssl_enabled:
            patch_list.append({'op': 'replace', 'path': '/sslCertificate', 'value': cert_data})
        if ssl_key_pem_file and ssl_enabled or ssl_key_pem_file and self.ssl_enabled:
            patch_list.append({'op': 'replace', 'path': '/sslKey', 'value': key_data})
        if ssl_cname and ssl_enabled or ssl_cname and self.ssl_enabled:
            patch_list.append({'op': 'replace', 'path': '/cname', 'value': ssl_cname})
        if enable_app_insights is not None:
            patch_list.append({'op': 'replace', 'path': '/appInsightsEnabled', 'value': enable_app_insights})
        resp = ClientBase._execute_func(get_requests_session().patch, self._mms_endpoint, headers=headers,
                                        params=params, json=patch_list, timeout=MMS_SYNC_TIMEOUT_SECONDS)

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
        self.update(properties=updated_properties)

        print('Image tag properties operation complete.')

    def serialize(self):
        """Convert this Webservice into a json serialized dictionary.

        :return: The json representation of this Webservice
        :rtype: dict
        """
        properties = super(AciWebservice, self).serialize()
        container_resource_requirements = self.container_resource_requirements.serialize() \
            if self.container_resource_requirements else None
        image = self.image.serialize() if self.image else None
        aci_properties = {'containerResourceRequirements': container_resource_requirements, 'imageId': self.image_id,
                          'imageDetails': image, 'scoringUri': self.scoring_uri, 'location': self.location,
                          'authEnabled': self.auth_enabled, 'sslEnabled': self.ssl_enabled,
                          'appInsightsEnabled': self.enable_app_insights, 'sslCertificate': self.ssl_certificate,
                          'sslKey': self.ssl_key, 'cname': self.cname, 'publicIp': self.public_ip,
                          'publicFqdn': self.public_fqdn}
        properties.update(aci_properties)
        return properties


class ContainerResourceRequirements(object):
    """Class containing details for the resource requirements for the Webservice."""

    _expected_payload_keys = ['cpu', 'memoryInGB']

    def __init__(self, cpu, memory_in_gb):
        """Initialize the container resource requirements.

        :param cpu: The number of cpu cores to allocate for this Webservice. Can be a decimal
        :type cpu: float
        :param memory_in_gb: The amount of memory (in GB) to allocate for this Webservice. Can be a decimal
        :type memory_in_gb: float
        """
        self.cpu = cpu
        self.memory_in_gb = memory_in_gb

    def serialize(self):
        """Convert this ContainerResourceRequirements into a json serialized dictionary.

        :return: The json representation of this ContainerResourceRequirements
        :rtype: dict
        """
        return {'cpu': self.cpu, 'memoryInGB': self.memory_in_gb}

    @staticmethod
    def deserialize(payload_obj):
        """Convert a json object into a ContainerResourceRequirements object.

        :param payload_obj: A json object to convert to a ContainerResourceRequirements object
        :type payload_obj: dict
        :return: The ContainerResourceRequirements representation of the provided json object
        :rtype: azureml.core.webservice.aci.ContainerResourceRequirements
        """
        for payload_key in ContainerResourceRequirements._expected_payload_keys:
            if payload_key not in payload_obj:
                raise WebserviceException('Invalid webservice payload, missing {} for containerResourceReservation:\n'
                                          '{}'.format(payload_key, payload_obj), logger=module_logger)

        return ContainerResourceRequirements(payload_obj['cpu'], payload_obj['memoryInGB'])


class AciServiceDeploymentConfiguration(WebserviceDeploymentConfiguration):
    """Service deployment configuration object for services deployed to ACI.

    :param cpu_cores: The number of cpu cores to allocate for this Webservice. Can be a decimal. Defaults to 0.1
    :type cpu_cores: float
    :param memory_gb: The amount of memory (in GB) to allocate for this Webservice. Can be a decimal.
        Defaults to 0.5
    :type memory_gb: float
    :param tags: Dictionary of key value tags to give this Webservice
    :type tags: dict[str, str]
    :param properties: Dictionary of key value properties to give this Webservice. These properties cannot
        be changed after deployment, however new key value pairs can be added
    :type properties: dict[str, str]
    :param description: A description to give this Webservice
    :type description: str
    :param location: The Azure region to deploy this Webservice to. If not specified the Workspace location will
        be used. More details on available regions can be found here:
        https://azure.microsoft.com/en-us/global-infrastructure/services/?regions=all&products=container-instances
    :type location: str
    :param auth_enabled: Whether or not to enable auth for this Webservice. Defaults to False
    :type auth_enabled: bool
    :param ssl_enabled: Whether or not to enable SSL for this Webservice. Defaults to False
    :type ssl_enabled: bool
    :param enable_app_insights: Whether or not to enable AppInsights for this Webservice. Defaults to False
    :type enable_app_insights: bool
    :param ssl_cert_pem_file: The cert file needed if SSL is enabled
    :type ssl_cert_pem_file: str
    :param ssl_key_pem_file: The key file needed if SSL is enabled
    :type ssl_key_pem_file: str
    :param ssl_cname: The cname for if SSL is enabled
    :type ssl_cname: str
    """

    webservice_type = AciWebservice

    def __init__(self, cpu_cores=None, memory_gb=None, tags=None, properties=None, description=None, location=None,
                 auth_enabled=None, ssl_enabled=None, enable_app_insights=None, ssl_cert_pem_file=None,
                 ssl_key_pem_file=None, ssl_cname=None, dns_name_label=None):
        """Create a configuration object for deploying an ACI Webservice.

        :param cpu_cores: The number of cpu cores to allocate for this Webservice. Can be a decimal. Defaults to 0.1
        :type cpu_cores: float
        :param memory_gb: The amount of memory (in GB) to allocate for this Webservice. Can be a decimal.
            Defaults to 0.5
        :type memory_gb: float
        :param tags: Dictionary of key value tags to give this Webservice
        :type tags: dict[str, str]
        :param properties: Dictionary of key value properties to give this Webservice. These properties cannot
            be changed after deployment, however new key value pairs can be added
        :type properties: dict[str, str]
        :param description: A description to give this Webservice
        :type description: str
        :param location: The Azure region to deploy this Webservice to. If not specified the Workspace location will
            be used. More details on available regions can be found here:
            https://azure.microsoft.com/en-us/global-infrastructure/services/?regions=all&products=container-instances
        :type location: str
        :param auth_enabled: Whether or not to enable auth for this Webservice. Defaults to False
        :type auth_enabled: bool
        :param ssl_enabled: Whether or not to enable SSL for this Webservice. Defaults to False
        :type ssl_enabled: bool
        :param enable_app_insights: Whether or not to enable AppInsights for this Webservice. Defaults to False
        :type enable_app_insights: bool
        :param ssl_cert_pem_file: The cert file needed if SSL is enabled
        :type ssl_cert_pem_file: str
        :param ssl_key_pem_file: The key file needed if SSL is enabled
        :type ssl_key_pem_file: str
        :param ssl_cname: The cname for if SSL is enabled
        :type ssl_cname: str
        :param dns_name_label: The dns name label for the scoring endpoint.
            If not specified a unique dns name label will be generated for the scoring endpoint.
        :type dns_name_label: str
        :raises: WebserviceException
        """
        super(AciServiceDeploymentConfiguration, self).__init__(AciWebservice)
        self.cpu_cores = cpu_cores
        self.memory_gb = memory_gb
        self.tags = tags
        self.properties = properties
        self.description = description
        self.location = location
        self.auth_enabled = auth_enabled
        self.ssl_enabled = ssl_enabled
        self.enable_app_insights = enable_app_insights
        self.ssl_cert_pem_file = ssl_cert_pem_file
        self.ssl_key_pem_file = ssl_key_pem_file
        self.ssl_cname = ssl_cname
        self.dns_name_label = dns_name_label
        self.validate_configuration()

    def validate_configuration(self):
        """Check that the specified configuration values are valid.

        Will raise a WebserviceException if validation fails.

        :raises: WebserviceException
        """
        if self.cpu_cores and self.cpu_cores <= 0:
            raise WebserviceException('Invalid configuration, cpu_cores must be positive.', logger=module_logger)
        if self.memory_gb and self.memory_gb <= 0:
            raise WebserviceException('Invalid configuration, memory_gb must be positive.', logger=module_logger)
        if self.ssl_enabled:
            if not self.ssl_cert_pem_file or not self.ssl_key_pem_file or not self.ssl_cname:
                raise WebserviceException('SSL is enabled, you must provide a SSL certificate, key, and cname.',
                                          logger=module_logger)
