# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""ImputationMarker operator converter."""
import numbers
import numpy as np

import sys
from ..onnx_convert_constants import OnnxConvertConstants

# Import the onnx related packages, only if the python version is less than 3.8.
# The onnx package does not support python 3.8 yet.
if sys.version_info < OnnxConvertConstants.OnnxIncompatiblePythonVersion:
    from skl2onnx.proto import onnx_proto
    from skl2onnx.common.data_types import Int64TensorType
    from skl2onnx.common.data_types import FloatTensorType
    from skl2onnx.common.data_types import StringTensorType
    from skl2onnx.common.data_types import DictionaryType
    from skl2onnx.common.data_types import SequenceType

    from skl2onnx.common._apply_operation import apply_cast, apply_identity, apply_reshape, apply_mul
    from skl2onnx.common.utils import check_input_and_output_types, check_input_and_output_numbers
    from skl2onnx import update_registered_converter

# AutoML modules.
from automl.client.core.common.exceptions import OnnxConvertException    # noqa: E402
from ...featurizer.transformer import ImputationMarker    # noqa: E402
from ._abstract_operator_converter import _AbstractOperatorConverter    # noqa: E402


class ImputationMarkerConverter(_AbstractOperatorConverter):
    """ImputationMarker operator converter."""

    def __init__(self):
        """Construct the ImputationMarker operator converter."""
        type(self).OPERATOR_ALIAS = 'AutoMLImputationMarker'

    def setup(self):
        """Set up the converter."""
        update_registered_converter(ImputationMarker,
                                    ImputationMarkerConverter.OPERATOR_ALIAS,
                                    ImputationMarkerConverter._calculate_automl_imputationmarker_output_shapes,
                                    ImputationMarkerConverter._convert_automl_imputationmarker)

    @staticmethod
    def _calculate_automl_imputationmarker_output_shapes(operator):
        # All inputs and outputs must be float.
        check_input_and_output_numbers(operator, input_count_range=1, output_count_range=1)
        check_input_and_output_types(operator, good_input_types=[FloatTensorType])
        N = operator.inputs[0].type.shape[0]
        C = operator.inputs[0].type.shape[1]
        operator.outputs[0].type.shape = [N, C]

    @staticmethod
    def _convert_automl_imputationmarker(scope, operator, container):
        op_type = OnnxConvertConstants.IsNaN
        input_name = operator.inputs[0].full_name
        nan_res_var = scope.get_unique_variable_name('impmk_nan_res_var')
        attrs = {'name': scope.get_unique_operator_name(op_type)}
        container.add_node(op_type, input_name, nan_res_var, op_version=9, **attrs)
        # Cast the result bool tensor to float.
        output_name = operator.outputs[0].full_name
        apply_cast(scope, nan_res_var, output_name, container, to=onnx_proto.TensorProto.FLOAT)
