# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Operator manager of onnx conversion module."""
from typing import Any, Dict
import numbers
import numpy as np
import pandas as pd
import sys

# -----------------------------------
from . import OnnxConvertConstants
# Import the onnx related packages, only if the python version is less than 3.7.
# The onnx package does not support python 3.7 yet.
if sys.version_info < OnnxConvertConstants.OnnxIncompatiblePythonVersion:
    import sklearn
    from sklearn.feature_extraction.text import CountVectorizer

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

    # ----------------
    from skl2onnx.common.shape_calculator import \
        calculate_linear_classifier_output_shapes as s2o_calculate_linear_classifier_output_shapes
    from skl2onnx.shape_calculators.TextVectorizer import calculate_sklearn_text_vectorizer_output_shapes

    # -----------------------------------
    # onnxmltools modules.
    # Redefine the onnxmltools data type classes, this is needed to fix issue in the
    # onnxmltools.
    import onnxmltools.convert.common.data_types
    onnxmltools.convert.common.data_types.Int64TensorType = Int64TensorType
    onnxmltools.convert.common.data_types.StringTensorType = StringTensorType
    onnxmltools.convert.common.data_types.FloatTensorType = FloatTensorType
    onnxmltools.convert.common.data_types.DictionaryType = DictionaryType
    onnxmltools.convert.common.data_types.SequenceType = SequenceType

    from lightgbm import LGBMClassifier, LGBMRegressor       # noqa: E402
    from onnxmltools.convert.lightgbm.operator_converters.LightGbm import convert_lightgbm       # noqa: E402
    from onnxmltools.convert.lightgbm.shape_calculators.Classifier import \
        calculate_linear_classifier_output_shapes as omt_calculate_linear_classifier_output_shapes       # noqa: E402
    from onnxmltools.convert.lightgbm.shape_calculators.Regressor import \
        calculate_linear_regressor_output_shapes       # noqa: E402

    try:
        # Try import xgboost.
        from xgboost import XGBClassifier, XGBRegressor       # noqa: E402
        from onnxmltools.convert.xgboost.operator_converters.XGBoost import convert_xgboost       # noqa: E402
        from onnxmltools.convert.xgboost.shape_calculators.Classifier import \
            calculate_xgboost_classifier_output_shapes       # noqa: E402
        _xgboost_present = True
    except ImportError:
        _xgboost_present = False


# -----------------------------------
# AutoML modules.
from automl.client.core.common.exceptions import OnnxConvertException       # noqa: E402

# Model wrappers.
from automl.client.core.common.model_wrappers import _AbstractModelWrapper       # noqa: E402
from automl.client.core.common.model_wrappers import PipelineWithYTransformations       # noqa: E402
from automl.client.core.common.model_wrappers import PreFittedSoftVotingClassifier       # noqa: E402
from automl.client.core.common.model_wrappers import PreFittedSoftVotingRegressor       # noqa: E402
# Transformers.

# Onnx converter modules.
from .operator_converters import _AbstractOperatorConverter   # noqa: E402
from .operator_converters import CatImputerConverter       # noqa: E402
from .operator_converters import HashOneHotVectorizerConverter   # noqa: E402
from .operator_converters import ImputationMarkerConverter    # noqa: E402
from .operator_converters import LaggingTransformerConverter   # noqa: E402
from .operator_converters import \
    StringCastTransformerConverter       # noqa: E402
from .operator_converters import DatetimeTransformerConverter    # noqa: E402

from .operator_converters import \
    DataTransformerFeatureConcatenatorConverter       # noqa: E402

from .operator_converters import \
    YTransformerLabelEncoderConverter       # noqa: E402
from .operator_converters import \
    PrefittedVotingClassifierConverter       # noqa: E402
from .operator_converters import \
    PrefittedVotingRegressorConverter       # noqa: E402

from .operator_converters import OpConverterUtil       # noqa: E402


# ----------------------------------------------------------------
# The operator converter manager class.
# ----------------------------------------------------------------
class OperatorConverterManager:
    """
    The operator converter manager class.

    The central place to hold all the operator converters.
    It will create and register default converters, upper level
    code can also register custom op converters.

    When a converter is registered, it will be setuped, the operator
    classes are responsible of initialize their shape calculator and
    converter methods to the dependent component in skl2onnx package.
    """

    def __init__(self):
        """Construct the operator converter manager."""
        self.inited = False
        # Operator converter registry.
        self.op_converters = {}     # type: Dict[str, _AbstractOperatorConverter]

    def initialize(self):
        """
        Initialize the operator manager.

        This will register the default AutoML operator converters, and the operator
        converters for other packages, e.g. lightgbm.
        """
        if not self.inited:
            # Register AutoML shape calculators and converters.
            self._setup_default_operator_converters()
            # Register default shape calculators and converters for other packages.
            self._register_converter_for_count_vectorizer()
            self._register_default_converters_for_lightgbm()
            self._register_default_converters_for_xgboost()

            self.inited = True

    def register_op_converter(self, converter, force_overwrite=False):
        """Register an operator converter."""
        alias = converter.get_alias()
        if alias in self.op_converters and not force_overwrite:
            # By default we don't allow register same alias converter.
            raise OnnxConvertException('The operator converter {0} has already been registered.'
                                       .format(alias))
        converter.setup()
        self.op_converters[alias] = converter

    def _setup_default_operator_converters(self):
        # Register AutoML operator converters.
        # -----------------------
        # Transformers.
        self.register_op_converter(CatImputerConverter())
        self.register_op_converter(HashOneHotVectorizerConverter())
        self.register_op_converter(ImputationMarkerConverter())
        self.register_op_converter(LaggingTransformerConverter())
        self.register_op_converter(StringCastTransformerConverter())
        self.register_op_converter(DatetimeTransformerConverter())

        self.register_op_converter(DataTransformerFeatureConcatenatorConverter())

        # -----------------------
        # The Y transformers.
        self.register_op_converter(YTransformerLabelEncoderConverter())

        # -----------------------
        # The Ensemble estimators.
        self.register_op_converter(PrefittedVotingClassifierConverter())
        self.register_op_converter(PrefittedVotingRegressorConverter())

    def _register_converter_for_count_vectorizer(self):
        update_registered_converter(CountVectorizer,
                                    OnnxConvertConstants.SklearnCountVectorizer,
                                    calculate_sklearn_text_vectorizer_output_shapes,
                                    OpConverterUtil._convert_count_vectorizer_wrapper)

    def _register_default_converters_for_lightgbm(self):
        # Update the lightgbm converters.

        # We use onnxmltools shape calculator and converter for light gbm.
        # Note, this calculator/converter will generate the Sequence type ZipMap probability
        # output var directly within convert method.
        update_registered_converter(LGBMClassifier,
                                    OnnxConvertConstants.LightGbmLGBMClassifier,
                                    s2o_calculate_linear_classifier_output_shapes,
                                    OpConverterUtil._convert_lightgbm_classifier_wrapper)
        update_registered_converter(LGBMRegressor,
                                    OnnxConvertConstants.LightGbmLGBMRegressor,
                                    calculate_linear_regressor_output_shapes,
                                    convert_lightgbm)

    def _register_lightgbm_converter_for_ensemble_conversion(self):
        # For the lightgbm classifier object that are ensembled in the votingclassifier,
        # we will use the skl2onnx shape calculator, and use our own wrapper shape convert
        # and parse method. These ones can produce tensor type probability vars.
        # This is needed since the prob var needs to be further processed in the ensemble model.
        # And there's no ONNX op that can take an Sequence type input.
        update_registered_converter(LGBMClassifier,
                                    OnnxConvertConstants.LightGbmLGBMClassifier,
                                    s2o_calculate_linear_classifier_output_shapes,
                                    OpConverterUtil._convert_lightgbm_classifier_wrapper)

    def _register_default_converters_for_xgboost(self):
        # Update the xgboost converters.
        if _xgboost_present:
            update_registered_converter(XGBClassifier,
                                        OnnxConvertConstants.XGBClassifier,
                                        calculate_xgboost_classifier_output_shapes,
                                        convert_xgboost)
            update_registered_converter(XGBRegressor,
                                        OnnxConvertConstants.XGBRegressor,
                                        calculate_linear_regressor_output_shapes,
                                        convert_xgboost)
