# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Parameter Validator."""

import os
import re
from datetime import datetime

from azureml.contrib.datadrift import alert_configuration
from azureml.core import Workspace

from .._logging._telemetry_logger import _TelemetryLogger

module_logger = _TelemetryLogger.get_telemetry_logger(__name__)
EMAIL_REGEX = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")


class ParameterValidator:
    @staticmethod
    def validate_workspace(input):
        if not isinstance(input, Workspace):
            raise TypeError("workspace must be a Workspace type")
        return input

    @staticmethod
    def validate_model_name(input):
        if not isinstance(input, str):
            raise TypeError("model_name must be a string")
        pattern = r'^([a-zA-Z0-9 ._-]*)$'
        if(re.match(pattern, input) is None):
            raise ValueError("model_name should only contain characters, numbers, "
                             "dash, underscore, dot and whitespace.")
        return input

    @staticmethod
    def validate_model_version(input):
        if not isinstance(input, int) or input <= 0:
            raise TypeError("model_version must be a positive integer")
        return input

    @staticmethod
    def validate_services(input):
        if not isinstance(input, list):
            raise TypeError("services must be a list")
        if not input:
            raise TypeError("services cannot be empty")
        for s in input:
            if not isinstance(s, str):
                raise TypeError("Each service name must be a string")
            pattern = r'^([a-zA-Z0-9 ._-]*)$'
            if (re.match(pattern, s) is None):
                raise ValueError("service name should only contain characters, numbers, "
                                 "dash, underscore, dot and whitespace.")
        return input

    @staticmethod
    def validate_compute_target_name(input, workspace, none_ok=True, not_exist_ok=False):
        if not ((none_ok and input is None) or isinstance(input, str)):
            raise TypeError("compute_target_name must be a string")
        if input is None:
            return input
        if not not_exist_ok and input not in workspace.compute_targets:
            raise KeyError("compute_target with name {} does not exist".format(input))
        if not not_exist_ok and workspace.compute_targets[input]._compute_type is not "AmlCompute":
            raise TypeError("Compute target {} must be an AmlCompute type".format(input))
        if not not_exist_ok and workspace.compute_targets[input].status.provisioning_state.capitalize() != "Succeeded":
            raise TypeError("Compute target {} must be in active state".format(input))
        return input

    @staticmethod
    def validate_frequency(input, none_ok=True, instance_logger=module_logger):
        frequencies = ["Day", "Week", "Month"]
        if not ((none_ok and input is None) or input in frequencies):
            raise TypeError("frequency must one of {}".format(frequencies))
        if not (input is frequencies[0] or input is None):
            instance_logger.warning("Only frequency=Day is supported for now, updating..")
        return frequencies[0]  # TODO: frequencies[0] if input is None else input

    @staticmethod
    def validate_interval(input, none_ok=True, instance_logger=module_logger):
        if not ((none_ok and input is None) or (isinstance(input, int) and input > 0)):
            raise TypeError("interval must be a positive integer")
        if not (input is 1 or input is None):
            instance_logger.warning("Only interval=1 is supported for now, updating..")
        return 1  # TODO: 1 if input is None else input

    @staticmethod
    def validate_datetime(input, name="Input", none_ok=True):
        if not ((none_ok and input is None) or isinstance(input, datetime)):
            raise TypeError("{} must be a datetime".format(name))
        return input

    @staticmethod
    def validate_features(input, none_ok=True):
        if not (none_ok and input is None):
            if not isinstance(input, list):
                raise TypeError("feature_list must be a list")
            for i in input:
                if not isinstance(i, str) or "," in i:
                    raise ValueError("A feature must be a string and cannot contain any commas(,)")
                # not sure if this necessary for feature name check
                pattern = r'^([a-zA-Z0-9 ._-]*)$'
                if (re.match(pattern, i) is None):
                    raise ValueError("feature name should only contain characters, numbers, "
                                     "dash, underscore, dot and whitespace.")
        return input

    @staticmethod
    def validate_alert_configuration(input, none_ok=True):
        if not (none_ok and input is None):
            if not isinstance(input, alert_configuration.AlertConfiguration):
                raise TypeError("alert_config must be of type {}".format(
                    alert_configuration.AlertConfiguration.__module__ +
                    alert_configuration.AlertConfiguration.__name__))
            input.email_addresses = ParameterValidator.validate_email_addresses(input.email_addresses)
        return input

    @staticmethod
    def validate_run_id(input):
        if not isinstance(input, str):
            raise TypeError("run_id must be a string")
        return input

    @staticmethod
    def validate_filepath(input, name="Input", none_ok=True):
        if not ((none_ok and input is None) or isinstance(input, str)):
            raise TypeError("{} must be a datetime".format(name))
        if (input is not None and not os.path.exists(os.path.dirname(input))):
            raise NotADirectoryError("Directory {} does not exist yet.".format(os.path.dirname(input)))
        return input

    @staticmethod
    def is_guid(test_str):
        pattern = r'^([a-zA-Z0-9]{8}-([a-zA-Z0-9]{4}-){3}[a-zA-Z0-9]{12})$'
        matched = re.match(pattern, test_str)
        return (matched is not None)

    @staticmethod
    def validate_drift_threshold(input, none_ok=True):
        if not ((none_ok and input is None) or (isinstance(input, float) and 0 <= input <= 1)):
            raise TypeError("threshold must be a positive float value between 0 and 1")
        return input

    @staticmethod
    def validate_email_addresses(input):
        if not (isinstance(input, list)):
            raise TypeError("email_addresses must be of type list(str)")
        invalid_emails = []
        for m in input:
            match = re.match(EMAIL_REGEX, m)
            if not match:
                invalid_emails.append(m)
        if invalid_emails:
            raise ValueError("Invalid email address format: {}".format(", ".join(invalid_emails)))
        return input
