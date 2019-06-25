# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Cat imputer operator converter."""
import numbers
import numpy as np
import pandas as pd

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
from automl.client.core.common.constants import DatetimeDtype   # noqa: E402
from automl.client.core.common.exceptions import OnnxConvertException    # noqa: E402
from ...featurizer.transformer import CatImputer    # noqa: E402
from ...stats_computation import RawFeatureStats     # noqa: E402
from ._abstract_operator_converter import _AbstractOperatorConverter    # noqa: E402


class CatImputerConverter(_AbstractOperatorConverter):
    """CatImputer operator converter."""

    def __init__(self):
        """Construct the cat imputer op converter."""
        type(self).OPERATOR_ALIAS = 'AutoMLCatImputer'

    def setup(self):
        """Set up the converter."""
        update_registered_converter(CatImputer,
                                    CatImputerConverter.OPERATOR_ALIAS,
                                    CatImputerConverter._calculate_automl_catimputer_output_shapes,
                                    CatImputerConverter._convert_automl_catimputer)

    @staticmethod
    def _calculate_automl_catimputer_output_shapes(operator):
        # All inputs and outputs must be float/int64/string tensor.
        check_input_and_output_numbers(operator, input_count_range=1, output_count_range=1)
        check_input_and_output_types(operator, good_input_types=[
                                     FloatTensorType, Int64TensorType, StringTensorType])
        # N means number of elements in dimension 0 (rows),
        # C means number of elements in dimension 1 (cols).
        # This N and C naming applies to other shape calculator methods.
        N = operator.inputs[0].type.shape[0]
        C = operator.inputs[0].type.shape[1]
        # Output type is same as input.
        operator.outputs[0].type = type(operator.inputs[0].type)([N, C])

    @staticmethod
    def _convert_automl_catimputer(scope, operator, container):
        # -------------------------
        # Step1, get the mask value and !mask value.
        # Mask = isnan(input)
        raw_op = operator.raw_operator
        if len(operator.inputs) != 1:
            raise OnnxConvertException('The number of input is not 1.')

        # Define the node(s) to check if the input is a NaN.
        input_var = operator.inputs[0]
        input_name = input_var.full_name
        mask_variable_name = None
        if type(input_var.type) == FloatTensorType:
            # Use IsNaN to get the mask tensor from float tensor input.
            # This op is only added in default domain, op version 9.
            op_type = OnnxConvertConstants.IsNaN
            mask_variable_name = scope.get_unique_variable_name('mask_of_cat_imputer')
            attrs = {'name': scope.get_unique_operator_name(op_type)}
            container.add_node(op_type, input_name, mask_variable_name, op_version=9, **attrs)
        elif type(input_var.type) == Int64TensorType:
            # Use Equal to get the mask tensor from int64 tensor input.
            mask_var_names_for_int = []

            # For each missing values need to check, create a Equal compare op.
            for i_miss_val, val in enumerate(raw_op._missing_vals):
                if (isinstance(val, float) and np.isnan(val)):
                    continue

                # Put the value we want to check to a tensor.
                missing_value_variable_name = scope.get_unique_variable_name('missing_value_of_catimputer')
                container.add_initializer(missing_value_variable_name, onnx_proto.TensorProto.INT64, [1], [val])

                # Use Equal to compare.
                op_type = OnnxConvertConstants.Equal
                mask_variable_name = scope.get_unique_variable_name('mask_of_int_' + str(i_miss_val))
                attrs = {'name': scope.get_unique_operator_name(op_type)}
                container.add_node(op_type, [input_name, missing_value_variable_name],
                                   mask_variable_name, op_version=7, **attrs)
                mask_var_names_for_int.append(mask_variable_name)

            # Get logical 'Or' of output masks to get final mask value.
            prev_mask_val = mask_var_names_for_int[0]
            for i in range(1, len(mask_var_names_for_int)):
                op_type = OnnxConvertConstants.Or
                cur_mask_val = mask_var_names_for_int[i]
                mask_variable_name = scope.get_unique_variable_name('mask_of_int_combined_' + str(i))
                attrs = {'name': scope.get_unique_operator_name(op_type)}
                container.add_node(op_type, [prev_mask_val, cur_mask_val],
                                   mask_variable_name, op_version=7, **attrs)
                prev_mask_val = mask_variable_name
        elif type(input_var.type) == StringTensorType:
            # Check string value of np.nan, np.NaN, and None.
            # Encode the string into int, invalid/missing string will be mapped
            # to the int value 0, or 1, or 2 (the index in classes_strings array).
            op_type = OnnxConvertConstants.LabelEncoder
            attrs = {'name': scope.get_unique_operator_name(op_type),
                     'default_int64': 1024}
            attrs['classes_strings'] = ['NaN', 'nan', 'None']
            encoded_var = scope.get_unique_variable_name('encoded_var')
            container.add_node(op_type, [input_name], encoded_var,
                               op_domain=OnnxConvertConstants.OnnxMLDomain, **attrs)

            # Cast the encoded int64 tensor to int32 type, since onnxruntime only supports int32.
            encoded_var_i32 = scope.get_unique_variable_name('encoded_var_i32')
            apply_cast(scope, encoded_var, encoded_var_i32, container, to=onnx_proto.TensorProto.INT32)

            # Use Less to compare if encoded int value (which is the found index, or default 1024)
            # is less than 3 (since we have 3 candidate missing values to check).
            num_indices_check_var = scope.get_unique_variable_name('num_indices_check_var')
            container.add_initializer(num_indices_check_var, onnx_proto.TensorProto.INT32, [1], [3])

            op_type = OnnxConvertConstants.Less
            mask_variable_name = scope.get_unique_variable_name('mask_of_string')
            attrs = {'name': scope.get_unique_operator_name(op_type)}
            container.add_node(op_type, [encoded_var_i32, num_indices_check_var],
                               mask_variable_name, op_version=9, **attrs)
        else:
            # Should not go here.
            assert(False)

        # -----------------------
        # Step 2, initialize the fill var.
        # Put the fill value into a tensor.
        fill_value_of_catimputer_name = scope.get_unique_variable_name('fill_value_of_catimputer')
        fill_val = raw_op._fill
        if type(input_var.type) == FloatTensorType:
            tensor_type = onnx_proto.TensorProto.FLOAT
        elif type(input_var.type) == Int64TensorType:
            tensor_type = onnx_proto.TensorProto.FLOAT
            # Currently the Where op only supports the string and float tensor.
            fill_val = fill_val.astype(np.float32)
        elif type(input_var.type) == StringTensorType:
            # We need to convert the fill value to string, it might be other type.
            ser = pd.Series(fill_val)
            fea_stat = RawFeatureStats(ser)
            if fea_stat.is_datetime:
                # Reformat the fill string value if it's a datetime.
                if fea_stat.column_type not in DatetimeDtype.FULL_SET:
                    fill_val = pd.to_datetime(fill_val)
                fill_val = fill_val.strftime('%Y-%m-%d %H:%M:%S')
            fill_val = str(fill_val)
            tensor_type = onnx_proto.TensorProto.STRING
            fill_val = fill_val.encode('utf-8')
        else:
            # Should not go here.
            assert(False)
        container.add_initializer(fill_value_of_catimputer_name, tensor_type, [1], [fill_val])

        # ---------------------
        # Step 3, output with mask and fill
        # Use Where with condition = mask, X = op.fill, Y = input.
        # Where behaves like np.where().  If cond==true then return X else return Y.
        # Ref: https://github.com/onnx/onnx/blob/master/docs/Operators.md#Where
        input_var_of_where = input_name
        output_name = operator.outputs[0].full_name
        if type(input_var.type) == Int64TensorType:
            # Cast the int to float for int type input since onnxruntime only
            # support float/string tensor input types.
            input_float_var = scope.get_unique_variable_name('input_float_var')
            apply_cast(scope, input_name, input_float_var, container, to=onnx_proto.TensorProto.FLOAT)
            input_var_of_where = input_float_var
            # Use temp float output var for Where op.
            output_name = scope.get_unique_variable_name('output_float_var')

        op_type = OnnxConvertConstants.Where
        attrs = {'name': scope.get_unique_operator_name(op_type)}
        container.add_node(op_type, [mask_variable_name, fill_value_of_catimputer_name,
                                     input_var_of_where], output_name, op_version=9, **attrs)

        if type(input_var.type) == Int64TensorType:
            # Cast back the output to int, for the int type input.
            apply_cast(scope, output_name, operator.outputs[0].full_name,
                       container, to=onnx_proto.TensorProto.INT64)
