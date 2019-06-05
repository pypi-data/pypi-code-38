from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class Toast(VuetifyWidget):

    _model_name = Unicode('ToastModel').tag(sync=True)

    append_toast = Bool(None, allow_none=True).tag(sync=True)

    auto_hide_delay = Union([
        Float(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)

    body_class = Union([
        Unicode(),
        Dict(),
        List(Any())
    ], default_value=None, allow_none=True).tag(sync=True)

    header_class = Union([
        Unicode(),
        Dict(),
        List(Any())
    ], default_value=None, allow_none=True).tag(sync=True)

    href = Unicode(None, allow_none=True).tag(sync=True)

    id = Unicode(None, allow_none=True).tag(sync=True)

    is_status = Bool(None, allow_none=True).tag(sync=True)

    no_auto_hide = Bool(None, allow_none=True).tag(sync=True)

    no_close_button = Bool(None, allow_none=True).tag(sync=True)

    no_fade = Bool(None, allow_none=True).tag(sync=True)

    no_hover_pause = Bool(None, allow_none=True).tag(sync=True)

    solid = Bool(None, allow_none=True).tag(sync=True)

    static = Bool(None, allow_none=True).tag(sync=True)

    title = Unicode(None, allow_none=True).tag(sync=True)

    to = Union([
        Unicode(),
        Dict()
    ], default_value=None, allow_none=True).tag(sync=True)

    toast_class = Union([
        Unicode(),
        Dict(),
        List(Any())
    ], default_value=None, allow_none=True).tag(sync=True)

    toaster = Unicode(None, allow_none=True).tag(sync=True)

    variant = Unicode(None, allow_none=True).tag(sync=True)

    visible = Bool(None, allow_none=True).tag(sync=True)


__all__ = ['Toast']
