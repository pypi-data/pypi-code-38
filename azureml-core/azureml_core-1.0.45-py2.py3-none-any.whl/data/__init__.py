# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Contains modules for data related functionality.

It includes Datastore, which stores connection information to an Azure storage service, DataPath, which points
to a location within a datastore, and Dataset, which points to a DataPath and contains transformations applied
to the data.
"""

from azureml._base_sdk_common import __version__ as VERSION

__version__ = VERSION
