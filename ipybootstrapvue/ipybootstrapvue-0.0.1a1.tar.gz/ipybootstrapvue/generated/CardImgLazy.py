from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class CardImgLazy(VuetifyWidget):

    _model_name = Unicode('CardImgLazyModel').tag(sync=True)

    alt = Unicode(None, allow_none=True).tag(sync=True)

    blank_color = Unicode(None, allow_none=True).tag(sync=True)

    blank_height = Union([
        Float(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)

    blank_src = Unicode(None, allow_none=True).tag(sync=True)

    blank_width = Union([
        Float(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)

    bottom = Bool(None, allow_none=True).tag(sync=True)

    end = Bool(None, allow_none=True).tag(sync=True)

    height = Union([
        Float(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)

    left = Bool(None, allow_none=True).tag(sync=True)

    offset = Union([
        Float(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)

    right = Bool(None, allow_none=True).tag(sync=True)

    show = Bool(None, allow_none=True).tag(sync=True)

    src = Unicode(None, allow_none=True).tag(sync=True)

    start = Bool(None, allow_none=True).tag(sync=True)

    throttle = Union([
        Float(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)

    top = Bool(None, allow_none=True).tag(sync=True)

    width = Union([
        Float(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)


__all__ = ['CardImgLazy']
