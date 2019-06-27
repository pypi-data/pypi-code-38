# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Operator manager of onnx conversion module."""
from typing import Any, Dict, Optional, Tuple
import numbers
import numpy as np
import pandas as pd
import sys

# -----------------------------------
from . import OnnxConvertConstants
from automl.client.core.common.constants import (NumericalDtype, DatetimeDtype, TextOrCategoricalDtype)

# Import the onnx related packages, only if the python version is less than 3.8.
# The onnx package does not support python 3.8 yet.
if sys.version_info < OnnxConvertConstants.OnnxIncompatiblePythonVersion:
    try:
        # Try import onnxruntime.
        import onnxruntime as onnxrt    # noqa: E402
        _onnxrt_present = True
    except ImportError:
        _onnxrt_present = False


class InferenceDataFeedMode:
    """The class for data feed model when do the prediction."""

    # Per record mode.
    RecordMode = 'RecordMode'
    # Batch mode.
    BatchMode = 'BatchMode'


class OnnxInferenceHelper:
    """Helper class for inference with ONNX model."""

    def __init__(self, onnx_model_bytes: Any,
                 onnx_res: Dict[Any, Any],
                 data_feed_mode: str = InferenceDataFeedMode.RecordMode):
        if _onnxrt_present:
            if not data_feed_mode:
                raise ValueError("Invalid data feed mode passed in!")
            if data_feed_mode != InferenceDataFeedMode.RecordMode:
                raise NotImplementedError("The inference helper only supports record data feed mode.")
            self._data_feed_mode = data_feed_mode

            self.inference_session = onnxrt.InferenceSession(onnx_model_bytes)
            raw_to_onnx_column_mapping = onnx_res[OnnxConvertConstants.RawColumnNameToOnnxNameMap]
            self.raw_col_schema = onnx_res[OnnxConvertConstants.InputRawColumnSchema]
            if not raw_to_onnx_column_mapping or not self.raw_col_schema:
                raise ValueError("The onnx resource passed in is invalid."
                                 "Please make sure the x_train data is pandas DataFrame type.")

            self.onnx_to_raw_column_mapping = {}    # type: Dict[Any, Any]
            for (k, v) in raw_to_onnx_column_mapping.items():
                self.onnx_to_raw_column_mapping[v] = k

    def predict(self, X: pd.DataFrame, with_prob: bool = True) -> Tuple[Any, Any]:
        """
        Predict the target using the ONNX model

        :param X: The input data to score.
        :type X: pandas.DataFrame.
        :param with_prob: If returns the probability when the model contains a classifier op.
        :return: A 1-d array of predictions made by the model.
        """
        predicted_labels = None
        predicted_probas = None
        if _onnxrt_present:
            if not isinstance(X, pd.DataFrame):
                raise ValueError('The inference helper only supports the X with pandas DataFrame type.')

            results = []
            results_prob = []

            outputs = self.inference_session.get_outputs()
            if len(outputs) == 1:
                with_prob = False

            label = outputs[0].name
            if with_prob:
                prob_name = outputs[1].name
                output_names = [label, prob_name]
            else:
                output_names = [label]

            for input_feed in self._generate_input_feed(X):
                result = None
                result = self.inference_session.run(output_names, input_feed)

                results.append(result[0])
                if with_prob:
                    if isinstance(result[1][0], dict):
                        result = [result[1][0][key] for key in sorted(result[1][0].keys())]
                    else:
                        result = result[1][0]
                    results_prob.append(result)

            predicted_labels = np.vstack(results).reshape(-1)
            if with_prob:
                predicted_probas = np.vstack(results_prob)

        return predicted_labels, predicted_probas

    def _convert_input_to_onnx_compatible_types(self, X):
        for column in X:
            if column not in self.raw_col_schema:
                # The raw column was dropped by the data transformer.
                continue

            col_type = self.raw_col_schema[column]

            if col_type == NumericalDtype.Floating or col_type == NumericalDtype.MixedIntegerFloat:
                X[column] = X[column].astype(np.float32)
            elif col_type == NumericalDtype.Integer:
                X[column] = X[column].astype(np.int64)
            elif col_type in DatetimeDtype.FULL_SET:
                # Format the datetime to string format 'yyyy-mm-dd HH:MM:SS'
                X[column] = pd.to_datetime(X[column])
                X[column] = X[column].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if not pd.isnull(x) else None)
            elif col_type == TextOrCategoricalDtype.String or col_type == NumericalDtype.MixedInteger or \
                    col_type == OnnxConvertConstants.Boolean or col_type == OnnxConvertConstants.Mixed:
                X[column] = X[column].astype(str)
            else:
                raise ValueError("Unsupported data type [{}] in the raw data.".format(col_type))

        return X

    def _generate_input_feed(self, X):
        # Convert X to a compatible tensor format
        X = self._convert_input_to_onnx_compatible_types(X)

        if self._data_feed_mode == InferenceDataFeedMode.RecordMode:
            # Do the inference by feeding the data record by record.
            # This is a limitation in current onnxmltools/skl2onnx and the onnxruntime.
            # After the limitation is removed, we'll add batch mode and enable it as default.
            for i in range(0, X.shape[0]):
                input_feed = {}

                for _, in_var in enumerate(self.inference_session.get_inputs()):
                    raw_feature_name = self.onnx_to_raw_column_mapping[in_var.name]
                    if X[raw_feature_name].dtype == np.float32 or X[raw_feature_name].dtype == np.int64:
                        input_feed[in_var.name] = X[raw_feature_name].iat[i].reshape(-1)
                    else:
                        input_feed[in_var.name] = (np.array(X[raw_feature_name].iat[i])).reshape(-1)

                yield input_feed
