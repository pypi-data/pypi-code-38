# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""DatetimeFeatureTransformer operator converter."""
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
    from skl2onnx.common.utils_classifier import _finalize_converter_classes
    from skl2onnx.operator_converters.common import convert_integer_to_float
    from skl2onnx import update_registered_converter

# AutoML modules.
from automl.client.core.common.exceptions import OnnxConvertException    # noqa: E402
from ...featurizer.transformer import DateTimeFeaturesTransformer    # noqa: E402
from ._abstract_operator_converter import _AbstractOperatorConverter    # noqa: E402

from ._utilities import OpConverterUtil       # noqa: E402


class DatetimeTransformerConverter(_AbstractOperatorConverter):
    """DatetimeFeatureTransformer op converter."""

    def __init__(self):
        """Construct the DatetimeFeatureTransformer op converter."""
        type(self).OPERATOR_ALIAS = 'AutoMLDateTimeFeaturesTransformer'

    def setup(self):
        """Set up the converter."""
        update_registered_converter(DateTimeFeaturesTransformer,
                                    DatetimeTransformerConverter.OPERATOR_ALIAS,
                                    DatetimeTransformerConverter._calculate_automl_datetimetransformer_output_shapes,
                                    DatetimeTransformerConverter._convert_automl_datetimetransformer)

    @staticmethod
    def _calculate_automl_datetimetransformer_output_shapes(operator):
        # All inputs must be string.
        check_input_and_output_types(operator, good_input_types=[StringTensorType])
        N = operator.inputs[0].type.shape[0]
        # The output has 10 columns, this is a fixed number.
        C = 10
        operator.outputs[0].type = FloatTensorType([N, C])

    @staticmethod
    def _convert_automl_datetimetransformer(scope, operator, container):
        if len(operator.inputs) != 1:
            raise OnnxConvertException('The number of input is not 1.')

        # ----------------------------------
        # Tokenize the input string tensor.
        input_var = operator.inputs[0]
        input_name = input_var.full_name

        # Put a tensor indicating seperators.
        default_separators = [' ', '-', '/', ':']

        # The tokenizer.
        op_type = OnnxConvertConstants.Tokenizer
        string_tokens_variable_name = scope.get_unique_variable_name('string_tokens_variable')
        attrs = {'name': scope.get_unique_operator_name(op_type),
                 'mark': False,
                 'pad_value': '#',
                 'separators': default_separators,
                 'mincharnum': 1
                 }
        container.add_node(op_type, input_name, string_tokens_variable_name,
                           op_domain=OnnxConvertConstants.OnnxMSDomain, **attrs)

        # ----------------------------------
        # Extract each date/time component from the tensor including all tokens
        # to several string tensors.
        year_int_var_name = DatetimeTransformerConverter._extract_datetime_component(
            scope, container, string_tokens_variable_name, 'year', 0)
        month_int_var_name = DatetimeTransformerConverter._extract_datetime_component(
            scope, container, string_tokens_variable_name, 'month', 1)
        day_int_var_name = DatetimeTransformerConverter._extract_datetime_component(
            scope, container, string_tokens_variable_name, 'day', 2)
        hour_int_var_name = DatetimeTransformerConverter._extract_datetime_component(
            scope, container, string_tokens_variable_name, 'hour', 3)
        minute_int_var_name = DatetimeTransformerConverter._extract_datetime_component(
            scope, container, string_tokens_variable_name, 'minute', 4)
        second_int_var_name = DatetimeTransformerConverter._extract_datetime_component(
            scope, container, string_tokens_variable_name, 'second', 5)

        # ----------------------------------
        # Calculate day-of-year, day-of-week, quarter, day-div-by-seven
        # components based on existing date/time components.
        day_of_weak_var_name = scope.get_unique_variable_name('day_of_weak')
        day_of_year_var_name = scope.get_unique_variable_name('day_of_year')
        quarter_of_year_var_name = scope.get_unique_variable_name('quarter_of_year')
        day_floordiv_seven_var_name = scope.get_unique_variable_name('day_div_seven')

        DatetimeTransformerConverter._setup_day_of_week_nodes(scope,
                                                              container,
                                                              year_int_var_name,
                                                              month_int_var_name,
                                                              day_int_var_name,
                                                              day_of_weak_var_name)
        DatetimeTransformerConverter._setup_day_of_year_nodes(scope,
                                                              container,
                                                              year_int_var_name,
                                                              month_int_var_name,
                                                              day_int_var_name,
                                                              day_of_year_var_name)
        DatetimeTransformerConverter._setup_quarter_nodes(scope,
                                                          container,
                                                          month_int_var_name,
                                                          quarter_of_year_var_name)
        DatetimeTransformerConverter._setup_day_floordiv_by_seven_nodes(scope,
                                                                        container,
                                                                        day_int_var_name,
                                                                        day_floordiv_seven_var_name)

        # ----------------------------------
        # Concat all date/time components into one output tensor, then cast to float tensor.
        op_type = OnnxConvertConstants.Concat
        output_int_var = scope.get_unique_variable_name('output_int_var')
        all_datetime_comp_var_names = [year_int_var_name,
                                       month_int_var_name,
                                       day_int_var_name,
                                       day_of_weak_var_name,
                                       day_of_year_var_name,
                                       quarter_of_year_var_name,
                                       day_floordiv_seven_var_name,
                                       hour_int_var_name,
                                       minute_int_var_name,
                                       second_int_var_name
                                       ]
        attrs = {'name': scope.get_unique_operator_name(op_type), 'axis': 1}
        container.add_node(op_type, all_datetime_comp_var_names, output_int_var, op_version=4, **attrs)
        # Cast to float tensor.
        apply_cast(scope, output_int_var, operator.outputs[0].full_name, container, to=onnx_proto.TensorProto.FLOAT)

    @staticmethod
    def _extract_datetime_component(scope, container, whole_datetime_var_name, component_name, component_index):
        # Put a tensor of the feature index we want to extract.
        index_component_var_name = scope.get_unique_variable_name('datetime_extract_index_' + component_name)
        container.add_initializer(index_component_var_name, onnx_proto.TensorProto.INT64, [1], [component_index])

        # Extract the component feature.
        component_var_name = scope.get_unique_variable_name('extracted_' + component_name)
        extractor_type = OnnxConvertConstants.ArrayFeatureExtractor
        extractor_attrs = {'name': scope.get_unique_operator_name(extractor_type)}
        container.add_node(extractor_type, [whole_datetime_var_name, index_component_var_name],
                           component_var_name, op_domain=OnnxConvertConstants.OnnxMLDomain, **extractor_attrs)

        # Cast the component from string to int.
        comp_int_var_name = scope.get_unique_variable_name(component_var_name + '_int')
        apply_cast(scope, component_var_name, comp_int_var_name, container, to=onnx_proto.TensorProto.INT64)

        # Reshape the tensor, since the extracted tensor has one additional dimension.
        res_var_name = scope.get_unique_variable_name(comp_int_var_name + '_reshaped')
        apply_reshape(scope, comp_int_var_name, res_var_name, container, desired_shape=[-1, 1])

        return res_var_name

    @staticmethod
    def _setup_day_of_week_nodes(scope, container, year_var, month_var, day_var, dow_var):
        # -------------------------------------
        # Use Sakamoto's methods to calculate day of weak.
        # https://en.wikipedia.org/wiki/Determination_of_the_day_of_the_week
        # dayofweek(y, m, d)
        # {
        #     static int t[] = {0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4};
        #     y -= m < 3;
        #     return (y + y/4 - y/100 + y/400 + t[m-1] + d) % 7;
        # }
        # Note, the component (y + y/4 - y/100 + y/400 + t[m-1] + d) value is bigger than python
        # result by 1, need to sub 1 for this, before mod 7.

        # -------------------------------------
        # Init the t tensor.
        t_variable_name = scope.get_unique_variable_name('dow_temp')
        container.add_initializer(t_variable_name, onnx_proto.TensorProto.INT64,
                                  [12], [0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4])

        # -------------------------------------
        # Init virtual year y -= m < 3: y = y - int(less(m, 3)) .
        # The 3 1-d tensor.
        three_variable_name = scope.get_unique_variable_name('dow_three')
        container.add_initializer(three_variable_name, onnx_proto.TensorProto.INT32, [1], [3])
        # Cast month var to int32 since onnxruntime only supports int32.
        month_var_i32 = scope.get_unique_variable_name('month_var_i32')
        apply_cast(scope, month_var, month_var_i32, container, to=onnx_proto.TensorProto.INT32)

        # Bool result of less(m, 3).
        op_type = OnnxConvertConstants.Less
        attrs = {'name': scope.get_unique_operator_name(op_type)}
        less_bool_name = scope.get_unique_variable_name('dow_less_than_3_bool')
        container.add_node(op_type, [month_var_i32, three_variable_name], less_bool_name, op_version=9, **attrs)

        # Cast to int.
        casted_isless_name = scope.get_unique_variable_name('dow_less_than_3_int')
        apply_cast(scope, less_bool_name, casted_isless_name, container, to=onnx_proto.TensorProto.INT64)

        # Get virtual y: y = y - isLess.
        op_type = OnnxConvertConstants.Sub
        attrs = {'name': scope.get_unique_operator_name(op_type)}
        virtual_y_name = scope.get_unique_variable_name('dow_virtual_y')
        container.add_node(op_type, [year_var, casted_isless_name], virtual_y_name, op_version=7, **attrs)

        # -------------------------------------
        # Get components to sum.
        # Get y/4.
        four_var_name = scope.get_unique_variable_name('dow_four')
        container.add_initializer(four_var_name, onnx_proto.TensorProto.INT64, [1], [4])

        op_type = OnnxConvertConstants.Div
        attrs = {'name': scope.get_unique_operator_name(op_type)}
        y_div_four = scope.get_unique_variable_name('dow_y_div_four')
        container.add_node(op_type, [virtual_y_name, four_var_name], y_div_four, op_version=7, **attrs)

        # Get y/100.
        one_hundred_var_name = scope.get_unique_variable_name('dow_one_hundred')
        container.add_initializer(one_hundred_var_name, onnx_proto.TensorProto.INT64, [1], [100])

        op_type = OnnxConvertConstants.Div
        attrs = {'name': scope.get_unique_operator_name(op_type)}
        y_div_one_hundred = scope.get_unique_variable_name('dow_y_div_one_hundred')
        container.add_node(op_type, [virtual_y_name, one_hundred_var_name],
                           y_div_one_hundred, op_version=7, **attrs)

        # Get y/400.
        four_hundred_var_name = scope.get_unique_variable_name('dow_four_hundred')
        container.add_initializer(four_hundred_var_name, onnx_proto.TensorProto.INT64, [1], [400])

        op_type = OnnxConvertConstants.Div
        attrs = {'name': scope.get_unique_operator_name(op_type)}
        y_div_four_hundred = scope.get_unique_variable_name('dow_y_div_four_hundred')
        container.add_node(op_type, [virtual_y_name, four_hundred_var_name],
                           y_div_four_hundred, op_version=7, **attrs)

        # Get m - 1.
        one_var_name = scope.get_unique_variable_name('dow_one')
        container.add_initializer(one_var_name, onnx_proto.TensorProto.INT64, [1], [1])

        op_type = OnnxConvertConstants.Sub
        attrs = {'name': scope.get_unique_operator_name(op_type)}
        m_minus_one_name = scope.get_unique_variable_name('dow_m_minus_one')
        container.add_node(op_type, [month_var, one_var_name], m_minus_one_name, op_version=7, **attrs)

        # Get t[m - 1].  Note that 'm - 1' is within [0, 11], so it can be used
        # as index in the ArrayFeatureExtractor.
        extractor_type = OnnxConvertConstants.ArrayFeatureExtractor
        extracted_t_temp_name = scope.get_unique_variable_name('dow_extracted_t_temp')
        extractor_attrs = {'name': scope.get_unique_operator_name(extractor_type)}
        container.add_node(extractor_type, [t_variable_name, m_minus_one_name],
                           extracted_t_temp_name, op_domain=OnnxConvertConstants.OnnxMLDomain, **extractor_attrs)
        # Reshape to get 2 dimension tensor.
        extracted_t_name = scope.get_unique_variable_name('dow_extracted_t')
        apply_reshape(scope, extracted_t_temp_name, extracted_t_name, container, desired_shape=[-1, 1])

        # -------------------------------------
        # Get sum of (y + y/4 - y/100 + y/400 + t[m-1] + d).
        # Cast each component to float since Sum only supports float.
        virtual_y_f = scope.get_unique_variable_name('dow_virtual_y_f')
        apply_cast(scope, virtual_y_name, virtual_y_f, container, to=onnx_proto.TensorProto.FLOAT)
        y_div_four_f = scope.get_unique_variable_name('dow_y_div_four_f')
        apply_cast(scope, y_div_four, y_div_four_f, container, to=onnx_proto.TensorProto.FLOAT)
        y_div_one_hundred_f = scope.get_unique_variable_name('dow_y_div_one_hundred_f')
        apply_cast(scope, y_div_one_hundred, y_div_one_hundred_f, container, to=onnx_proto.TensorProto.FLOAT)
        y_div_four_hundred_f = scope.get_unique_variable_name('dow_y_div_four_hundred_f')
        apply_cast(scope, y_div_four_hundred, y_div_four_hundred_f, container, to=onnx_proto.TensorProto.FLOAT)
        extracted_t_name_f = scope.get_unique_variable_name('dow_extracted_t_f')
        apply_cast(scope, extracted_t_name, extracted_t_name_f, container, to=onnx_proto.TensorProto.FLOAT)
        day_var_f = scope.get_unique_variable_name('dow_day_var_f')
        apply_cast(scope, day_var, day_var_f, container, to=onnx_proto.TensorProto.FLOAT)

        # Temp: (y + y/4 + y/400 + t[m-1] + d)
        temp_summary_name = scope.get_unique_variable_name('dow_temp_summary')
        op_type = OnnxConvertConstants.Sum
        attrs = {'name': scope.get_unique_operator_name(op_type)}
        sum_vars = [virtual_y_f,    # y
                    y_div_four_f,   # y/4
                    y_div_four_hundred_f,  # y/400
                    extracted_t_name_f,  # t[m-1]
                    day_var_f,  # d
                    ]
        container.add_node(op_type, sum_vars, temp_summary_name, op_version=7, **attrs)

        # Result: Temp - y/100
        op_type = OnnxConvertConstants.Sub
        attrs = {'name': scope.get_unique_operator_name(op_type)}
        summary_name = scope.get_unique_variable_name('dow_summary')
        container.add_node(op_type, [temp_summary_name, y_div_one_hundred_f], summary_name, op_version=7, **attrs)

        # Cast back to int64 and sub 1 to match python result.
        sum_int_tmp = scope.get_unique_variable_name('dow_summary_int_temp')
        apply_cast(scope, summary_name, sum_int_tmp, container, to=onnx_proto.TensorProto.INT64)

        # Sub 1 for the sum result. Get this: sum = (y + y/4 + y/400 + t[m-1] + d) - 1
        sum_int = scope.get_unique_variable_name('dow_summary_int')
        op_type = OnnxConvertConstants.Sub
        attrs = {'name': scope.get_unique_operator_name(op_type)}
        container.add_node(op_type, [sum_int_tmp, one_var_name], sum_int, op_version=7, **attrs)

        # -------------------------------------
        # Final result: (sum % 7).
        seven_var = scope.get_unique_variable_name('dow_seven')
        container.add_initializer(seven_var, onnx_proto.TensorProto.INT64, [1], [7])
        OpConverterUtil._apply_mod(scope, container, sum_int, seven_var, dow_var)

    @staticmethod
    def _setup_day_of_year_nodes(scope, container, year_var, month_var, day_var, dyear_var):
        # Implementation in glibc:
        # https://github.com/lattera/glibc/blob/master/time/mktime.c
        # day_of_year = _mon_yday[_leap_year(y)][m - 1] + d
        # which equals to: day_of_year = _mon_yday[0][m - 1] + _is_leap_year + d
        # _mon_yday[2][13] =
        # {
        #     /* Normal years.  */
        #     { 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365 },
        #     /* Leap years.  */
        #     { 0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366 }
        # }

        # ------------------
        # Init the 2-d tensor for __mon_yday.
        mon_yday_not_leap_var_name = scope.get_unique_variable_name('doy_mon_yday_not_leap')
        container.add_initializer(mon_yday_not_leap_var_name, onnx_proto.TensorProto.INT64, [13],
                                  [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365])

        # ------------------
        # Get if the year is a leap year from _leap_year(y), the result
        # variable is a int64 tensor.
        is_leap_year = scope.get_unique_variable_name('doy_is_leap_year')
        DatetimeTransformerConverter._setup_is_leap_year_nodes(scope, container, year_var, is_leap_year)

        # ------------------
        # Extract from _mon_yday to get: _mon_yday[_leap_year(y)][m - 1].
        # We extract from non _leap_year tensors, get the value, add is_leap_year int value (0 or 1).
        # Get: _mon_yday[non_leap]
        one_var_name = scope.get_unique_variable_name('doy_one')
        container.add_initializer(one_var_name, onnx_proto.TensorProto.INT64, [1], [1])
        op_type = OnnxConvertConstants.Sub
        attrs = {'name': scope.get_unique_operator_name(op_type)}
        m_minus_one_name = scope.get_unique_variable_name('doy_m_minus_one')
        container.add_node(op_type, [month_var, one_var_name], m_minus_one_name, op_version=7, **attrs)

        # Extract not leap year _mon_yday.
        extracted_mon_yday_var_not_leap = scope.get_unique_variable_name('doy_extracted_mon_yday_nl')
        extractor_type = OnnxConvertConstants.ArrayFeatureExtractor
        extractor_attrs = {'name': scope.get_unique_operator_name(extractor_type)}
        container.add_node(extractor_type,
                           [mon_yday_not_leap_var_name, m_minus_one_name],
                           extracted_mon_yday_var_not_leap,
                           op_domain=OnnxConvertConstants.OnnxMLDomain,
                           **extractor_attrs)
        extracted_mon_yday_nl_var = scope.get_unique_variable_name('extracted_mon_yday_nl_var')
        apply_reshape(scope, extracted_mon_yday_var_not_leap,
                      extracted_mon_yday_nl_var, container, desired_shape=[-1, 1])

        # ------------------
        # Get result.
        # Cast to float before sum.
        extracted_mon_yday_var_nl_var_f = scope.get_unique_variable_name('doy_mon_yday_var_nl_var_f')
        apply_cast(scope, extracted_mon_yday_nl_var, extracted_mon_yday_var_nl_var_f,
                   container, to=onnx_proto.TensorProto.FLOAT)
        is_leap_year_f = scope.get_unique_variable_name('doy_is_leap_year_f')
        apply_cast(scope, is_leap_year, is_leap_year_f, container, to=onnx_proto.TensorProto.FLOAT)
        day_var_f = scope.get_unique_variable_name('doy_day_var_f')
        apply_cast(scope, day_var, day_var_f, container, to=onnx_proto.TensorProto.FLOAT)

        # Sum to get result: res = _mon_yday[non_leap] + _is_leap_year + d
        op_type = OnnxConvertConstants.Sum
        attrs = {'name': scope.get_unique_operator_name(op_type)}
        result_f = scope.get_unique_variable_name('doy_result_f')
        container.add_node(op_type, [extracted_mon_yday_var_nl_var_f, is_leap_year_f,
                                     day_var_f], result_f, op_version=7, **attrs)

        # Cast back to int, to the result var.
        apply_cast(scope, result_f, dyear_var, container, to=onnx_proto.TensorProto.INT64)

    @staticmethod
    def _setup_is_leap_year_nodes(scope, container, year_var, result):
        # is_leap = (y % 4 == 0 && y % 100 != 0) || (y % 400 == 0)
        # Setup the constant tensors.
        zero_var_name = scope.get_unique_variable_name('isleap_zero')
        container.add_initializer(zero_var_name, onnx_proto.TensorProto.INT64, [1], [0])
        four_var_name = scope.get_unique_variable_name('isleap_four')
        container.add_initializer(four_var_name, onnx_proto.TensorProto.INT64, [1], [4])
        one_hundred_var_name = scope.get_unique_variable_name('isleap_one_hundred')
        container.add_initializer(one_hundred_var_name, onnx_proto.TensorProto.INT64, [1], [100])
        four_hundred_var_name = scope.get_unique_variable_name('isleap_four_hundred')
        container.add_initializer(four_hundred_var_name, onnx_proto.TensorProto.INT64, [1], [400])

        # Setup nodes for y % 4 == 0.
        y_mod_four_var = scope.get_unique_variable_name('isleap_y_mod_four')
        OpConverterUtil._apply_mod(scope, container, year_var, four_var_name, y_mod_four_var)

        op_type = OnnxConvertConstants.Equal
        attrs = {'name': scope.get_unique_operator_name(op_type)}
        y_mod_four_equal_zero = scope.get_unique_variable_name('isleap_y_mod_four_equal_zero')
        container.add_node(op_type, [y_mod_four_var, zero_var_name], y_mod_four_equal_zero, op_version=7, **attrs)

        # Setup nodes for y % 100 != 0.
        y_mod_one_hundred_var = scope.get_unique_variable_name('isleap_y_mod_one_hundred')
        OpConverterUtil._apply_mod(scope, container, year_var, one_hundred_var_name, y_mod_one_hundred_var)

        op_type = OnnxConvertConstants.Equal
        attrs = {'name': scope.get_unique_operator_name(op_type)}
        y_mod_one_hundred_equal_zero = scope.get_unique_variable_name('isleap_y_mod_one_hundred_equal_zero')
        container.add_node(op_type, [y_mod_one_hundred_var, zero_var_name],
                           y_mod_one_hundred_equal_zero, op_version=7, **attrs)

        # Setup nodes for y % 400 == 0.
        y_mod_four_hundred_var = scope.get_unique_variable_name('isleap_y_mod_four_hundred')
        OpConverterUtil._apply_mod(scope, container, year_var, four_hundred_var_name, y_mod_four_hundred_var)

        op_type = OnnxConvertConstants.Equal
        attrs = {'name': scope.get_unique_operator_name(op_type)}
        y_mod_four_hundred_equal_zero = scope.get_unique_variable_name('isleap_y_mod_four_hundred_equal_zero')
        container.add_node(op_type, [y_mod_four_hundred_var, zero_var_name],
                           y_mod_four_hundred_equal_zero, op_version=7, **attrs)

        # Result of bool: (y % 4 == 0 && y % 100 != 0) || (y % 400 == 0)
        op_type = OnnxConvertConstants.And
        attrs = {'name': scope.get_unique_operator_name(op_type)}
        temp_res_1 = scope.get_unique_variable_name('isleap_temp_res1')
        container.add_node(op_type, [y_mod_four_equal_zero, y_mod_one_hundred_equal_zero],
                           temp_res_1, op_version=7, **attrs)

        op_type = OnnxConvertConstants.Or
        attrs = {'name': scope.get_unique_operator_name(op_type)}
        temp_res_bool = scope.get_unique_variable_name('isleap_temp_res_bool')
        container.add_node(op_type, [temp_res_1, y_mod_four_hundred_equal_zero],
                           temp_res_bool, op_version=7, **attrs)

        # Cast to int64.
        temp_res_int = scope.get_unique_variable_name('isleap_temp_res_int')
        apply_cast(scope, temp_res_bool, temp_res_int, container, to=onnx_proto.TensorProto.INT64)

        # Reshape.
        apply_reshape(scope, temp_res_int, result, container, desired_shape=[-1, 1])

    @staticmethod
    def _setup_quarter_nodes(scope, container, month_var, quarter_var):
        # Quarter = mon / 4 + 1
        one_var_name = scope.get_unique_variable_name('quarter_one')
        container.add_initializer(one_var_name, onnx_proto.TensorProto.FLOAT, [1], [1])
        four_var_name = scope.get_unique_variable_name('quarter_four')
        container.add_initializer(four_var_name, onnx_proto.TensorProto.INT64, [1], [4])

        op_type = OnnxConvertConstants.Div
        attrs = {'name': scope.get_unique_operator_name(op_type)}
        month_div_four = scope.get_unique_variable_name('quarter_month_div_four')
        container.add_node(op_type, [month_var, four_var_name], month_div_four, op_version=7, **attrs)

        # Cast to float to do sum.
        month_div_four_f = scope.get_unique_variable_name('month_div_four_f')
        apply_cast(scope, month_div_four, month_div_four_f, container, to=onnx_proto.TensorProto.FLOAT)

        quarter_var_t = scope.get_unique_variable_name('quarter_var_t')
        op_type = OnnxConvertConstants.Sum
        attrs = {'name': scope.get_unique_operator_name(op_type)}
        container.add_node(op_type, [month_div_four_f, one_var_name], quarter_var_t, op_version=7, **attrs)

        # Cast back to int64
        apply_cast(scope, quarter_var_t, quarter_var, container, to=onnx_proto.TensorProto.INT64)

    @staticmethod
    def _setup_day_floordiv_by_seven_nodes(scope, container, day_var, result):
        # res = (day - 1) // 7 + 1.
        one_var_name = scope.get_unique_variable_name('daydiv7_one')
        container.add_initializer(one_var_name, onnx_proto.TensorProto.INT64, [1], [1])
        seven_var_name = scope.get_unique_variable_name('daydiv7_seven')
        container.add_initializer(seven_var_name, onnx_proto.TensorProto.INT64, [1], [7])

        # Since the input day variable is int, we can simply use int divsion,
        # which eaquals to floor division '//'.
        op_type = OnnxConvertConstants.Sub
        attrs = {'name': scope.get_unique_operator_name(op_type)}
        day_sub_one = scope.get_unique_variable_name('daydiv7_day_sub_one')
        container.add_node(op_type, [day_var, one_var_name], day_sub_one, op_version=7, **attrs)

        op_type = OnnxConvertConstants.Div
        attrs = {'name': scope.get_unique_operator_name(op_type)}
        day_s1_div_seven = scope.get_unique_variable_name('daydiv7_day_s1_div_seven')
        container.add_node(op_type, [day_sub_one, seven_var_name], day_s1_div_seven, op_version=7, **attrs)

        # Cast to float to do sum.
        day_s1_div_seven_f = scope.get_unique_variable_name('day_s1_div_seven_f')
        apply_cast(scope, day_s1_div_seven, day_s1_div_seven_f, container, to=onnx_proto.TensorProto.FLOAT)
        one_var_name_f = scope.get_unique_variable_name('one_var_name_f')
        apply_cast(scope, one_var_name, one_var_name_f, container, to=onnx_proto.TensorProto.FLOAT)

        result_t = scope.get_unique_variable_name('result_t')
        op_type = OnnxConvertConstants.Sum
        attrs = {'name': scope.get_unique_operator_name(op_type)}
        container.add_node(op_type, [day_s1_div_seven_f, one_var_name_f], result_t, op_version=7, **attrs)

        # Cast back to int64
        apply_cast(scope, result_t, result, container, to=onnx_proto.TensorProto.INT64)
