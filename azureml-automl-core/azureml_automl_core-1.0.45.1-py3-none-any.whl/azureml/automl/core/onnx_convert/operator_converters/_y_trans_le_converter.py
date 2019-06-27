# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""ImputationMarker operator converter."""
import numbers
import numpy as np
import six


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
    from skl2onnx.common.utils_classifier import _finalize_converter_classes
    from skl2onnx.operator_converters.common import convert_integer_to_float
    from skl2onnx import update_registered_converter

# AutoML modules.
from automl.client.core.common.exceptions import OnnxConvertException    # noqa: E402
from ._abstract_operator_converter import _AbstractOperatorConverter    # noqa: E402

import sklearn    # noqa: E402
from sklearn.base import BaseEstimator, ClassifierMixin    # noqa: E402


class _YTransformLabelEncoder(BaseEstimator, ClassifierMixin):
    """
    Virtual operator for converting the y transformer LabelEncoder.

    Containing the actual label encoder to do the y transform.
    This class is used by convert the y transformers.
    Since the object of this class needs to be put into last step of
    the reconstructed pipeline, it inherits the BaseEstimator and ClassifierMixin.
    But it's a dummy estimator, and only used for onnx conversion.
    """

    def __init__(self, le):
        """
        Construct the Virtual operator.

        :param le: The raw original operator.
        """
        self.label_encoder = le


class YTransformerLabelEncoderConverter(_AbstractOperatorConverter):
    """Y Transformer LabelEncoder operator converter."""

    def __init__(self):
        """Construct the Y Transformer LabelEncoder operator converter."""
        type(self).OPERATOR_ALIAS = 'AutoMLYTransLabelEncoder'

    def setup(self):
        """Set up the converter."""
        update_registered_converter(_YTransformLabelEncoder,
                                    YTransformerLabelEncoderConverter.OPERATOR_ALIAS,
                                    YTransformerLabelEncoderConverter._calc_y_trans_labelencoder_output_shapes,
                                    YTransformerLabelEncoderConverter._convert_automl_y_trans_labelencoder)

    @staticmethod
    def _calc_y_trans_labelencoder_output_shapes(operator):
        N = operator.inputs[0].type.shape[0]
        class_labels = operator.raw_operator.classes_
        if all(isinstance(i, np.ndarray) for i in class_labels):
            class_labels = np.concatenate(class_labels)

        if all(isinstance(i, np.ndarray) for i in class_labels):
            class_labels = np.concatenate(class_labels)
        if all(isinstance(i, (six.string_types, six.text_type)) for i in class_labels):
            operator.outputs[0].type = StringTensorType(shape=[N])
        elif all(isinstance(i, (numbers.Real)) for i in class_labels):
            operator.outputs[0].type = FloatTensorType(shape=[N])
        else:
            # For other types we treat the class labels as string.
            operator.outputs[0].type = StringTensorType(shape=[N])

        if len(operator.inputs) > 0:
            operator.outputs[1].type = operator.inputs[1].type

    @staticmethod
    def _convert_automl_y_trans_labelencoder(scope, operator, container):
        op = operator.raw_operator
        op_type = OnnxConvertConstants.LabelEncoder
        attrs = {'name': scope.get_unique_operator_name(op_type)}
        attrs['classes_strings'] = [str(c) for c in op.classes_]
        attrs['default_string'] = '__unknown__'

        # By default this label encoder output is string type, cast to float if needed.
        need_cast = False
        cast_to_type = None
        if isinstance(operator.outputs[0].type, FloatTensorType):
            lbl_out = scope.get_unique_variable_name('lbl_out')
            need_cast = True
            cast_to_type = onnx_proto.TensorProto.FLOAT
        else:
            lbl_out = operator.outputs[0].full_name

        container.add_node(op_type, operator.inputs[0].full_name,
                           lbl_out, op_domain=OnnxConvertConstants.OnnxMLDomain,
                           **attrs)
        if need_cast:
            apply_cast(scope, lbl_out, operator.outputs[0].full_name, container, to=cast_to_type)

        if len(operator.inputs) > 0:
            apply_identity(scope, operator.inputs[1].full_name, operator.outputs[1].full_name, container)
