# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml.widgets._universal_widgets import _RunWidgetBase


class _HyperDriveWidget(_RunWidgetBase):
    """Hyperdrive widget object."""

    runType = "HyperDrive"
