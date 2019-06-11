from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class Toolbar(VuetifyWidget):

    _model_name = Unicode('ToolbarModel').tag(sync=True)

    absolute = Bool(None, allow_none=True).tag(sync=True)

    app = Bool(None, allow_none=True).tag(sync=True)

    card = Bool(None, allow_none=True).tag(sync=True)

    clipped_left = Bool(None, allow_none=True).tag(sync=True)

    clipped_right = Bool(None, allow_none=True).tag(sync=True)

    color = Unicode(None, allow_none=True).tag(sync=True)

    dark = Bool(None, allow_none=True).tag(sync=True)

    dense = Bool(None, allow_none=True).tag(sync=True)

    extended = Bool(None, allow_none=True).tag(sync=True)

    extension_height = Union([
        Float(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)

    fixed = Bool(None, allow_none=True).tag(sync=True)

    flat = Bool(None, allow_none=True).tag(sync=True)

    floating = Bool(None, allow_none=True).tag(sync=True)

    height = Union([
        Float(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)

    inverted_scroll = Bool(None, allow_none=True).tag(sync=True)

    light = Bool(None, allow_none=True).tag(sync=True)

    manual_scroll = Bool(None, allow_none=True).tag(sync=True)

    prominent = Bool(None, allow_none=True).tag(sync=True)

    scroll_off_screen = Bool(None, allow_none=True).tag(sync=True)

    scroll_target = Unicode(None, allow_none=True).tag(sync=True)

    scroll_threshold = Float(None, allow_none=True).tag(sync=True)

    scroll_toolbar_off_screen = Bool(None, allow_none=True).tag(sync=True)

    tabs = Bool(None, allow_none=True).tag(sync=True)


__all__ = ['Toolbar']
