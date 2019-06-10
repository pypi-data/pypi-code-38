# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from ipywidgets import register as register_widget
from traitlets import Unicode
from azureml.widgets._widgets import _RunWidgetBase


@register_widget
class _HyperDriveWidget(_RunWidgetBase):
    """HyperDrive Jupyter Widget."""

    _view_name = Unicode('ShowHyperDriveRunsView').tag(sync=True)
    _model_name = Unicode('ShowHyperDriveRunsModel').tag(sync=True)
