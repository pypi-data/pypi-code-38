from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class Tabs(VuetifyWidget):

    _model_name = Unicode('TabsModel').tag(sync=True)

    active_nav_item_class = Union([
        Unicode(),
        List(Any()),
        Dict()
    ], default_value=None, allow_none=True).tag(sync=True)

    active_tab_class = Union([
        Unicode(),
        List(Any()),
        Dict()
    ], default_value=None, allow_none=True).tag(sync=True)

    align = Unicode(None, allow_none=True).tag(sync=True)

    bottom = Bool(None, allow_none=True).tag(sync=True)

    card = Bool(None, allow_none=True).tag(sync=True)

    content_class = Union([
        Unicode(),
        List(Any()),
        Dict()
    ], default_value=None, allow_none=True).tag(sync=True)

    end = Bool(None, allow_none=True).tag(sync=True)

    fill = Bool(None, allow_none=True).tag(sync=True)

    id = Unicode(None, allow_none=True).tag(sync=True)

    justified = Bool(None, allow_none=True).tag(sync=True)

    lazy = Bool(None, allow_none=True).tag(sync=True)

    nav_class = Union([
        Unicode(),
        List(Any()),
        Dict()
    ], default_value=None, allow_none=True).tag(sync=True)

    nav_wrapper_class = Union([
        Unicode(),
        List(Any()),
        Dict()
    ], default_value=None, allow_none=True).tag(sync=True)

    no_fade = Bool(None, allow_none=True).tag(sync=True)

    no_key_nav = Bool(None, allow_none=True).tag(sync=True)

    no_nav_style = Bool(None, allow_none=True).tag(sync=True)

    pills = Bool(None, allow_none=True).tag(sync=True)

    small = Bool(None, allow_none=True).tag(sync=True)

    tag = Unicode(None, allow_none=True).tag(sync=True)

    value = Float(None, allow_none=True).tag(sync=True)

    vertical = Bool(None, allow_none=True).tag(sync=True)


__all__ = ['Tabs']
