# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from ipywidgets import register as register_widget
from traitlets import Unicode
from azureml.widgets._widgets import _RunWidgetBase


@register_widget
class _PipelineWidget(_RunWidgetBase):
    """Pipeline run Jupyter Widget."""

    _view_name = Unicode('ShowPipelineRunsView').tag(sync=True)
    _model_name = Unicode('ShowPipelineRunsModel').tag(sync=True)
