# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""HashOneHotVectorizerTransformer operator converter."""
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
from ...featurizer.transformer import HashOneHotVectorizerTransformer    # noqa: E402
from ._abstract_operator_converter import _AbstractOperatorConverter    # noqa: E402
from ._utilities import OpConverterUtil    # noqa: E402


class HashOneHotVectorizerConverter(_AbstractOperatorConverter):
    """HashOneHotVectorizerTransformer operator converter."""

    def __init__(self):
        """Construct the HashOneHotVectorizerTransformer operator converter."""
        type(self).OPERATOR_ALIAS = 'AutoMLHashOneHotVectorizerTransformer'

    def setup(self):
        """Set up the converter."""
        update_registered_converter(HashOneHotVectorizerTransformer,
                                    HashOneHotVectorizerConverter.OPERATOR_ALIAS,
                                    HashOneHotVectorizerConverter._calc_hashonehotvectorizer_output_shapes,
                                    HashOneHotVectorizerConverter._convert_automl_hashonehotvectorizertransformer)

    @staticmethod
    def _calc_hashonehotvectorizer_output_shapes(operator):
        raw_op = operator.raw_operator
        check_input_and_output_numbers(operator, input_count_range=1, output_count_range=1)
        # N means number of elements in dimension 0 (rows),
        # C means number of elements in dimension 1 (cols).
        N = operator.inputs[0].type.shape[0]
        C = raw_op._num_cols
        operator.outputs[0].type.shape = [N, C]

    @staticmethod
    def _convert_automl_hashonehotvectorizertransformer(scope, operator, container):
        # The transformer behaves like the OneHotEncoder.
        # Given X (3,1): ['a', 'b', 'a'],
        # and op._num_cols == pow(2, int(math.log(num_unique_categories, 2)) + 1),
        # which is 4 here,
        # and hash values are calculated as: [0, 3, 0]
        # The computed csr_matrix has shape 3 x 4, with 'True' values at row:
        # [0, 1, 2], col: [0, 3, 0].
        raw_op = operator.raw_operator
        if raw_op._seed is None or raw_op._num_cols is None:
            raise OnnxConvertException('The hash one hot vectorizer transformer has invalid properties.')

        # Transformer code: hash_val = murmurhash3_32(val, self._seed) % self._num_cols
        # Use MurmurHash3 op to get the hash val.
        input_var = operator.inputs[0]
        input_name = input_var.full_name
        op_type = OnnxConvertConstants.MurmurHash3
        hash_variable_name = scope.get_unique_variable_name('hohv_hashed_variable')
        attrs = {'name': scope.get_unique_operator_name(op_type),
                 'seed': raw_op._seed,
                 'positive': 0}
        container.add_node(op_type, input_name, hash_variable_name,
                           op_domain=OnnxConvertConstants.OnnxMSDomain, **attrs)

        # Cast to int type explicitly.
        hash_int64_var = scope.get_unique_variable_name('hohv_hash_int64_var')
        apply_cast(scope, hash_variable_name, hash_int64_var, container, to=onnx_proto.TensorProto.INT64)

        # Mod the num_cols.
        num_cols_var = scope.get_unique_variable_name('hohv_num_cols_var')
        container.add_initializer(num_cols_var, onnx_proto.TensorProto.INT64, [1], [raw_op._num_cols])
        hash_mod_var = scope.get_unique_variable_name('hohv_hash_mod_var')
        OpConverterUtil._apply_mod(scope, container, hash_int64_var, num_cols_var, hash_mod_var)

        # Use the OneHotEncoder to setup the output var, with the hash_mode var used as the input.
        # https://github.com/onnx/onnx/blob/master/docs/Operators-ml.md#ai.onnx.ml.OneHotEncoder
        op_type = OnnxConvertConstants.OneHotEncoder
        output_name = operator.outputs[0].full_name
        attrs = {'name': scope.get_unique_operator_name(op_type),
                 'cats_int64s': [i for i in range(raw_op._num_cols)]}
        container.add_node(op_type, hash_mod_var, output_name, op_domain=OnnxConvertConstants.OnnxMLDomain, **attrs)
