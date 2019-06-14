# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Auto ML common logging module."""
from typing import Optional
import logging

from automl.client.core.common.activity_logger import TelemetryActivityLogger
from azureml.telemetry import AML_INTERNAL_LOGGER_NAMESPACE, get_telemetry_log_handler
from ._azureautomlsettings import AzureAutoMLSettings
from .constants import ComputeTargets

TELEMETRY_AUTOML_COMPONENT_KEY = 'automl'


def get_logger(
    log_file_name: Optional[str] = None,
    verbosity: int = logging.DEBUG,
    automl_settings: Optional[AzureAutoMLSettings] = None
) -> TelemetryActivityLogger:
    """
    Create the logger with telemetry hook.

    :param log_file_name: log file name
    :param verbosity: logging verbosity
    :param automl_settings: the AutoML settings object
    :return logger if log file name is provided otherwise null logger
    :rtype
    """
    telemetry_handler = get_telemetry_log_handler(component_name=TELEMETRY_AUTOML_COMPONENT_KEY)
    try:
        from automl.client.core.common import __version__ as CC_VERSION
        common_core_version = CC_VERSION    # type: Optional[str]
    except Exception:
        common_core_version = None
    try:
        from azureml.train.automl import __version__ as SDK_VERSION
        aml_sdk_version = SDK_VERSION    # type: Optional[str]
    except Exception:
        aml_sdk_version = None

    custom_dimensions = {
        "automl_client": "azureml",
        "common_core_version": common_core_version,
        "automl_sdk_version": aml_sdk_version
    }
    if automl_settings is not None:
        if automl_settings.is_timeseries:
            task_type = "forecasting"
        else:
            task_type = automl_settings.task_type
        if automl_settings.compute_target in (ComputeTargets.LOCAL, ComputeTargets.AMLCOMPUTE):
            compute_target = automl_settings.compute_target
        elif automl_settings.spark_service == 'adb':
            compute_target = 'adb'
        else:
            compute_target = 'remote'
        custom_dimensions.update(
            {
                "experiment_id": automl_settings.name,
                "task_type": task_type,
                "compute_target": compute_target,
                "subscription_id": automl_settings.subscription_id,
                "region": automl_settings.region
            }
        )
    logger = TelemetryActivityLogger(
        namespace=AML_INTERNAL_LOGGER_NAMESPACE,
        filename=log_file_name,
        verbosity=verbosity,
        extra_handlers=[telemetry_handler],
        custom_dimensions=custom_dimensions)
    return logger
