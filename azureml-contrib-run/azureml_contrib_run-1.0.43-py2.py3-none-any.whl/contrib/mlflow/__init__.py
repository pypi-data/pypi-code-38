# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Deprecated: Please use azureml-mlflow instead. Will be removed soon."""

import logging

from azureml.mlflow import get_portal_url, register_model
from azureml.mlflow._version import VERSION

logger = logging.getLogger(__name__)

__version__ = VERSION

__all__ = ["get_portal_url", "register_model"]

logger.warning("Deprecated, please use the azureml-mlflow package instead.")
logger.warning("Deprecated, will no longer be updated in upcoming releases.")
