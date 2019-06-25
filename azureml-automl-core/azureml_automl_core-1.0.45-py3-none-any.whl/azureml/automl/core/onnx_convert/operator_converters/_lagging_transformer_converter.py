# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""LaggingTransformer operator converter."""
from typing import Any, List
import numbers
import numpy as np
from collections import deque

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
from ...featurizer.transformer import LaggingTransformer    # noqa: E402
from ._abstract_operator_converter import _AbstractOperatorConverter    # noqa: E402


class LaggingTransformerConverter(_AbstractOperatorConverter):
    """LaggingTransformer operator converter."""

    def __init__(self):
        """Construct the LaggingTransformer operator converter."""
        type(self).OPERATOR_ALIAS = 'AutoMLLaggingTransformer'

    def setup(self):
        """Set up the converter."""
        update_registered_converter(LaggingTransformer,
                                    LaggingTransformerConverter.OPERATOR_ALIAS,
                                    LaggingTransformerConverter._calculate_automl_laggingtransformer_output_shapes,
                                    LaggingTransformerConverter._convert_automl_laggingtransformer)

    @staticmethod
    def _calculate_automl_laggingtransformer_output_shapes(operator):
        raw_op = operator.raw_operator
        check_input_and_output_numbers(operator, input_count_range=1, output_count_range=1)
        check_input_and_output_types(operator, good_input_types=[FloatTensorType, Int64TensorType])
        N = operator.inputs[0].type.shape[0]
        C = operator.inputs[0].type.shape[1] * (1 + raw_op._lag_length)
        operator.outputs[0].type.shape = [N, C]

    @staticmethod
    def _convert_automl_laggingtransformer(scope, operator, container):
        raw_op = operator.raw_operator
        if not len(operator.inputs) == 1:
            raise OnnxConvertException('The number of input is not 1.')

        # We loop below operator building block for n times,
        # where n == lagging_length of the raw operator.
        idx_lag = 1
        num_iter = raw_op._lag_length
        input_var = operator.inputs[0]
        num_col_input = input_var.type.shape[1]

        queue = deque([])       # type: Any
        queue.append(input_var.full_name)

        while len(queue) > 0:
            input_name = queue.pop()

            # Slice the input to get cells[(0, 0), (-idx_lag, width_col)),
            # Reference: https://github.com/onnx/onnx/blob/master/docs/Operators.md#Slice
            op_type = OnnxConvertConstants.Slice
            sliced_variable_name = scope.get_unique_variable_name('lag_sliced_variable_' + str(idx_lag))
            attrs = {'name': scope.get_unique_operator_name(op_type),
                     'starts': [0, 0],
                     # Use INT_MAX as we want all rows including last row.
                     'ends': [-idx_lag, num_col_input]
                     }
            container.add_node(op_type, input_name, sliced_variable_name, **attrs)

            # Generate a tensor with the raw op's missing filling value, of the shape (idx_lag, width_col).
            missing_value_variable_name = scope.get_unique_variable_name('lag_missing_value_' + str(idx_lag))
            container.add_initializer(missing_value_variable_name, onnx_proto.TensorProto.FLOAT, [
                                      idx_lag, num_col_input], [np.float32(raw_op._missing_fill)])

            # Concat the filling tensor and the sliced tensor along axis 0 (row wise),
            # to make the shifted variable.
            op_type = OnnxConvertConstants.Concat
            shifted_variable_name = scope.get_unique_variable_name('lag_shifted_variable_' + str(idx_lag))
            attrs = {'name': scope.get_unique_operator_name(op_type), 'axis': 0}
            container.add_node(op_type, [missing_value_variable_name, sliced_variable_name],
                               shifted_variable_name, op_version=4, **attrs)

            # Concat the original input with the shifted variable along axis 1 (column wise),
            # to make the output of this iteration.
            op_type = OnnxConvertConstants.Concat
            if idx_lag < num_iter:
                # This is not the last lagging iteration.
                output_itr_variable_name = scope.get_unique_variable_name('lag_output_' + str(idx_lag))
            else:
                # Use output var name for the last iteration.
                output_itr_variable_name = operator.outputs[0].full_name

            attrs = {'name': scope.get_unique_operator_name(op_type), 'axis': 1}
            container.add_node(op_type, [input_name, shifted_variable_name],
                               output_itr_variable_name, op_version=4, **attrs)

            # Enqueue the current output var.
            if idx_lag < num_iter:
                queue.append(output_itr_variable_name)
                idx_lag += 1
