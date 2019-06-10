# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Package containing modules used in automated machine learning.

Included classes provide resources for configuring, managing pipelines, and examining run output
for automated machine learning experiments.

For more information on automated machine learning, please see 
https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-automated-ml

To define a reusable machine learning workflow for automated machine learning, you may use
:class:`azureml.train.automl.AutoMLStep` to create a
:class:`azureml.pipeline.core.pipeline.Pipeline`.
"""
import azureml.automl.core
from automl.client.core.common.utilities import extract_user_data, get_sdk_dependencies
from azureml.automl.core import _backward_compatible

import warnings
with warnings.catch_warnings():
    # Suppress the warnings at the import phase.
    warnings.simplefilter("ignore")
    from .automl import fit_pipeline
    from .automlconfig import AutoMLConfig
    from .automl_step import AutoMLStep, AutoMLStepRun

__all__ = [
    'AutoMLConfig',
    'AutoMLStep',
    'AutoMLStepRun',
    'fit_pipeline',
    'extract_user_data',
    'get_sdk_dependencies']

for m in _backward_compatible.PackageMappings:
    m.backward_compatible_import_module()

try:
    from ._version import ver as VERSION
    __version__ = VERSION
except ImportError:
    VERSION = '0.0.0+dev'
    __version__ = VERSION
