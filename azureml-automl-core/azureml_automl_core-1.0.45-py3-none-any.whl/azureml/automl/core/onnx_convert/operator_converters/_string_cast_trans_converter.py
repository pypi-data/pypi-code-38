# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""StringCast transformer operator converter."""
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
from ...featurizer.transformer import StringCastTransformer    # noqa: E402

from ._abstract_operator_converter import _AbstractOperatorConverter    # noqa: E402


class StringCastTransformerConverter(_AbstractOperatorConverter):
    """StringCast transformer operator converter."""

    def __init__(self):
        """Construct the StringCast transformer operator converter."""
        type(self).OPERATOR_ALIAS = 'AutoMLStringCastTransformer'

    def setup(self):
        """Set up the converter."""
        update_registered_converter(StringCastTransformer,
                                    StringCastTransformerConverter.OPERATOR_ALIAS,
                                    StringCastTransformerConverter._calc_stringcasttransformer_output_shapes,
                                    StringCastTransformerConverter._convert_automl_stringcasttransformer)

    @staticmethod
    def _calc_stringcasttransformer_output_shapes(operator):
        # All inputs and outputs must be float.
        check_input_and_output_numbers(operator, input_count_range=1, output_count_range=1)
        check_input_and_output_types(operator, good_input_types=[
                                     FloatTensorType, Int64TensorType, StringTensorType])
        N = operator.inputs[0].type.shape[0]
        C = operator.inputs[0].type.shape[1]
        # We change the output type to string tensor.
        operator.outputs[0].type = StringTensorType([N, C])

    @staticmethod
    def _convert_automl_stringcasttransformer(scope, operator, container):
        # In the onnxruntime, it's invalid to cast from string type to string type.
        input_name = operator.inputs[0].full_name
        output_name = operator.outputs[0].full_name

        # Here we check if input type is already string.
        if isinstance(operator.inputs[0].type, StringTensorType):
            # if so, use an Identity op to pass through the input variable.
            apply_identity(scope, input_name, output_name, container)
        else:
            # Cast from/to string needs op version 9, explicitly define it.
            op_type = OnnxConvertConstants.Cast
            attrs = {'name': scope.get_unique_operator_name(op_type),
                     'to': onnx_proto.TensorProto.STRING}
            container.add_node(op_type, input_name, output_name, op_version=9, **attrs)
