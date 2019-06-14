# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from ipywidgets import register as register_widget
from traitlets import Unicode
from azureml.widgets._widgets import _RunWidgetBase


@register_widget
class _AutoMLWidget(_RunWidgetBase):
    """AutoML Jupyter Widget."""

    _view_name = Unicode('ShowAutoMLRunsView').tag(sync=True)
    _model_name = Unicode('ShowAutoMLRunsModel').tag(sync=True)
