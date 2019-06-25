# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility methods for interacting with azureml.dataprep."""
from typing import Any, Dict
import json
import numpy as np

from automl.client.core.common.exceptions import DataException, DataprepException

DATAPREP_INSTALLED = True
try:
    import azureml.dataprep as dprep
except ImportError:
    DATAPREP_INSTALLED = False


__activities_flag__ = 'activities'


def try_retrieve_pandas_dataframe(dataflow):
    """Retreieve pandas dataframe from dataflow and return underlying ndarray.

    Param dataflow: the dataflow to retrieve
    type: azureml.dataprep.Dataflow
    return: the retrieved np.ndarray, or the original dataflow value when it is of incorrect type
    """
    if not is_dataflow(dataflow):
        return dataflow
    try:
        df = dataflow.to_pandas_dataframe()
        return df.values
    except Exception as e:
        raise DataprepException.from_exception(e)


def try_retrieve_pandas_dataframe_adb(dataflow):
    """Retreieve pandas dataframe from dataflow for ADB.

    Param dataflow: the dataflow to retrieve
    type: azureml.dataprep.Dataflow
    return: the retrieved pandas DataFrame, or the original dataflow value when it is of incorrect type
    """
    if not is_dataflow(dataflow):
        return dataflow
    try:
        df = dataflow.to_pandas_dataframe()
        return df
    except Exception as e:
        raise DataprepException.from_exception(e)


def try_retrieve_numpy_array(dataflow):
    """Retreieve numpy array.

    Param dataflow: the single column dataflow to retrieve
    type: azureml.dataprep.Dataflow
    return: the retrieved numpy array, or the original dataflow value when it is of incorrect type
    """
    if not is_dataflow(dataflow):
        return dataflow
    try:
        df = dataflow.to_pandas_dataframe()
        return df[df.columns[-1]].values
    except Exception as e:
        raise DataprepException.from_exception(e)


def try_resolve_cv_splits_indices(cv_splits_indices):
    """Resolve cv splits indices.

    Param cv_splits_indices: the list of dataflow where each represents a set of split indices
    type: list(azureml.dataprep.Dataflow)
    return: the resolved cv_splits_indices, or the original passed in value when it is of incorrect type
    """
    if cv_splits_indices is None:
        return None
    cv_splits_indices_list = []
    for split in cv_splits_indices:
        if not is_dataflow(split):
            return cv_splits_indices
        else:
            is_train_list = try_retrieve_numpy_array(split)
            train_indices = []
            valid_indices = []
            for i in range(len(is_train_list)):
                if is_train_list[i] == 1:
                    train_indices.append(i)
                elif is_train_list[i] == 0:
                    valid_indices.append(i)
            cv_splits_indices_list.append(
                [np.array(train_indices), np.array(valid_indices)])
    return cv_splits_indices_list


def get_dataprep_json(X=None, y=None, sample_weight=None, X_valid=None, y_valid=None,
                      sample_weight_valid=None, cv_splits_indices=None):
    """Get dataprep json.

    :param X: Training features.
    :type X: azureml.dataprep.Dataflow
    :param y: Training labels.
    :type y: azureml.dataprep.Dataflow
    :param sample_weight: Sample weights for training data.
    :type sample_weight: azureml.dataprep.Dataflow
    :param X_valid: validation features.
    :type X_valid: azureml.dataprep.Dataflow
    :param y_valid: validation labels.
    :type y_valid: azureml.dataprep.Dataflow
    :param sample_weight_valid: validation set sample weights.
    :type sample_weight_valid: azureml.dataprep.Dataflow
    :param cv_splits_indices: custom validation splits indices.
    :type cv_splits_indices: azureml.dataprep.Dataflow
    return: JSON string representation of a dict of Dataflows
    """
    dataprep_json = None
    df_value_list = [X, y, sample_weight, X_valid,
                     y_valid, sample_weight_valid, cv_splits_indices]
    if any(var is not None for var in df_value_list):
        def raise_type_error():
            raise DataException("Passing X, y, sample_weight, X_valid, y_valid, sample_weight_valid or "
                                "cv_splits_indices as Pandas or numpy dataframe is only supported for local runs. "
                                "For remote runs, please provide X, y, sample_weight, X_valid, y_valid, "
                                "sample_weight_valid and cv_splits_indices as azureml.dataprep.Dataflow "
                                "objects, or provide a get_data() file instead.")

        dataflow_dict = {
            'X': X,
            'y': y,
            'sample_weight': sample_weight,
            'X_valid': X_valid,
            'y_valid': y_valid,
            'sample_weight_valid': sample_weight_valid
        }
        for i in range(len(cv_splits_indices or [])):
            split = cv_splits_indices[i]
            if not is_dataflow(split):
                raise_type_error()
            else:
                dataflow_dict['cv_splits_indices_{0}'.format(i)] = split
        dataprep_json = save_dataflows_to_json(dataflow_dict)
        if dataprep_json is None:
            raise_type_error()

    return dataprep_json


def save_dataflows_to_json(dataflow_dict):
    """Save dataflows to json.

    Param dataflow_dict: the dict with key as dataflow name and value as dataflow
    type: dict(str, azureml.dataprep.Dataflow)
    return: the JSON string representation of a dict of Dataflows
    """
    dataflow_json_dict = {}     # type: Dict[str, Any]
    for name in dataflow_dict:
        dataflow = dataflow_dict[name]
        if not is_dataflow(dataflow):
            continue
        try:
            # json.dumps(json.loads(...)) to remove newlines and indents
            dataflow_json = json.dumps(json.loads(dataflow.to_json()))
        except Exception as e:
            raise DataprepException.from_exception(e)
        dataflow_json_dict[name] = dataflow_json

    if len(dataflow_json_dict) == 0:
        return None

    dataflow_json_dict[__activities_flag__] = 0  # backward compatible with old Jasmine
    return json.dumps(dataflow_json_dict)


def load_dataflows_from_json(dataprep_json):
    """Load dataflows from json.

    Param dataprep_json: the JSON string representation of a dict of Dataflows
    type: str
    return: a dict with key as dataflow name and value as dataflow, or None if JSON is malformed
    """
    dataflow_json_dict = json.loads(dataprep_json)
    if __activities_flag__ in dataflow_json_dict:
        del dataflow_json_dict[__activities_flag__]  # backward compatible with old Jasmine

    dataflow_dict = {}
    for name in dataflow_json_dict:
        try:
            dataflow = dprep.Dataflow.from_json(dataflow_json_dict[name])
        except Exception as e:
            raise DataprepException.from_exception(e)
        dataflow_dict[name] = dataflow
    return dataflow_dict


def is_dataflow(dataflow):
    """Check if object passed is of type dataflow.

    Param dataflow:
    return: True if dataflow is of type azureml.dataprep.Dataflow
    """
    if not DATAPREP_INSTALLED or not isinstance(dataflow, dprep.Dataflow):
        return False
    return True
