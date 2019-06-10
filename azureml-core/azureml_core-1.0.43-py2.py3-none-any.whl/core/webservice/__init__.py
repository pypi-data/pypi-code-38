# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""This package contains classes used to manage Webservice objects within Azure Machine Learning service."""

from azureml._base_sdk_common import __version__ as VERSION
from .webservice import Webservice
from .aci import AciWebservice
from .aks import AksWebservice
from .local import LocalWebservice
from .unknown_webservice import UnknownWebservice


__version__ = VERSION

__all__ = [
    'Webservice',
    'AciWebservice',
    'AksWebservice',
    'LocalWebservice',
    'UnknownWebservice'
]
