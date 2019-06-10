# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Inference config to accelerate Neural Networks with Azure ML HW Accelerated Models Service."""

from azureml.exceptions import WebserviceException
from azureml.accel._accel_container_image import AccelImageConfiguration
from azureml.core.model import Model
from azureml.accel._accel_onnx_converter import AccelOnnxConverter
import logging

module_logger = logging.getLogger(__name__)


class AccelInferenceConfig():
    """
      Model deployment config specific to accel model deployments.

      Will either:
        1. Deploy a converted model if it's passed one.
        2. Deploy a previously converted model version of the model passed, if one exists.
        3. Convert the passed model and deploy the converted model.
    """

    def __init__(self, description=None, input_tensor=None, output_tensor=None):
        """
        Model deployment config specific to the accel model deployments.

        :param description: A description to give this image
        :type description: str
        :param input_tensor: The name of the input tensor to the model
            - only used if it needs to be converted.
        :type input_tensor: str
        :param output_tensor: The name of the output tensor to the model
            - only used if it needs to be converted.
        :type output_tensor: str
        """
        self.description = description
        self.input_tensor = input_tensor
        self.output_tensor = output_tensor
        self.source_directory = None

    def validate_configuration(self):
        """Check that the specified configuration values are valid.

        Will raise a WebserviceException if validation fails.

        :raises: WebserviceException
        """
        pass

    def build_create_payload(self, workspace, name, model_ids):
        """Build the creation payload for the Container image.
        For accelerated inference, the model id will be the base model,
        and may be converted or used to select a previously converted model.

        :param workspace: The workspace object to create the image in
        :type workspace: azureml.core.workspace.Workspace
        :param name: The name of the image
        :type name: str
        :param model_ids: A list containing a single model id to determine which
        :type model_ids: :class:`list[str]`
        :return: Container image creation payload
        :rtype: dict
        :raises: azureml.exceptions.WebserviceException
        """
        if (len(model_ids)) != 1:
            raise WebserviceException("Can only deploy accelerated inferencing with a single model.")

        model_id = model_ids[0]
        (name, version) = model_id.split(":")
        model = Model(workspace, id=model_id)
        if not model.parent_id:
            # try to get an existing converted model
            try:
                model = Model(workspace, "{}.{}.accelonnx".format(name, version))
                module_logger.info("Using already converted model %s.%s.accelonnx", name, version)
            except WebserviceException:
                module_logger.info("Converting %s to accelerated model", name)
                req = AccelOnnxConverter.convert_tf_model(workspace, model, self.input_tensor, self.output_tensor)
                req.wait_for_completion()
                try:
                    model = req.result
                except ValueError:
                    raise WebserviceException("Error, tried to deploy accelerated"
                                              "inferencing service but could not convert model.")

        return AccelImageConfiguration(description=self.description).build_create_payload(workspace, name, [model.id])

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
        raise WebserviceException("Model profiling is not supported for Accelerated models.")
