# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Enable DataDriftDetector detection on Azure ML."""

from .datadriftdetector import DataDriftDetector
from .alert_configuration import AlertConfiguration
from ._datadiff import Metric, MetricType
from azureml._base_sdk_common import __version__ as VERSION
from azureml.core import Dataset
from azureml.contrib.datadrift._dataset_extensions import detect_drift

Dataset.detect_drift = detect_drift

__all__ = ["DataDriftDetector", "Metric", "MetricType", "AlertConfiguration"]
__version__ = VERSION
