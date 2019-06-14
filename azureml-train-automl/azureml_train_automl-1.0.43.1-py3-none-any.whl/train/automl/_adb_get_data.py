# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from azureml.automl.core import dataprep_utilities
from azureml.automl.core import training_utilities


class _input_data_model(object):
    def __init__(self, data_dictionary):
        if data_dictionary is None:
            data_dictionary = {}
        self.X = data_dictionary.get('X', None)
        self.y = data_dictionary.get('y', None)
        self.X_valid = data_dictionary.get('X_valid', None)
        self.y_valid = data_dictionary.get('y_valid', None)
        self.sample_weight = data_dictionary.get('sample_weight', None)
        self.sample_weight_valid = data_dictionary.get('sample_weight_valid', None)
        self.cv_splits_indices = data_dictionary.get('cv_splits_indices', None)
        self.x_raw_column_names = data_dictionary.get('x_raw_column_names', None)


def _none_log_message(message, logging_level=logging.DEBUG):
    pass


def get_input_datamodel_from_dataprep_json(dataprep_json,
                                           log_message=_none_log_message,
                                           automl_settings=None,
                                           logger=None):
    """
    Convert dataprep data from json to datamodel.

    :param dataprep_json: The dataprep object in json format.
    :return: The dataprep object in datamodel format.
    """
    try:
        log_message("getting input data from dataprep json...")
        if dataprep_json is None:
            raise ValueError("dataprep_json is None")
        data_dictionary = dataprep_utilities.load_dataflows_from_json(
            dataprep_json)
        if data_dictionary is None:
            raise ValueError("data_dictionary is None")

        cv_splits_indices = []
        cv_splits_indices_key = "cv_splits_indices"
        new_dictionary = {}
        for key in data_dictionary:
            if cv_splits_indices_key in key:
                cv_splits_indices.append(data_dictionary[key])
            else:
                new_dictionary[key] = data_dictionary[key]

        new_dictionary[cv_splits_indices_key] = cv_splits_indices if cv_splits_indices else None
        new_dictionary['is_adb_run'] = True
        new_dictionary['automl_settings'] = automl_settings
        new_dictionary['logger'] = logger
        return _input_data_model(training_utilities.format_training_data(**new_dictionary))
    except Exception as e:
        log_message(message="Error from getting input data from dataprep json: {0} {1}".format(e.__class__, e),
                    logging_level=logging.ERROR)
        raise
