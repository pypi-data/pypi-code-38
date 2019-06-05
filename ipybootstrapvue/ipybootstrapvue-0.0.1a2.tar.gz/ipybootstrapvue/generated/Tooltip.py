from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class Tooltip(VuetifyWidget):

    _model_name = Unicode('TooltipModel').tag(sync=True)

    boundary = Union([
        Unicode(),
        Dict()
    ], default_value=None, allow_none=True).tag(sync=True)

    boundary_padding = Float(None, allow_none=True).tag(sync=True)

    container = Unicode(None, allow_none=True).tag(sync=True)

    delay = Union([
        Float(),
        Dict(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)

    disabled = Bool(None, allow_none=True).tag(sync=True)

    fallback_placement = Union([
        Unicode(),
        List(Any())
    ], default_value=None, allow_none=True).tag(sync=True)

    no_fade = Bool(None, allow_none=True).tag(sync=True)

    offset = Union([
        Float(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)

    placement = Unicode(None, allow_none=True).tag(sync=True)

    show = Bool(None, allow_none=True).tag(sync=True)

    target = Union([
        Unicode(),
        Dict(),
        Dict()
    ], default_value=None, allow_none=True).tag(sync=True)

    title = Unicode(None, allow_none=True).tag(sync=True)

    triggers = Union([
        Unicode(),
        List(Any())
    ], default_value=None, allow_none=True).tag(sync=True)


__all__ = ['Tooltip']
