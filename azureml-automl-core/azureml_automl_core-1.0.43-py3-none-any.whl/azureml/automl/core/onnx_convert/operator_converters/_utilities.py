# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Util of operator converters."""
from typing import Any, Dict, Optional, List
import numbers
import numpy as np

# -----------------------------------
# Import skl2onnx modules.
import sklearn

import sys
from types import ModuleType


class __DummyClassForSklearn:
    pass


class _SklearnCompatibilityUtil:
    """
    This class is a workaround to unblock the user who is using 0.19.* sklearn versions.

    The reason of this workaround is that the skl2onnx package imports the latest sklearn 0.20.*
    modules and classes directly, and it doesn't provide sklearn 0.19.* backward compatibility.
    Ref: https://github.com/onnx/sklearn-onnx/issues/94
    """

    SKLEARN_INCOMPATIBLE_VER_0_19_1 = '0.19.1'
    SKLEARN_INCOMPATIBLE_VER_0_19_2 = '0.19.2'

    # -------------------
    # Sub module names.
    _M_COMPOSE = 'compose'
    _M_IMPUTE = 'impute'
    _M_PREPROCESSING = 'preprocessing'

    # -------------------
    # Class names.
    # In compose module.
    _C_COLUMN_TRANSFORMER = 'ColumnTransformer'
    # In impute module.
    _C_SIMPLE_IMPUTER = 'SimpleImputer'
    # In preprocess module.
    _C_KBINS_DISCRETIZER = 'KBinsDiscretizer'

    # -------------------
    # Version to array of the sub module names map, for adding modules.
    _sklearn_version_to_new_module_names_map = {
        SKLEARN_INCOMPATIBLE_VER_0_19_1: [_M_COMPOSE, _M_IMPUTE],
        SKLEARN_INCOMPATIBLE_VER_0_19_2: [_M_COMPOSE, _M_IMPUTE]
    }

    # -------------------
    # Version to a map of {sub_module : [class_names]} map, for adding classes.
    _sklearn_ver_to_class_names_in_sub_modules = {
        # The
        SKLEARN_INCOMPATIBLE_VER_0_19_1: [
            # sklearn.compose.ColumnTransformer
            # sklearn.impute.SimpleImputer
            # sklearn.preprocessing.KBinsDiscretizer
            # Compose module.
            {_M_COMPOSE: [_C_COLUMN_TRANSFORMER]},
            # Impute module.
            {_M_IMPUTE: [_C_SIMPLE_IMPUTER]},
            # Preprocess module.
            {_M_PREPROCESSING: [_C_KBINS_DISCRETIZER]}
        ],
        SKLEARN_INCOMPATIBLE_VER_0_19_2: [
            # sklearn.compose.ColumnTransformer
            # sklearn.impute.SimpleImputer
            # sklearn.preprocessing.KBinsDiscretizer
            # Compose module.
            {_M_COMPOSE: [_C_COLUMN_TRANSFORMER]},
            # Impute module.
            {_M_IMPUTE: [_C_SIMPLE_IMPUTER]},
            # Preprocess module.
            {_M_PREPROCESSING: [_C_KBINS_DISCRETIZER]}
        ]
    }


def __add_sub_model_in_sklearn(module_name):
    # Create the module.
    m = ModuleType(module_name, None)
    m.__file__ = module_name + '.py'
    # Register it in sys module, this is needed for import.
    sys.modules['sklearn.' + module_name] = m
    # Add it to sklearn module.
    sklearn.__dict__[module_name] = m
    return m


def __add_class_in_sklearn_sub_module(sub_module_name, class_name):
    sub_module = sklearn.__dict__[sub_module_name]
    if sub_module is None:
        # Ensure the sub module exists, if not, add it.
        sub_module = __add_sub_model_in_sklearn(sub_module_name)
    # Add the class to the sub module.
    sub_module.__dict__[class_name] = __DummyClassForSklearn


def _make_sklearn_compatible_with_skl2onnx():
    """Make the skl2onnx compatible with sklearn specific version.

    It defines sub modules and classes that coming after given specific sklearn package version.
    And those sub modules/classes in sklearn are used in skl2onnx.
    Note. This is safe for the automl package, since we use pinned sklearn version.
    """
    # Get the version of sklearn package that is loaded in runtime.
    import pkg_resources
    sklearn_ver = pkg_resources.get_distribution("scikit_learn").version

    if sklearn_ver == _SklearnCompatibilityUtil.SKLEARN_INCOMPATIBLE_VER_0_19_1 \
            or sklearn_ver == _SklearnCompatibilityUtil.SKLEARN_INCOMPATIBLE_VER_0_19_2:
        # Add sub modules to sklearn, based on this version.
        if sklearn_ver in _SklearnCompatibilityUtil._sklearn_version_to_new_module_names_map:
            sub_modules_to_add = _SklearnCompatibilityUtil._sklearn_version_to_new_module_names_map[sklearn_ver]
            for module_name in sub_modules_to_add:
                __add_sub_model_in_sklearn(module_name)

        # Add classes to sub modules, based on this version.
        if sklearn_ver in _SklearnCompatibilityUtil._sklearn_ver_to_class_names_in_sub_modules:
            mod_to_class_maps = _SklearnCompatibilityUtil._sklearn_ver_to_class_names_in_sub_modules[sklearn_ver]
            for m_to_c_map in mod_to_class_maps:
                for mod_name in m_to_c_map:
                    class_names = m_to_c_map[mod_name]
                    for cls_n in class_names:
                        __add_class_in_sklearn_sub_module(mod_name, cls_n)

        # Import all dummy classes defined above.
        from sklearn.compose import ColumnTransformer
        from sklearn.impute import SimpleImputer
        from sklearn.preprocessing import KBinsDiscretizer


# Based on the sklearn version we are pinning, make sklearn be compatible with
# the skl2onnx package.
_make_sklearn_compatible_with_skl2onnx()

from sklearn.feature_extraction.text import CountVectorizer       # noqa: E402


# ------------------------------------
from ..onnx_convert_constants import OnnxConvertConstants       # noqa: E402

# Import the onnx related packages, only if the python version is less than 3.7.
# The onnx package does not support python 3.7 yet.
if sys.version_info < OnnxConvertConstants.OnnxIncompatiblePythonVersion:
    from skl2onnx.proto import onnx_proto       # noqa: E402
    from skl2onnx.common.data_types import Int64TensorType       # noqa: E402
    from skl2onnx.common.data_types import FloatTensorType       # noqa: E402
    from skl2onnx.common.data_types import StringTensorType       # noqa: E402
    from skl2onnx.common.data_types import DictionaryType       # noqa: E402
    from skl2onnx.common.data_types import SequenceType       # noqa: E402

    from skl2onnx.common._apply_operation import (       # noqa: E402
        apply_cast, apply_identity,
        apply_reshape, apply_mul, apply_sub,
        apply_div)

    from skl2onnx.operator_converters.TextVectorizer import convert_sklearn_text_vectorizer       # noqa: E402

    # -----------------------------------
    # Dependencies for convert the lightgbm.
    from collections import Counter       # noqa: E402
    import copy       # noqa: E402
    import six       # noqa: E402
    import onnxmltools.convert.common.data_types       # noqa: E402
    # -----------------------------------
    # Redefine the onnxmltools data type classes, this is needed to fix issue with onnxmltools.
    onnxmltools.convert.common.data_types.Int64TensorType = Int64TensorType
    onnxmltools.convert.common.data_types.StringTensorType = StringTensorType
    onnxmltools.convert.common.data_types.FloatTensorType = FloatTensorType
    onnxmltools.convert.common.data_types.DictionaryType = DictionaryType
    onnxmltools.convert.common.data_types.SequenceType = SequenceType

    from onnxmltools.convert.lightgbm.operator_converters.LightGbm import convert_lightgbm       # noqa: E402
    from onnxmltools.convert.lightgbm.operator_converters.LightGbm import (       # noqa: E402
        _translate_split_criterion, _create_node_id, _parse_tree_structure, _parse_node)
    from lightgbm import LGBMClassifier       # noqa: E402
    from onnxmltools.convert.common._registration import register_converter       # noqa: E402
    from onnxmltools.convert.common.tree_ensemble import get_default_tree_classifier_attribute_pairs       # noqa: E402


# -----------------------------------
# AutoML modules.
from automl.client.core.common.exceptions import OnnxConvertException       # noqa: E402
from ._abstract_operator_converter import _AbstractOperatorConverter       # noqa: E402


# -----------------------------------
# Check the Python version, now onnx package only supports < 3.7.
def _raise_exception_if_python_ver_doesnot_support_onnx():
    # Now onnx package only supports < 3.7.
    if sys.version_info >= OnnxConvertConstants.OnnxIncompatiblePythonVersion:
        raise OnnxConvertException("The ONNX conversion does not support Python version 3.7, "
                                   "please use lower version of Python to get the ONNX models.")


class OpConverterUtil:
    """Util of operator converters."""

    # The seperator string for cat transformer, used in converting the CountVectorizer,
    # when the number of categories is greater than 2. The purpose is to make the tokenizer
    # return a list containining the original string.
    _COUNT_VECTORIZER_SEPERATOR_FOR_CAT_TRANSFORMER = '_AA51DED7266648A79596883C0B90D67A_'

    @staticmethod
    def _apply_mod(scope, container, var1, var2, result):
        # result = var1 % var2
        # There's no mod op in ONNX[v1.3], mod = v1 - (v2 * (v1/v2)), v1, v2
        # are int vars.
        op_type = OnnxConvertConstants.Div
        div_var = scope.get_unique_variable_name('mod_v1_div_v2')
        attrs = {}    # type: Dict[str, Any]
        container.add_node(op_type, [var1, var2], div_var, op_version=7, **attrs)

        op_type = OnnxConvertConstants.Mul
        v2_mul_v1_div_v2_var = scope.get_unique_variable_name('mod_v2_mul_v1_div_v2_var')
        container.add_node(op_type, [var2, div_var], v2_mul_v1_div_v2_var, op_version=7, **attrs)

        op_type = OnnxConvertConstants.Sub
        container.add_node(op_type, [var1, v2_mul_v1_div_v2_var], result, op_version=7, **attrs)

    @staticmethod
    def _convert_count_vectorizer_wrapper(scope, operator, container):
        raw_op = operator.raw_operator
        tokenizer = raw_op.tokenizer

        # Need to remove the custom tokenizer for the raw op, since skl2onnx doesn't support it.
        if tokenizer is not None:
            # Add an option of seperator string to the container.
            container.options = {CountVectorizer: {
                "sep": [OpConverterUtil._COUNT_VECTORIZER_SEPERATOR_FOR_CAT_TRANSFORMER]}}
            raw_op.tokenizer = None

        # Call the skl2onnx convert method.
        convert_sklearn_text_vectorizer(scope, operator, container)

        if tokenizer is not None:
            # Reset the option in the container and the raw op.
            container.options = None
            raw_op.tokenizer = tokenizer

    # The method for the lightgbm classifier.
    # TODO. This is a workaround, remove this after the onnxmltools changes
    # to seperate the processing of the ZipMap output prob var.
    @staticmethod
    def _convert_lightgbm_classifier_wrapper(scope, operator, container):
        gbm_model = operator.raw_operator
        gbm_text = gbm_model.booster_.dump_model()

        attrs = get_default_tree_classifier_attribute_pairs()
        attrs['name'] = operator.full_name

        # Create different attributes for classifier and regressor, respectively
        if isinstance(gbm_model, LGBMClassifier):
            n_classes = gbm_text['num_class']
            if gbm_model.objective_ == 'multiclass':
                attrs['post_transform'] = 'SOFTMAX'
            else:
                attrs['post_transform'] = 'LOGISTIC'
        else:
            n_classes = 1  # Regressor has only one output variable
            attrs['post_transform'] = 'NONE'
            attrs['n_targets'] = n_classes

        # Use the same algorithm to parse the tree
        for i, tree in enumerate(gbm_text['tree_info']):
            tree_id = i
            class_id = tree_id % n_classes
            learning_rate = 1.  # tree['shrinkage'] --> LightGbm provides figures with it already.
            _parse_tree_structure(tree_id, class_id, learning_rate, tree['tree_structure'], attrs)

        # Sort nodes_* attributes. For one tree, its node indexes should appear in an ascent order
        # in nodes_nodeids. Nodes from a tree with a smaller tree index should appear before trees
        # with larger indexes in nodes_nodeids.
        node_numbers_per_tree = Counter(attrs['nodes_treeids'])
        tree_number = len(node_numbers_per_tree.keys())
        accumulated_node_numbers = [0] * tree_number
        for i in range(1, tree_number):
            accumulated_node_numbers[i] = accumulated_node_numbers[i - 1] + node_numbers_per_tree[i - 1]
        global_node_indexes = []
        for i in range(len(attrs['nodes_nodeids'])):
            tree_id = attrs['nodes_treeids'][i]
            node_id = attrs['nodes_nodeids'][i]
            global_node_indexes.append(accumulated_node_numbers[tree_id] + node_id)
        for k, v in attrs.items():
            if k.startswith('nodes_'):
                merged_indexes = zip(copy.deepcopy(global_node_indexes), v)
                sorted_list = [pair[1] for pair in sorted(merged_indexes, key=lambda x: x[0])]
                attrs[k] = sorted_list

        # Create ONNX object
        # Prepare label information for both of TreeEnsembleClassifier and ZipMap
        class_type = onnx_proto.TensorProto.STRING
        zipmap_attrs = {'name': scope.get_unique_variable_name('ZipMap')}
        class_labels = None     # type: Any
        if all(isinstance(i, (numbers.Real, bool, np.bool_)) for i in gbm_model.classes_):
            class_type = onnx_proto.TensorProto.INT64
            class_labels = [int(i) for i in gbm_model.classes_]
            attrs['classlabels_int64s'] = class_labels
            zipmap_attrs['classlabels_int64s'] = class_labels
        elif all(isinstance(i, (six.text_type, six.string_types)) for i in gbm_model.classes_):
            class_labels = [str(i) for i in gbm_model.classes_]
            attrs['classlabels_strings'] = class_labels
            zipmap_attrs['classlabels_strings'] = class_labels
        else:
            raise ValueError('Only string and integer class labels are allowed')

        # Create tree classifier
        probability_tensor_name = scope.get_unique_variable_name('probability_tensor')
        label_tensor_name = scope.get_unique_variable_name('label_tensor')

        container.add_node('TreeEnsembleClassifier', operator.input_full_names,
                           [label_tensor_name, probability_tensor_name],
                           op_domain='ai.onnx.ml', **attrs)
        prob_tensor = probability_tensor_name

        if gbm_model.boosting_type == 'rf':
            col_index_name = scope.get_unique_variable_name('col_index')
            first_col_name = scope.get_unique_variable_name('first_col')
            zeroth_col_name = scope.get_unique_variable_name('zeroth_col')
            denominator_name = scope.get_unique_variable_name('denominator')
            modified_first_col_name = scope.get_unique_variable_name('modified_first_col')
            unit_float_tensor_name = scope.get_unique_variable_name('unit_float_tensor')
            merged_prob_name = scope.get_unique_variable_name('merged_prob')
            predicted_label_name = scope.get_unique_variable_name('predicted_label')
            classes_name = scope.get_unique_variable_name('classes')
            final_label_name = scope.get_unique_variable_name('final_label')

            container.add_initializer(col_index_name, onnx_proto.TensorProto.INT64, [], [1])
            container.add_initializer(unit_float_tensor_name, onnx_proto.TensorProto.FLOAT, [], [1.0])
            container.add_initializer(denominator_name, onnx_proto.TensorProto.FLOAT, [], [100.0])
            container.add_initializer(classes_name, class_type,
                                      [len(class_labels)], class_labels)

            container.add_node('ArrayFeatureExtractor', [probability_tensor_name, col_index_name],
                               first_col_name, name=scope.get_unique_operator_name('ArrayFeatureExtractor'),
                               op_domain='ai.onnx.ml')
            apply_div(scope, [first_col_name, denominator_name], modified_first_col_name, container, broadcast=1)
            apply_sub(scope, [unit_float_tensor_name, modified_first_col_name],
                      zeroth_col_name, container, broadcast=1)
            container.add_node('Concat', [zeroth_col_name, modified_first_col_name],
                               merged_prob_name, name=scope.get_unique_operator_name('Concat'), axis=1)
            container.add_node('ArgMax', merged_prob_name,
                               predicted_label_name, name=scope.get_unique_operator_name('ArgMax'), axis=1)
            container.add_node('ArrayFeatureExtractor', [classes_name, predicted_label_name], final_label_name,
                               name=scope.get_unique_operator_name('ArrayFeatureExtractor'), op_domain='ai.onnx.ml')
            apply_reshape(scope, final_label_name, operator.outputs[0].full_name, container, desired_shape=[-1, ])
            prob_tensor = merged_prob_name
        else:
            container.add_node('Identity', label_tensor_name, operator.outputs[0].full_name)

        apply_identity(scope, prob_tensor, operator.outputs[1].full_name, container)
