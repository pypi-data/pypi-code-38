from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class Dropdown(VuetifyWidget):

    _model_name = Unicode('DropdownModel').tag(sync=True)

    boundary = Union([
        Unicode(),
        Dict()
    ], default_value=None, allow_none=True).tag(sync=True)

    disabled = Bool(None, allow_none=True).tag(sync=True)

    dropleft = Bool(None, allow_none=True).tag(sync=True)

    dropright = Bool(None, allow_none=True).tag(sync=True)

    dropup = Bool(None, allow_none=True).tag(sync=True)

    html = Unicode(None, allow_none=True).tag(sync=True)

    id = Unicode(None, allow_none=True).tag(sync=True)

    menu_class = Union([
        Unicode(),
        List(Any())
    ], default_value=None, allow_none=True).tag(sync=True)

    no_caret = Bool(None, allow_none=True).tag(sync=True)

    no_flip = Bool(None, allow_none=True).tag(sync=True)

    offset = Union([
        Float(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)

    popper_opts = Any(None, allow_none=True).tag(sync=True)

    right = Bool(None, allow_none=True).tag(sync=True)

    role = Unicode(None, allow_none=True).tag(sync=True)

    size = Unicode(None, allow_none=True).tag(sync=True)

    split = Bool(None, allow_none=True).tag(sync=True)

    split_href = Unicode(None, allow_none=True).tag(sync=True)

    split_to = Union([
        Unicode(),
        Dict()
    ], default_value=None, allow_none=True).tag(sync=True)

    split_variant = Unicode(None, allow_none=True).tag(sync=True)

    text = Unicode(None, allow_none=True).tag(sync=True)

    toggle_class = Union([
        Unicode(),
        List(Any())
    ], default_value=None, allow_none=True).tag(sync=True)

    toggle_tag = Unicode(None, allow_none=True).tag(sync=True)

    toggle_text = Unicode(None, allow_none=True).tag(sync=True)

    variant = Unicode(None, allow_none=True).tag(sync=True)


__all__ = ['Dropdown']
