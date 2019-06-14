# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Widgets classes used by Jupyter notebooks."""
import ipywidgets as widgets
from traitlets import Unicode, Dict, List, Bool
from ._constants import WIDGET_MODULE_NAME


class _DOMWidgetBase(widgets.DOMWidget):
    """Base class for jupyter widget class."""

    _view_module = Unicode(WIDGET_MODULE_NAME).tag(sync=True)
    _model_module = Unicode(WIDGET_MODULE_NAME).tag(sync=True)
    _model_module_version = Unicode("^1.0.0").tag(sync=True)
    _view_module_version = Unicode("^1.0.0").tag(sync=True)
    widget_settings = Dict().tag(sync=True)


class _RunWidgetBase(_DOMWidgetBase):
    """Base class for run widgets."""

    selected_run_id = Unicode().tag(sync=True)
    selected_run_log = Unicode().tag(sync=True)
    run_properties = Dict().tag(sync=True)
    run_logs = Unicode().tag(sync=True)
    run_metrics = List().tag(sync=True)
    run_id = Unicode().tag(sync=True)
    run_arguments = Unicode().tag(sync=True)
    child_runs = List().tag(sync=True)
    child_runs_metrics = Dict().tag(sync=True)
    workbench_uri = Unicode().tag(sync=True)
    error = Unicode(default_value='').tag(sync=True)
    compute_target_status = Dict().tag(sync=True)
    is_finished = Bool(default_value=False).tag(sync=True)
    graph = Dict(default_value={}).tag(sync=True)
