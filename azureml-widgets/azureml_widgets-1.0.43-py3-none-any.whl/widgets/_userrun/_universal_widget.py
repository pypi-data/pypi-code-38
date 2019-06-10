# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml.widgets._universal_widgets import _RunWidgetBase


class _UserRunWidget(_RunWidgetBase):
    """Single run widget object."""

    runType = "UserRun"
