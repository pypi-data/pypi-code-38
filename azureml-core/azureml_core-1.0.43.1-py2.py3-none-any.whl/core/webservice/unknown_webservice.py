# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for managing unknown Webservices in Azure Machine Learning service."""

from azureml._model_management._constants import UNKNOWN_WEBSERVICE_TYPE
from azureml.core.webservice import Webservice


class UnknownWebservice(Webservice):
    """Class for unknown Webservices."""

    # _expected_payload_keys inherited from Webservice

    _webservice_type = UNKNOWN_WEBSERVICE_TYPE

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
        # Validate obj_dict with _expected_payload_keys from parent Webservice
        UnknownWebservice._validate_get_payload(obj_dict)

        # Initialize common Webservice attributes
        super(UnknownWebservice, self)._initialize(workspace, obj_dict)

        # Initialize optional UnknownWebservice specific attributes (based on the BrainwaveWebservice)
        mms_sdk_map = {
            'ipAddress': 'ip_address',
            'port': 'port',
            'numReplicas': 'num_replicas',
            'sslEnabled': 'ssl'
        }
        for key in mms_sdk_map:
            sdk_key = mms_sdk_map[key]
            self.__dict__[sdk_key] = obj_dict[key] if key in obj_dict else None

        # check to get scoring URI
        if self.ip_address and self.port:
            self.scoring_uri = "{}:{}".format(self.ip_address, self.port)

    @staticmethod
    def _deploy(workspace, name, image, deployment_config, deployment_target):
        """Deploy the Webservice.

        :param workspace:
        :type workspace: azureml.core.workspace.Workspace
        :param name:
        :type name: str
        :param image:
        :type image: azureml.core.image.image.Image
        :param deployment_config:
        :type deployment_config: WebserviceDeploymentConfiguration
        :param deployment_target:
        :type deployment_target: azureml.core.compute.ComputeTarget
        :return:
        :rtype: Webservice
        """
        raise NotImplementedError("Cannot deploy Webservice because webservice type is not known.")

    def run(self, input):
        """Call this Webservice with the provided input.

        :param input: The input to call the Webservice with
        :type input: varies
        :return: The result of calling the Webservice
        :rtype: dict
        :raises: WebserviceException
        """
        raise NotImplementedError("Cannot run Webservice because webservice type is not known.")

    def update(self, *args):
        """Update the Webservice. Possible options to update vary based on Webservice type.

        :param args: Values to update
        :type args: varies
        :raises: WebserviceException
        """
        raise NotImplementedError("Cannot update Webservice because webservice type is not known.")
