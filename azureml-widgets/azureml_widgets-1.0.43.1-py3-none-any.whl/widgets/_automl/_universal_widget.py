# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml.widgets._universal_widgets import _RunWidgetBase


class _AutoMLWidget(_RunWidgetBase):
    """AutoML widget object."""

    runType = "AutoML"
