# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Create a model converter to convert a model to AccelOnnx model flavor."""

from azureml._model_converters._model_convert_request import ModelConvertRequest
from azureml._model_converters._model_convert_client import ModelConvertClient
from azureml._model_converters.model_convert_operation import ModelConvertOperation
import azureml._model_converters._utils as utils


class AccelOnnxConverter(object):
    """Class for converting models to AccelOnnx flavor."""

    @staticmethod
    def convert_tf_model(workspace,
                         source_model,
                         input_node,
                         outputs_nodes,
                         require_fpga_conversion=True):
        """
        Convert a TensorFlow model into a AccelOnnx model.

        :param workspace: Workspace object containing the registered model to retrieve
        :type workspace: azureml.core.workspace.Workspace
        :param source_model: Registered model to be converted
        :type source_model: azureml.core.model or model id str
        :param input_node: Name of the input layer
        :type input_node: str
        :param outputs_nodes: List of graph's output nodes where each one will represent the output layer
                              of the network
        :type outputs_nodes: str list
        :param require_fpga_conversion: Specify whether a FPGA is required for processing. Default value is True.
        :type require_fpga_conversion: bool
        :return: Object to wait for conversion and get the converted model
        :rtype: ModelConvertOperation
        """
        # group the compile options used for conversion
        _target_model_flavor = 'AccelOnnx'
        _input_node = 'input_node_names'
        _outputs_nodes = 'output_node_names'
        _model_flavor_tf = 'TF'
        _require_fpga_conversion = 'require_fpga_conversion'

        source_model_id = utils._get_model_id(workspace, source_model)

        # create convert request object
        request = ModelConvertRequest(modelId=source_model_id,
                                      sourceModelFlavor=_model_flavor_tf,
                                      targetModelFalvor=_target_model_flavor,
                                      toolName="fpga")
        request.compilation_options[_input_node] = input_node
        request.compilation_options[_outputs_nodes] = outputs_nodes
        request.compilation_options[_require_fpga_conversion] = require_fpga_conversion

        # create model convert client and start model conversion
        client = ModelConvertClient(workspace)
        operation_id = client.convert_model(request)

        # create and return ModelConvert operation
        return ModelConvertOperation(workspace, operation_id)
