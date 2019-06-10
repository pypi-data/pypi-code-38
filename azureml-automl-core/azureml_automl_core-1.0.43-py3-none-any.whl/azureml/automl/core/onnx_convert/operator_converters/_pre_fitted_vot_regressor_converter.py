# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""PrefittedVottingRegressor virtual operator converter."""
import numbers
import numpy as np


import sys
from ..onnx_convert_constants import OnnxConvertConstants

# Import the onnx related packages, only if the python version is less than 3.7.
# The onnx package does not support python 3.7 yet.
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


class _VirtualPrefittedVotingRegressor:
    """The Virtual operator used by convert the ensemble votting regressor."""

    def __init__(self, raw_op):
        """
        Construct the PrefittedVottingClassifier virtual operator.

        The raw operator holds the actual PreFittedSoftVotingRegressor object.
        It will be used in convert method
        to convert the estimator operation into ONNX ops.
        :param raw_op: The raw original operator.
        """
        self.raw_operator = raw_op


class PrefittedVotingRegressorConverter(_AbstractOperatorConverter):
    """PrefittedVottingRegressor virtual operator converter."""

    def __init__(self):
        """Construct the PrefittedVottingRegressor virtual operator converter."""
        type(self).OPERATOR_ALIAS = 'AutoMLPrefittedVottingRegressor'

    def setup(self):
        """Set up the converter."""
        update_registered_converter(_VirtualPrefittedVotingRegressor,
                                    PrefittedVotingRegressorConverter.OPERATOR_ALIAS,
                                    PrefittedVotingRegressorConverter._calc_prefitted_vottingregressor_ot_shapes,
                                    PrefittedVotingRegressorConverter._convert_prefitted_votting_regressor)

    @staticmethod
    def _calc_prefitted_vottingregressor_ot_shapes(operator):
        check_input_and_output_types(operator, good_input_types=[FloatTensorType, Int64TensorType])
        N = operator.inputs[0].type.shape[0]
        operator.outputs[0].type = FloatTensorType([N, 1])

    @staticmethod
    def _convert_prefitted_votting_regressor(scope, operator, container):
        op = operator.raw_operator
        variable_names = [inp.full_name for inp in operator.inputs]
        num_estimators = len(variable_names)

        weighted_vars = []
        # Handle weights, for each var tensor, multiply it by a weight value.
        if op.weights is not None:
            weights = (op.weights if isinstance(op.weights, list)
                       else op.weights.flatten().tolist())
            # Number of weight values for each estimator.
            num_weights = len(weights)

            alpha = num_estimators * 1.0 / sum(weights)

            for idx_est, var_nm in enumerate(variable_names):
                w_value = 0.0
                if idx_est < num_weights:
                    # This should always be true, one estimator has one weight value.
                    # But we protect the overflow.
                    w_value = weights[idx_est]
                w_value = w_value * alpha

                # Apply a scaler to this estimator's output values.
                op_type = OnnxConvertConstants.Scaler
                weighted_variable_name = scope.get_unique_variable_name('weighted_variable_' + str(idx_est))
                scaler_attrs = {
                    'name': scope.get_unique_operator_name(op_type),
                    'scale': [w_value],
                    'offset': [0.]
                }
                container.add_node(op_type, var_nm, weighted_variable_name, op_domain='ai.onnx.ml', **scaler_attrs)

                weighted_vars.append(weighted_variable_name)
            variable_names = weighted_vars

        # Concat output or weighted output tensors of each estimator along column axis.
        op_type = OnnxConvertConstants.Concat
        concat_estimators = scope.get_unique_variable_name('concat_estimators')
        attrs = {'name': scope.get_unique_operator_name(op_type), 'axis': 1}
        container.add_node(op_type, variable_names, [concat_estimators], op_domain='', op_version=4, **attrs)

        # Calculate the weighted average output values along axis 1 (column).
        if op.voting == 'hard':
            avg_op_name = OnnxConvertConstants.ReduceMax
        elif op.voting == 'soft':
            avg_op_name = OnnxConvertConstants.ReduceMean
        else:
            raise OnnxConvertException("Unuspported voting kind '{}'.".format(op.voting))
        if op.flatten_transform not in (False, None):
            raise OnnxConvertException("flatten_transform==True is not implemented yet.")

        attrs = {'name': scope.get_unique_operator_name(avg_op_name), 'keepdims': 0, 'axes': [1]}
        container.add_node(avg_op_name, concat_estimators, operator.outputs[0].full_name, **attrs)
