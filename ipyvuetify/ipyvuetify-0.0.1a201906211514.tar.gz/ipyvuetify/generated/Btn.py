from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class Btn(VuetifyWidget):

    _model_name = Unicode('BtnModel').tag(sync=True)

    absolute = Bool(None, allow_none=True).tag(sync=True)

    active_class = Unicode(None, allow_none=True).tag(sync=True)

    append = Bool(None, allow_none=True).tag(sync=True)

    block = Bool(None, allow_none=True).tag(sync=True)

    bottom = Bool(None, allow_none=True).tag(sync=True)

    color = Unicode(None, allow_none=True).tag(sync=True)

    dark = Bool(None, allow_none=True).tag(sync=True)

    depressed = Bool(None, allow_none=True).tag(sync=True)

    disabled = Bool(None, allow_none=True).tag(sync=True)

    exact = Bool(None, allow_none=True).tag(sync=True)

    exact_active_class = Unicode(None, allow_none=True).tag(sync=True)

    fab = Bool(None, allow_none=True).tag(sync=True)

    fixed = Bool(None, allow_none=True).tag(sync=True)

    flat = Bool(None, allow_none=True).tag(sync=True)

    href = Union([
        Unicode(),
        Dict()
    ], default_value=None, allow_none=True).tag(sync=True)

    icon = Bool(None, allow_none=True).tag(sync=True)

    input_value = Any(None, allow_none=True).tag(sync=True)

    large = Bool(None, allow_none=True).tag(sync=True)

    left = Bool(None, allow_none=True).tag(sync=True)

    light = Bool(None, allow_none=True).tag(sync=True)

    loading = Bool(None, allow_none=True).tag(sync=True)

    nuxt = Bool(None, allow_none=True).tag(sync=True)

    outline = Bool(None, allow_none=True).tag(sync=True)

    replace = Bool(None, allow_none=True).tag(sync=True)

    right = Bool(None, allow_none=True).tag(sync=True)

    ripple = Union([
        Bool(),
        Dict()
    ], default_value=None, allow_none=True).tag(sync=True)

    round = Bool(None, allow_none=True).tag(sync=True)

    small = Bool(None, allow_none=True).tag(sync=True)

    tag = Unicode(None, allow_none=True).tag(sync=True)

    target = Unicode(None, allow_none=True).tag(sync=True)

    to = Union([
        Unicode(),
        Dict()
    ], default_value=None, allow_none=True).tag(sync=True)

    top = Bool(None, allow_none=True).tag(sync=True)

    type = Unicode(None, allow_none=True).tag(sync=True)

    value = Any(None, allow_none=True).tag(sync=True)


__all__ = ['Btn']
