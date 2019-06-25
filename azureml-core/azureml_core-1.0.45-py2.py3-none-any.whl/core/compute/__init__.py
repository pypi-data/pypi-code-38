# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""This package contains classes used to manage Compute Targets objects within Azure Machine Learning."""

from azureml._base_sdk_common import __version__ as VERSION
from .compute import ComputeTarget
from .aks import AksCompute
from .amlcompute import AmlCompute
from .batch import BatchCompute
from .dsvm import DsvmCompute
from .datafactory import DataFactoryCompute
from .adla import AdlaCompute
from .databricks import DatabricksCompute
from .hdinsight import HDInsightCompute
from .remote import RemoteCompute

__version__ = VERSION

__all__ = [
    'ComputeTarget',
    'AksCompute',
    'AmlCompute',
    'BatchCompute',
    'DsvmCompute',
    'DataFactoryCompute',
    'AdlaCompute',
    'DatabricksCompute',
    'RemoteCompute',
    'HDInsightCompute'
]
