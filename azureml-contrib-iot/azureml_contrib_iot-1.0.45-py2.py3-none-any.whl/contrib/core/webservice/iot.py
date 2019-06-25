# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for managing the Azure IoT Webservices in Azure Machine Learning service."""

from azureml.core.webservice import Webservice
from azureml.exceptions import WebserviceException
import copy
from ._util import iot_service_payload_template
from azureml._base_sdk_common.tracking import global_tracking_info_registry
from azureml._model_management._constants import IOT_WEBSERVICE_TYPE
from azureml.core.webservice.webservice import WebserviceDeploymentConfiguration


class IotWebservice(Webservice):
    """Class for IoT Webservices."""

    _expected_payload_keys = Webservice._expected_payload_keys + \
        ['iotDeviceId', 'routes', 'computeName', 'iotEdgeModules']
    _webservice_type = IOT_WEBSERVICE_TYPE

    def _initialize(self, workspace, obj_dict):
        """Initialize the Webservice instance.

        :param workspace:
        :type workspace: azureml.core.workspace.Workspace
        :param obj_dict:
        :type obj_dict: dict
        :return:
        :rtype: None
        """
        # Validate obj_dict with _expected_payload_keys
        IotWebservice._validate_get_payload(obj_dict)

        # Initialize common Webservice attributes
        super(IotWebservice, self)._initialize(workspace, obj_dict)

        # Initialize expected IoT specific attributes
        self.iot_device_id = obj_dict['iotDeviceId']
        self.routes = obj_dict['routes']
        self.compute_name = obj_dict['computeName']
        self.iot_edge_modules = obj_dict['iotEdgeModules']

    @staticmethod
    def deploy_configuration(routes=None, device_id=None, aml_module=None,
                             external_modules=None, acr_credentials=None,
                             tags=None, properties=None, description=None):
        """Create a configuration object for deploying to an IOT compute target.

        :param routes: routes of the IotHub
        :type routes: dict[str, str]
        :param device_id: the id of the iotDevice
        :type device_id: str
        :param aml_module: module settings for registered model
        :type aml_module: azureml.contrib.core.webservice.iot.IotBaseModuleSettings
        :param external_modules: modules settings for user custom models
        :type external_modules: list[azureml.contrib.core.webservice.iot.IotModuleSettings]
        :param acr_credentials: customer's acr credentails
        :type acr_credentials: list[azureml.core.container_registry.ContainerRegistry]
        :param tags: Dictionary of key value tags to give this Webservice
        :type tags: dict[str, str]
        :param properties: Dictionary of key value properties to give this Webservice. These properties cannot
            be changed after deployment, however new key value pairs can be added
        :param description: A description to give this Webservice
        :type description: str
        :return: A configuration object to use when deploying a Webservice object
        :rtype: IotServiceDeploymentConfiguration
        :raises: WebserviceException
        """

        config = IotServiceDeploymentConfiguration(
            routes, device_id, aml_module, external_modules,
            acr_credentials, tags, properties, description)

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
        :type deployment_config: IotServiceDeploymentConfiguration
        :param deployment_target:
        :type deployment_target: azureml.contrib.core.compute.IotHubCompute
        :return:
        :rtype: IotWebservice
        """
        if not deployment_target:
            raise WebserviceException('Error, deployment target must be provided.')
        if not deployment_config:
            raise WebserviceException('Error, deployment configuration must be provided.')
        elif not isinstance(deployment_config, IotServiceDeploymentConfiguration):
            raise WebserviceException('Error, provided deployment configuration must be of type '
                                      'IotServiceDeploymentConfiguration in order to deploy an IoT service.')
        deployment_config.validate_image(image)
        create_payload = IotWebservice._build_create_payload(name, image, deployment_config, deployment_target)
        return Webservice._deploy_webservice(workspace, name, create_payload, IotWebservice)

    @staticmethod
    def _build_create_payload(name, image, deploy_config, deployment_target):
        """Construct the payload used to create this Webservice.

        :param name:
        :type name: str
        :param image:
        :type image: azureml.core.image.Image
        :param deploy_config:
        :type deploy_config: IotServiceDeploymentConfiguration
        :param deployment_target:
        :type deployment_target: azureml.contrib.core.compute.IotHubCompute
        :return:
        :rtype: dict
        """
        # update common fields
        json_payload = copy.deepcopy(iot_service_payload_template)
        json_payload['name'] = name
        json_payload['computeType'] = IOT_WEBSERVICE_TYPE
        json_payload['computeName'] = deployment_target.name
        json_payload['imageId'] = image.id
        if deploy_config.description:
            json_payload['description'] = deploy_config.description
        else:
            del (json_payload['description'])

        if deploy_config.tags:
            json_payload['kvTags'] = deploy_config.tags

        properties = deploy_config.properties or {}
        properties.update(global_tracking_info_registry.gather_all())
        json_payload['properties'] = properties

        # update iot fields
        json_payload['routes'] = deploy_config.routes
        json_payload['iotDeviceId'] = deploy_config.device_id
        json_payload['iotEdgeModule'] = deploy_config.aml_module.serialize()

        if deploy_config.external_modules is None:
            del (json_payload['iotEdgeUserModule'])
        else:
            json_payload['iotEdgeUserModule'] = []
            for module in deploy_config.external_modules:
                json_payload['iotEdgeUserModule'].append(module.serialize())

        if deploy_config.acr_credentials is None:
            del (json_payload['acrCredentials'])
        else:
            json_payload['acrCredentials'] = IotWebservice._serialize_credentials(deploy_config.acr_credentials)

        return json_payload

    def run(self, input_data):
        """
        IoT webservice is not support this feature, calling this function always gets a WebserviceException
        """
        raise WebserviceException('Class does not support run method.')

    def update(self, *args):
        """
        IoT webservice is not implement this feature, calling this function always gets a NotImplementedError
        """
        raise NotImplementedError('Class does not implement update method yet.')

    def serialize(self):
        """Convert this Webservice into a json serialized dictionary.

        :return: The json representation of this Webservice
        :rtype: dict
        """
        self.scoring_uri = None
        properties = super(IotWebservice, self).serialize()
        iot_properties = {'iotDeviceId': self.iot_device_id, 'imageId': self.image_id,
                          'iotEdgeModules': self.iot_edge_modules,
                          'computeName': self.compute_name, 'routes': self.routes}
        properties.update(iot_properties)
        if 'scoringUri' in properties:
            del (properties['scoringUri'])

        return properties

    @staticmethod
    def _serialize_credentials(credential_list):
        credentials = []
        for credential in credential_list:
            credentials.append(
                {
                    'password': credential.password,
                    'user': credential.username,
                    'location': credential.address
                }
            )

        return credentials


class IotBaseModuleSettings:
    """Class containing module configurations for the registered model."""

    def __init__(self, name, env=None, create_option=None, properties_desired=None):
        """Construct the iotEdge module which represents the model registered in AML workspace

        :param name: the module name
        :type name: str
        :param env: environment variables
        :type env: dict[str, str]
        :param create_option:
        :type create_option: str
        :param properties_desired:
        :type properties_desired: dict[str, str]
        """
        self.name = name
        self.env = env
        self.create_option = create_option
        self.properties_desired = properties_desired

    def serialize(self):
        """Convert this IotBaseModuleSettings into a json serialized dictionary.

        :return: The json representation of this IotBaseModuleSettings
        :rtype: dict
        """
        data = {}
        data['moduleName'] = self.name
        if self.create_option:
            data['createOptions'] = self.create_option
        if self.env:
            data['environmentVariables'] = self.env
        if self.properties_desired:
            data['propertiesDesired'] = self.properties_desired

        return data


class IotModuleSettings(IotBaseModuleSettings):
    """Class containing module configurations for the unregistered models(user custom models)."""

    def __init__(self, name, image_location, env=None, create_option=None, properties_desired=None):
        """Construct the iotEdge module which represents the user custome model

        :param name: the module name
        :type name: str
        :param env: environment variables
        :type env: dict[str, str]
        :param create_option:
        :type create_option: str
        :param properties_desired:
        :type properties_desired: dict[str, str]
        :param image_location: url fo the image that contains the user custom model
        :type image_location: str
        """

        self.image_location = image_location
        super(IotModuleSettings, self).__init__(name, env, create_option, properties_desired)

    def serialize(self):
        """Convert this IotModuleSettings into a json serialized dictionary.

        :return: The json representation of this IotModuleSettings
        :rtype: dict
        """
        data = super(IotModuleSettings, self).serialize()
        if self.image_location:
            data['imageLocation'] = self.image_location

        return data


class IotServiceDeploymentConfiguration(WebserviceDeploymentConfiguration):
    """Service deployment configuration object for services deployed on IoT compute target.

    :param routes: routes of the IotHub
    :type routes: dict[str, str]
    :param device_id: the id of the iotDevice
    :type device_id: str
    :param aml_module: module settings for registered model
    :type aml_module: azureml.contrib.core.webservice.iot.IotBaseModuleSettings
    :param external_modules: modules settings for user custom models
    :type external_modules: list[azureml.contrib.core.webservice.iot.IotModuleSettings]
    :param acr_credentials: customer's acr credentails
    :type acr_credentials: list[azureml.core.container_registry.ContainerRegistry]
    :param tags: Dictionary of key value tags to give this Webservice
    :type tags: dict[str, str]
    :param properties: Dictionary of key value properties to give this Webservice. These properties cannot
        be changed after deployment, however new key value pairs can be added
    :type properties: dict[str, str]
    :param description: A description to give this Webservice
    :type description: str
    """
    webservice_type = IotWebservice

    def __init__(self, routes, device_id,
                 aml_module, external_modules=None, acr_credentials=None,
                 tags=None, properties=None, description=None):
        """Initialize a configuration object for deploying to an IoT compute target.

        :param routes: routes of the IotHub
        :type routes: dict[str, str]
        :param device_id: the id of the iotDevice
        :type device_id: str
        :param aml_module: module settings for registered model
        :type aml_module: IotBaseModuleSettings
        :param external_modules: modules settings for user custom models
        :type external_modules: list[IotModuleSettings]
        :param acr_credentials: customer's acr credentails
        :type acr_credentials: list[ContainerRegistry]
        :param tags: Dictionary of key value tags to give this Webservice
        :type tags: dict[str, str]
        :param properties: Dictionary of key value properties to give this Webservice. These properties cannot
            be changed after deployment, however new key value pairs can be added
        :type properties: dict[str, str]
        :param description: A description to give this Webservice
        :type description: str
        :raises: WebserviceException
        """
        super(IotServiceDeploymentConfiguration, self).__init__(IotWebservice)

        self.routes = routes
        self.device_id = device_id
        self.aml_module = aml_module
        self.external_modules = external_modules
        self.acr_credentials = acr_credentials
        self.tags = tags
        self.properties = properties
        self.description = description

        self.validate_configuration()

    def validate_configuration(self):
        """Check that the specified configuration values are valid.

        Will raise a WebserviceException if validation fails.

        :raises: WebserviceException
        """

        if self.aml_module is None:
            raise WebserviceException('Invalid configuration, aml_module must be provided.')
        else:
            if self.aml_module.name is None:
                raise WebserviceException('Invalid configuration, the name of aml_module must be provided.')
            if self.aml_module.env and not isinstance(self.aml_module.env, dict):
                raise WebserviceException('Invalid configuration, the type of aml_module.env must be dictionary.')
            if self.aml_module.properties_desired and not isinstance(self.aml_module.properties_desired, dict):
                raise WebserviceException(
                    'Invalid configuration, the type of aml_module.properties_desired must be dictionary.')
        if self.routes is None:
            raise WebserviceException('Invalid configuration, routes must be provided.')
        if self.device_id is None:
            raise WebserviceException('Invalid configuration, device_id must be provided.')

        if self.external_modules is not None:
            if self.acr_credentials:
                for credentail in self.acr_credentials:
                    if not credentail.address or not credentail.username or not credentail.password:
                        raise WebserviceException(
                            'Invalid configuration, acr_credentials must contain password, username and address.')

            for module in self.external_modules:
                if module.image_location is None:
                    raise WebserviceException(
                        'Invalid configuration, custom_module {0} missing image_location.'.format(module.name))
