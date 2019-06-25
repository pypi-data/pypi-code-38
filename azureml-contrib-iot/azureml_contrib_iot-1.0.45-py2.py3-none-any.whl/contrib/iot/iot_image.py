# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Create an AI container to deploy to Azure IoT."""

import os

from azureml.core.image import Image
from azureml.core.image.image import ImageConfig, Asset, TargetRuntime
from azureml.exceptions import WebserviceException
from azureml._model_management._util import validate_path_exists_or_throw
from ._container_image_request_builder import ContainerImageRequestBuilder
from azureml._model_management._constants import DOCKER_IMAGE_TYPE, IOT_IMAGE_FLAVOR


class IotContainerImage(Image):
    """Class for IoT container images."""

    _image_type = DOCKER_IMAGE_TYPE

    _image_flavor = IOT_IMAGE_FLAVOR

    _expected_payload_keys = Image._expected_payload_keys + ['assets', 'driverProgram', 'targetRuntime']

    _log_aml_debug = True

    SUPPORTED_RUNTIMES = ['python']
    SUPPORTED_ARCHITECTURES = ['arm32v7']

    def _initialize(self, workspace, obj_dict):
        super(IotContainerImage, self)._initialize(workspace, obj_dict)

        self.image_flavor = IotContainerImage._image_flavor
        self.assets = [Asset.deserialize(asset_payload) for asset_payload in obj_dict['assets']]
        self.driver_program = obj_dict['driverProgram']
        self.target_runtime = TargetRuntime.deserialize(obj_dict['targetRuntime'])

    @staticmethod
    def image_configuration(execution_script, architecture, requirements=None, docker_file=None,
                            dependencies=None, tags=None, properties=None, description=None):
        """Image config specific to IoT Container images - requires execution script and architecture.

        :param execution_script: Path to local file that contains the code to run for the image
        :type execution_script: str
        :param architecture: Architecture to target. Currently supported architecture is 'arm32v7'
        :type architecture: str
        :param requirements: Path to local file containing pip requirements.txt  to use for the image
        :type requirements: str
        :param docker_file: Path to local file containing additional Docker steps to run when setting up the image
        :type docker_file: str
        :param dependencies: List of paths to additional files/folders that the image needs to run
        :type dependencies: list[str]
        :param tags: Dictionary of key value tags to give this image
        :type tags: dict[str, str]
        :param properties: Dictionary of key value properties to give this image. These properties cannot
            be changed after deployment, however new key value pairs can be added
        :type properties: dict[str, str]
        :param description: A description to give this image
        :type description: str
        """
        conf = IotImageConfig(execution_script, architecture, requirements, docker_file, dependencies,
                              tags, properties, description)

        return conf

    def serialize(self):
        """Convert this IotContainerImage into a json serialized dictionary.

        :return: The json representation of this Image
        :rtype: dict
        """
        serialized_image = super(IotContainerImage, self).serialize()
        serialized_image['assets'] = [asset.serialize() for asset in self.assets] if self.assets else None
        serialized_image['driverProgram'] = self.driver_program
        serialized_image['targetRuntime'] = self.target_runtime.serialize() if self.target_runtime else None
        return serialized_image


class IotImageConfig(ImageConfig):
    """Image config specific to IoT containers."""

    def __init__(self, execution_script, architecture, requirements=None, docker_file=None,
                 dependencies=None, tags=None, properties=None, description=None):
        """Initialize the config object.

        :param execution_script: Path to local file that contains the code to run for the image
        :type execution_script: str
        :param architecture: Architecture to target. Currently supported architecture is 'arm32v7'
        :type architecture: str
        :param requirements: Path to local file containing pip requirements.txt  to use for the image
        :type requirements: str
        :param docker_file: Path to local file containing additional Docker steps to run when setting up the image
        :type docker_file: str
        :param dependencies: List of paths to additional files/folders that the image needs to run
        :type dependencies: list[str]
        :param tags: Dictionary of key value tags to give this image
        :type tags: dict[str, str]
        :param properties: Dictionary of key value properties to give this image. These properties cannot
            be changed after deployment, however new key value pairs can be added
        :type properties: dict[str, str]
        :param description: A description to give this image
        :type description: str
        :raises: azureml.exceptions.WebserviceException
        """
        self.execution_script = execution_script
        self.runtime = "python"
        self.architecture = architecture
        self.requirements = requirements
        self.docker_file = docker_file
        self.dependencies = dependencies
        self.tags = tags
        self.properties = properties
        self.description = description

        self.execution_script_path = os.path.abspath(os.path.dirname(self.execution_script))
        self.validate_configuration()

    def build_create_payload(self, workspace, name, model_ids):
        """Build the creation payload associated with this configuration object.

        :param workspace: The workspace associated with the image
        :type workspace: azureml.core.workspace.Workspace
        :param name: The name of the image
        :type name: str
        :param model_ids: A list of model IDs to be packaged with the image
        :type model_ids: list[str]
        :return: The creation payload to use for Image creation
        :rtype: dict
        """
        # create basic payload
        request_builder = ContainerImageRequestBuilder(workspace, IotContainerImage._image_flavor, name,
                                                       self.tags, self.properties, self.description)

        # add python stuff to payload
        self.execution_script = self.execution_script.rstrip(os.sep)
        request_builder.set_python_properties(self.runtime.lower(),
                                              self.architecture,
                                              self.execution_script,
                                              requirements=self.requirements,
                                              conda_file=None)

        # add docker file fragments
        request_builder.set_dockerfile(self.docker_file)

        # add models
        request_builder.set_model_ids(model_ids)

        # add dependencies
        request_builder.set_dependencies(self.dependencies)

        json = request_builder.get_payload()
        return json

    def validate_configuration(self):
        """Validate parameters to constructor.

        Validate the parameters in the order that they're passed to the constructor
        so the user can build up a valid object.

        :raises: WebserviceException
        :return: None
        """
        # The driver file must be in the current directory
        if not os.getcwd() == self.execution_script_path:
            raise WebserviceException('Unable to use a execution file not in current directory. '
                                      'Please navigate to the location of the execution file and try again.')

        validate_path_exists_or_throw(self.execution_script, "Execution script file")

        if self.architecture.lower() not in IotContainerImage.SUPPORTED_ARCHITECTURES:
            raise WebserviceException('Provided architecture not supported. '
                                      'Possible architectures are: {}'
                                      .format('|'.join(IotContainerImage.SUPPORTED_ARCHITECTURES)))

        if self.runtime.lower() not in IotContainerImage.SUPPORTED_RUNTIMES:
            raise WebserviceException('Provided runtime not supported. '
                                      'Possible runtimes are: {}'
                                      .format('|'.join(IotContainerImage.SUPPORTED_RUNTIMES)))

        if self.requirements:
            validate_path_exists_or_throw(self.requirements, "Requirements file")

        if self.docker_file:
            validate_path_exists_or_throw(self.docker_file, "Docker file")

        if self.dependencies:
            for dependency in self.dependencies:
                validate_path_exists_or_throw(dependency, "Dependency")

    @staticmethod
    def deserialize(workspace, image_payload):
        """Convert a json object into an IotContainerImage object.

        Will fail if the provided workspace is not the workspace the image is
        registered under.

        :param workspace: The workspace object the IotContainerImage is registered under
        :type workspace: azureml.core.workspace.Workspace
        :param image_payload: A json object to convert to a IotContainerImage object
        :type image_payload: dict
        :return: The IotContainerImage representation of the provided json object
        :rtype: azureml.contrib.iot.iot_image.IotContainerImage
        """
        IotContainerImage._deserialize(workspace, image_payload)
