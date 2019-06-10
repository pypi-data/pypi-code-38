# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""PrefittedVottingClassifier virtual operator converter."""
import numbers
import numpy as np
import six

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
    from skl2onnx import update_registered_converter

# AutoML modules.
from automl.client.core.common.exceptions import OnnxConvertException    # noqa: E402
from ._abstract_operator_converter import _AbstractOperatorConverter    # noqa: E402


class _VirtualPrefittedVotingClassifier:
    """The Virtual operator used by convert the ensemble votting classifier."""

    def __init__(self, raw_op):
        """
        Construct the PrefittedVottingClassifier virtual operator.

        The raw operator holds the actual PreFittedSoftVotingClassifier object.
        It will be used in convert method
        to convert the estimator operation into ONNX ops.
        :param raw_op: The raw original operator.
        """
        self.raw_operator = raw_op


class PrefittedVotingClassifierConverter(_AbstractOperatorConverter):
    """PrefittedVottingClassifier virtual operator converter."""

    def __init__(self):
        """Construct the PrefittedVottingClassifier virtual operator converter."""
        type(self).OPERATOR_ALIAS = 'AutoMLPrefittedVottingClassifier'

    def setup(self):
        """Set up the converter."""
        update_registered_converter(_VirtualPrefittedVotingClassifier,
                                    PrefittedVotingClassifierConverter.OPERATOR_ALIAS,
                                    PrefittedVotingClassifierConverter._calc_prefitted_vottingclassifier_ot_shapes,
                                    PrefittedVotingClassifierConverter._convert_prefitted_votting_classifier)

    @staticmethod
    def _calc_prefitted_vottingclassifier_ot_shapes(operator):
        check_input_and_output_types(operator, good_input_types=[FloatTensorType, Int64TensorType])

        N = operator.inputs[0].type.shape[0]
        class_labels = operator.raw_operator.classes_
        number_of_classes = len(class_labels)
        if all(isinstance(i, np.ndarray) for i in class_labels):
            class_labels = np.concatenate(class_labels)

        if all(isinstance(i, (six.string_types, six.text_type)) for i in class_labels):
            operator.outputs[0].type = StringTensorType(shape=[N])
            operator.outputs[1].type = FloatTensorType([N, number_of_classes])
        elif all(isinstance(i, (numbers.Real, bool, np.bool_)) for i in class_labels):
            operator.outputs[0].type = Int64TensorType(shape=[N])
            operator.outputs[1].type = FloatTensorType([N, number_of_classes])
        else:
            raise OnnxConvertException('Unsupported or mixed label types')

    @staticmethod
    def _convert_prefitted_votting_classifier(scope, operator, container):
        op = operator.raw_operator
        n_classes = len(op.classes_)
        probs_names = [inp.full_name for inp in operator.inputs]
        # Number of probability tensors (which is the number of inner estimators).
        num_estimators = len(probs_names)

        weighted_probs = []
        # Handle weights, for each proba tensor, multiply it by a weight value.
        if op.weights is not None:
            weights = (op.weights if isinstance(op.weights, list)
                       else op.weights.flatten().tolist())
            # Number of weight values for each estimator.
            num_weights = len(weights)

            alpha = num_estimators * 1.0 / sum(weights)

            for idx_est, prob_nm in enumerate(probs_names):
                w_value = 0.0
                if idx_est < num_weights:
                    # This should always be true, one estimator has one weight value.
                    # But we protect the overflow.
                    w_value = weights[idx_est]
                w_value = w_value * alpha

                # Apply a scaler to this estimator's prob values.
                op_type = OnnxConvertConstants.Scaler
                weighted_prob_name = scope.get_unique_variable_name('weighted_probability_' + str(idx_est))
                scaler_attrs = {
                    'name': scope.get_unique_operator_name(op_type),
                    'scale': [w_value],
                    'offset': [0.]
                }
                container.add_node(op_type, prob_nm, weighted_prob_name, op_domain='ai.onnx.ml', **scaler_attrs)

                weighted_probs.append(weighted_prob_name)
            probs_names = weighted_probs

        # For each class, extract each column of this class in all estimators.
        # Then concat the columns of each estimator into one tensor along column axis.
        # We will get n_classes tensors, in one tensor, each column hold one estimator's
        # prob value of corresponding class.
        # Each tensor's shape is: N * n_estimators.
        if op.voting == 'hard':
            avg_op_name = OnnxConvertConstants.ReduceMax
        elif op.voting == 'soft':
            avg_op_name = OnnxConvertConstants.ReduceMean
        else:
            raise OnnxConvertException("Unuspported voting kind '{}'.".format(op.voting))
        if op.flatten_transform not in (False, None):
            raise OnnxConvertException("flatten_transform==True is not implemented yet.")

        extractor_type = OnnxConvertConstants.ArrayFeatureExtractor
        all_classes_vars = []
        for idx_cls in range(n_classes):
            extracted_var_of_estimators = []
            # Extract each column of this class, in all estimators.
            for estimator_prob in probs_names:
                index_of_class_var = scope.get_unique_variable_name('index_class_var')
                container.add_initializer(index_of_class_var, onnx_proto.TensorProto.INT64, [1], [idx_cls])

                extracted_col_of_class = scope.get_unique_variable_name('extracted_col_of_class')
                extractor_attrs = {'name': scope.get_unique_operator_name(extractor_type)}
                container.add_node(extractor_type, [estimator_prob, index_of_class_var],
                                   extracted_col_of_class, op_domain='ai.onnx.ml', **extractor_attrs)
                # Reshape to get 2 dimension tensor.
                extracted_col_of_class_t = scope.get_unique_variable_name('extracted_col_of_class_t')
                apply_reshape(scope, extracted_col_of_class, extracted_col_of_class_t,
                              container, desired_shape=[-1, 1])

                extracted_var_of_estimators.append(extracted_col_of_class_t)

            # Concat the vars for each estimator, for this class, along axis 1.
            op_type = OnnxConvertConstants.Concat
            conc_of_class = scope.get_unique_variable_name('conc_of_class')
            attrs = {'name': scope.get_unique_operator_name(op_type), 'axis': 1}
            container.add_node(op_type, extracted_var_of_estimators, [
                               conc_of_class], op_domain='', op_version=4, **attrs)

            # Calculate the weighted average probability values along axis 1 (column) for this class.
            # We will get a N * 1 tensor.
            avg_var_of_class = scope.get_unique_variable_name('avg_var_of_class')
            attrs = {'name': scope.get_unique_operator_name(avg_op_name), 'axes': [1]}
            container.add_node(avg_op_name, conc_of_class, avg_var_of_class, **attrs)

            all_classes_vars.append(avg_var_of_class)

        # Concat the n_classes average tensors along column axis.
        # We'll get a tensor that holds each class'es average prob value in each column,
        # This is the final probability output var, it is a N * n_classes tensor.
        op_type = OnnxConvertConstants.Concat
        conc_of_all_classes_avgs = operator.outputs[1].full_name
        attrs = {'name': scope.get_unique_operator_name(op_type), 'axis': 1}
        container.add_node(op_type, all_classes_vars, [
                           conc_of_all_classes_avgs], op_domain='', op_version=4, **attrs)

        # Get the label var, by getting the index of max average value, then extract
        # the class value of this index.
        idx_of_max_avg_class = scope.get_unique_variable_name('label_name')
        container.add_node('ArgMax', conc_of_all_classes_avgs, idx_of_max_avg_class,
                           name=scope.get_unique_operator_name('ArgMax'), axis=1)
        _finalize_converter_classes(scope, idx_of_max_avg_class,
                                    operator.outputs[0].full_name, container,
                                    op.classes_)
