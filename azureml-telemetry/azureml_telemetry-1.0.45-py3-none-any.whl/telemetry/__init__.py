# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Init for telemetry package."""

import json
import logging
import os

from threading import Lock

AML_INTERNAL_LOGGER_NAMESPACE = "azureml.telemetry"
INSTRUMENTATION_KEY = '625b9182-81ec-41de-adce-183c9489ac1a'

# application insight logger name
LOGGER_NAME = 'ApplicationInsightLogger'
SEND_DIAGNOSTICS_KEY = 'send_diagnostics'
DIAGNOSTICS_VERBOSITY_KEY = 'diagnostics_verbosity'

# app insights logging
telemetry_handler = None

global_diagnostics_properties = {}
write_lock = Lock()


def _get_file_path():
    """Return the telemetry file path.

    :return: telemetry file path
    :rtype: str
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, "telemetry.json")


def _get_raw_config(file_path):
    try:
        with open(file_path, 'rt') as config_file:
            return json.load(config_file)
    except Exception:
        return {}


def set_diagnostics_collection(send_diagnostics=True, verbosity=logging.INFO, reason="", path=None):
    """Enable/disable diagnostics collection.

    :param send_diagnostics: send diagnostics
    :type send_diagnostics: bool
    :param verbosity: diagnostics verbosity
    :type verbosity: logging(const)
    :param reason: reason for enabling diagnostics
    :type reason: str
    :param path: path of the config file
    :type path: str path
    :return: telemetry file path
    :rtype: str
    """
    file_path = _get_file_path() if path is None else path

    try:
        with write_lock:
            config = _get_raw_config(file_path=file_path)
            config[SEND_DIAGNOSTICS_KEY] = send_diagnostics
            config[DIAGNOSTICS_VERBOSITY_KEY] = logging.getLevelName(verbosity)
            with open(file_path, "w+") as config_file:
                json.dump(config, config_file, indent=4)
                if send_diagnostics:
                    print("Turning diagnostics collection on. {}".format(reason))
    except Exception as e:
        print("Could not write the config file to: {}\n{}".format(file_path, str(e)))


def get_diagnostics_collection_info(component_name=None, path=None):
    """Return the current diagnostics collection status.

    :param component_name: component name to retrieve default value
    :param path: path of telemetry settings file
    :return: usage statistics config
    :rtype: dict
    """
    file_path = _get_file_path() if path is None else path

    try:
        config = _get_raw_config(file_path=file_path)
        send_diagnostics = config.get(SEND_DIAGNOSTICS_KEY, False)
        verbosity = config.get(DIAGNOSTICS_VERBOSITY_KEY,
                               logging.getLevelName(logging.NOTSET))

        if send_diagnostics is None and component_name:
            return config.get(component_name), verbosity
        elif send_diagnostics is None:
            return False, verbosity

        if send_diagnostics is True and component_name:
            return config.get(component_name), verbosity
        elif send_diagnostics is True:
            return send_diagnostics, verbosity

    except Exception:
        pass

    return False, logging.getLevelName(logging.NOTSET)


def is_diagnostics_collection_info_available():
    """Check that the diagnostics collection is being set by user."""
    file_path = _get_file_path()
    return os.path.isfile(file_path)


def add_diagnostics_properties(properties):
    """Add additional diagnostics properties.

    :param properties: additional diagnostic properties.
    :type properties: dict
    """
    global global_diagnostics_properties
    global_diagnostics_properties.update(properties)


def set_diagnostics_properties(properties):
    """Set the diagnostics properties.

    :param properties: the diagnostics properties.
    :type properties: dict
    """
    global global_diagnostics_properties
    global_diagnostics_properties.clear()
    global_diagnostics_properties.update(properties)


def get_telemetry_log_handler(instrumentation_key=INSTRUMENTATION_KEY, component_name=None, path=None):
    """Get the telemetry log handler if enabled otherwise return null handler.

    :param instrumentation_key: instrumentation key
    :type instrumentation_key: str
    :param component_name: component name
    :type component_name: str
    :param path: telemetry file with full path
    :type path: str
    :return: telemetry handler if enabled else null log handler
    :rtype: logging.handler
    """
    diagnostics_enabled, verbosity = get_diagnostics_collection_info(component_name=component_name, path=path)

    if diagnostics_enabled:
        global telemetry_handler
        if telemetry_handler is None:
            app_insights_file_logger = logging.getLogger(AML_INTERNAL_LOGGER_NAMESPACE).getChild(__name__)
            app_insights_file_logger.propagate = False
            app_insights_file_logger.setLevel(logging.CRITICAL)

            from azureml.telemetry.logging_handler import get_appinsights_log_handler
            global global_diagnostics_properties
            telemetry_handler = get_appinsights_log_handler(instrumentation_key, app_insights_file_logger,
                                                            properties=global_diagnostics_properties)
            telemetry_handler.setLevel(verbosity)
            return telemetry_handler
        return telemetry_handler

    return logging.NullHandler()


class UserErrorException(Exception):
    """Class for the user exceptions."""

    def __init__(self, exception_message, **kwargs):
        """Initialize the user exception.

        :param exception_message: exception message
        :param kwargs: arguments
        """
        super(UserErrorException, self).__init__(exception_message, **kwargs)
