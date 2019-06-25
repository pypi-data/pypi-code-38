# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains core packages, modules and classes for Azure Machine Learning.

Main areas include managing compute targets, creating/managing workspaces and experiments, and submitting/accessing
model runs and run output/logging.
"""
import logging
import pkg_resources

from .workspace import Workspace
from .experiment import Experiment
from .runconfig import RunConfiguration
from .environment import Environment
from .script_run import ScriptRun
from .run import Run, get_run
from .datastore import Datastore
from .script_run_config import ScriptRunConfig
from .compute_target import (
    prepare_compute_target,
    is_compute_target_prepared,
    attach_legacy_compute_target,
    remove_legacy_compute_target)
from .compute import ComputeTarget
from .container_registry import ContainerRegistry
from .model import Model
from .image import Image
from .webservice import Webservice
from .dataset import Dataset

from azureml._logging.debug_mode import diagnostic_log

import azureml._base_sdk_common.user_agent as user_agent
from azureml._base_sdk_common import __version__ as VERSION


module_logger = logging.getLogger(__name__)

__version__ = VERSION

__all__ = [
    "Datastore",
    "Environment",
    "Experiment",
    "Run",
    "RunConfiguration",
    "ScriptRun",
    "ScriptRunConfig",
    "Workspace",
    "prepare_compute_target",
    "is_compute_target_prepared",
    "attach_legacy_compute_target",
    "remove_legacy_compute_target",
    "ComputeTarget",
    "Model",
    "Image",
    "Webservice",
    "diagnostic_log",
    "get_run",
    "ContainerRegistry",
    "Dataset"
]

user_agent.append("azureml-sdk-core", __version__)

RUN_TYPE_PROVIDERS_ENTRYPOINT_KEY = "azureml_run_type_providers"
for entrypoint in pkg_resources.iter_entry_points(RUN_TYPE_PROVIDERS_ENTRYPOINT_KEY):
    try:
        Run.add_type_provider(entrypoint.name, entrypoint.load())
    except Exception as e:
        module_logger.warning("Failure while loading {}. Failed to load entrypoint {} with exception {}.".format(
            RUN_TYPE_PROVIDERS_ENTRYPOINT_KEY, entrypoint, e))
