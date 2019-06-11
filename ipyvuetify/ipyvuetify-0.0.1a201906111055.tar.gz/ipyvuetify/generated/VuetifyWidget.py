from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from ipywidgets import DOMWidget
from ipywidgets.widgets.widget import widget_serialization
from ..Events import Events


class VuetifyWidget(DOMWidget, Events):

    _model_name = Unicode('VuetifyWidgetModel').tag(sync=True)

    _view_name = Unicode('VuetifyView').tag(sync=True)

    _view_module = Unicode('jupyter-vuetify').tag(sync=True)

    _model_module = Unicode('jupyter-vuetify').tag(sync=True)

    _view_module_version = Unicode('0.1.0').tag(sync=True)

    _model_module_version = Unicode('0.1.0').tag(sync=True)

    _metadata = Dict(default_value=None, allow_none=True).tag(sync=True)

    children = List(Union([
        Instance(DOMWidget),
        Unicode()
    ], default_value=None)).tag(sync=True, **widget_serialization)

    slot = Unicode(None, allow_none=True).tag(sync=True)

    _events = List(Unicode(), default_value=None, allow_none=True).tag(sync=True)

    v_model = Any('!!disabled!!', allow_none=True).tag(sync=True)

    style_ = Unicode(None, allow_none=True).tag(sync=True)

    class_ = Unicode(None, allow_none=True).tag(sync=True)


__all__ = ['VuetifyWidget']
