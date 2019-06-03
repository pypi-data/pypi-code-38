from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class Chip(VuetifyWidget):

    _model_name = Unicode('ChipModel').tag(sync=True)

    close = Bool(None, allow_none=True).tag(sync=True)

    color = Unicode(None, allow_none=True).tag(sync=True)

    dark = Bool(None, allow_none=True).tag(sync=True)

    disabled = Bool(None, allow_none=True).tag(sync=True)

    label = Bool(None, allow_none=True).tag(sync=True)

    light = Bool(None, allow_none=True).tag(sync=True)

    outline = Bool(None, allow_none=True).tag(sync=True)

    selected = Bool(None, allow_none=True).tag(sync=True)

    small = Bool(None, allow_none=True).tag(sync=True)

    text_color = Unicode(None, allow_none=True).tag(sync=True)

    value = Bool(None, allow_none=True).tag(sync=True)


__all__ = ['Chip']
