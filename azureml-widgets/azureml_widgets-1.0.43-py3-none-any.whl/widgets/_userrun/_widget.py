# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from ipywidgets import register as register_widget
from traitlets import Unicode
from azureml.widgets._widgets import _RunWidgetBase


@register_widget
class _UserRunWidget(_RunWidgetBase):
    """Single run Jupyter Widget."""

    _view_name = Unicode('ShowRunDetailsView').tag(sync=True)
    _model_name = Unicode('ShowRunDetailsModel').tag(sync=True)
