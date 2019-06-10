# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Create an model converter to convert a model to dlc model flavor."""


from azureml._model_converters._model_convert_request import ModelConvertRequest
from azureml._model_converters._model_convert_client import ModelConvertClient
from azureml._model_converters.model_convert_operation import ModelConvertOperation
import azureml._model_converters._utils as utils


class SnpeConverter(object):
    """Class for converting models to dlc flavor using snpe."""

    @staticmethod
    def convert_tf_model(workspace,
                         source_model,
                         input_node,
                         input_dims,
                         outputs_nodes,
                         allow_unconsumed_nodes=True,
                         mirror_content=False,
                         tool_version=None):
        """Use snpe-tensorflow-to-dlc to convert a TensorFlow model into an SNPE DLC file.

        :param workspace:
        :type workspace: azureml.core.workspace.Workspace
        :param source_model: Registered model to be converted
        :type source_model: azureml.core.model or model id str
        :param input_node: Name of the input layer
        :type input_node: str
        :param input_dims: List of dimensions for the input layer
        :type input_dims: int list
        :param outputs_nodes: List of graph's output nodes where each one will represent the output layer
            of the network
        :type outputs_nodes: str list
        :param allow_unconsumed_nodes: Uses a relaxed graph node to layer mapping algorithm which may not use
            all graph nodes
        :type allow_unconsumed_nodes: bool
        :param mirror_content: Copy registered model folder contents to the converted model folder
        :type mirror_content: bool
        :param tool_version: Optional tool version
        :type tool_version: str
        :return: Object to wait for conversion and get the converted model
        :rtype: ModelConvertOperation
        """
        # group the compile options used for conversion
        _target_model_flavor = "DLC"
        _input_node = "inputNode"
        _input_dims = "inputDims"
        _outputs_nodes = "outputNodes"
        _allow_unconsumed_nodes = 'allowUnconsumedNodes'
        _mirror_input_folder = 'mirrorInputFolder'
        _model_flavor_tf = 'TF'

        source_model_id = utils._get_model_id(workspace, source_model)

        # create convert request object
        request = ModelConvertRequest(modelId=source_model_id, sourceModelFlavor=_model_flavor_tf,
                                      targetModelFalvor=_target_model_flavor,
                                      toolName="snpe",
                                      toolVersion=tool_version)
        request.compilation_options[_input_node] = input_node
        request.compilation_options[_allow_unconsumed_nodes] = allow_unconsumed_nodes
        request.compilation_options[_input_dims] = utils._get_as_str(input_dims)
        request.compilation_options[_outputs_nodes] = utils._get_as_str(outputs_nodes)
        request.compilation_options[_mirror_input_folder] = mirror_content

        # create model convert client and start model conversion
        client = ModelConvertClient(workspace)
        operation_id = client.convert_model(request)

        # create and return ModelConvert operation
        return ModelConvertOperation(workspace, operation_id)

    @staticmethod
    def convert_caffe_model(workspace,
                            source_model,
                            mirror_content=False,
                            tool_version=None):
        """Use snpe-caffe-to-dlc to convert a Caffe model into an SNPE DLC file.

        :param workspace:
        :type workspace: azureml.core.workspace.Workspace
        :param source_model: Registered model to be converted
        :type source_model: azureml.core.model or model id str
        :param mirror_content: Copy registered model folder contents to the converted model folder
        :type mirror_content: bool
        :param tool_version: Optional tool version
        :type tool_version: str
        :return: Object to wait for conversion and get the converted model
        :rtype: ModelConvertOperation
        """
        # group the compile options used for conversion
        _target_model_flavor = "DLC"
        _mirror_input_folder = 'mirrorInputFolder'
        _model_flavor_caffe = 'caffe'

        source_model_id = utils._get_model_id(workspace, source_model)

        # create convert request object
        request = ModelConvertRequest(modelId=source_model_id, sourceModelFlavor=_model_flavor_caffe,
                                      targetModelFalvor=_target_model_flavor,
                                      toolName="snpe",
                                      toolVersion=tool_version)
        request.compilation_options[_mirror_input_folder] = mirror_content

        # create model convert client and start model conversion
        client = ModelConvertClient(workspace)
        operation_id = client.convert_model(request)

        # create and return ModelConvert operation
        return ModelConvertOperation(workspace, operation_id)
