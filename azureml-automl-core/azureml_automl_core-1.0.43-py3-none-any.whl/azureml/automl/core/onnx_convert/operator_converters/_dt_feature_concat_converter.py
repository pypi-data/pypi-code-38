# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""DataTransformer feature concatenator virtual op converter."""
from typing import Any, Dict, Optional, Union
import numbers
import numpy as np

import sys
from ..onnx_convert_constants import OnnxConvertConstants

# Import the onnx related packages, only if the python version is less than 3.7.
# The onnx package does not support python 3.7 yet.
if sys.version_info < OnnxConvertConstants.OnnxIncompatiblePythonVersion:
    from skl2onnx.proto import onnx_proto
    from skl2onnx.common.data_types import FloatType
    from skl2onnx.common.data_types import Int64Type
    from skl2onnx.common.data_types import StringType
    from skl2onnx.common.data_types import Int64TensorType
    from skl2onnx.common.data_types import FloatTensorType
    from skl2onnx.common.data_types import StringTensorType
    from skl2onnx.common.data_types import DictionaryType
    from skl2onnx.common.data_types import SequenceType

    from skl2onnx.common._apply_operation import apply_cast, apply_identity, apply_reshape, apply_mul
    from skl2onnx.common.utils import check_input_and_output_types, check_input_and_output_numbers
    from skl2onnx.common.utils_classifier import _finalize_converter_classes
    from skl2onnx.operator_converters.common import convert_integer_to_float
    from skl2onnx import update_registered_converter

# AutoML modules.
from automl.client.core.common.exceptions import OnnxConvertException    # noqa: E402
from ._abstract_operator_converter import _AbstractOperatorConverter    # noqa: E402


# The Virtual concatenator used by convert the DataTransformer.
class _VirtualConcatenator:
    def __init__(self, *args, **kwargs):
        pass


class DataTransformerFeatureConcatenatorConverter(_AbstractOperatorConverter):
    """DataTransformer feature concatenator virtual op converter."""

    def __init__(self):
        """Construct the DataTransformer feature concatenator virtual op converter."""
        type(self).OPERATOR_ALIAS = 'DataTransformerFeatureConcatenator'

    def setup(self):
        """Set up the converter."""
        update_registered_converter(_VirtualConcatenator,
                                    DataTransformerFeatureConcatenatorConverter.OPERATOR_ALIAS,
                                    DataTransformerFeatureConcatenatorConverter._calculate_concatenator_output_shapes,
                                    DataTransformerFeatureConcatenatorConverter._convert_concatenator)

    @staticmethod
    def _calculate_concatenator_output_shapes(operator):
        # All inputs and outputs must be numerical.
        check_input_and_output_types(operator, good_input_types=[FloatTensorType, Int64TensorType])
        # N means number of elements in dimension 0 (rows),
        # C means number of elements in dimension 1 (cols).
        # This N and C naming applies to other operator's shape calculator methods.
        N = operator.inputs[0].type.shape[0]
        C = 0       # type: Union[int, str]
        for variable in operator.inputs:
            if variable.type.shape[1] != 'None':
                C += variable.type.shape[1]
            else:
                C = 'None'
                break
        operator.outputs[0].type.shape = [N, C]

    @staticmethod
    def _convert_concatenator(scope, operator, container):
        # Check if it's possible to concatenate those inputs.
        type_set = set([type(v.type) for v in operator.inputs])
        number_type_set = {FloatType, FloatTensorType, Int64Type, Int64TensorType}
        if StringType in type_set and any(number_type in type_set for number_type in number_type_set):
            raise OnnxConvertException('We are not able to concatenate numerical tensor(s) and string tensor(s)')

        input_names = []  # input variables' names we want to concatenate
        input_dims = []  # dimensions of the variables that is going to be concatenated

        # Collect input variable names and do cast if needed.
        for variable in operator.inputs:
            if isinstance(variable.type, (Int64TensorType, Int64Type)):
                input_names.append(convert_integer_to_float(scope, variable, container))
            else:
                input_names.append(variable.full_name)
            # We assume input variables' shape are [1, C_1], ..., [1, C_n] if
            # there are n inputs.
            input_dims.append(variable.type.shape[1])

        # We use FeatureVectorizer to concatenate.
        op_type = OnnxConvertConstants.FeatureVectorizer
        attrs = {'name': scope.get_unique_operator_name(op_type), 'inputdimensions': input_dims}
        # We are the concatenator op, use the name of the operator's output
        # variable as concatenated variable name.
        concatenated_name = operator.outputs[0].full_name
        # Set up our FeatureVectorizer
        container.add_node(op_type, input_names, concatenated_name,
                           op_domain=OnnxConvertConstants.OnnxMLDomain, **attrs)
