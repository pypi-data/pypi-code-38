from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class ExpansionPanel(VuetifyWidget):

    _model_name = Unicode('ExpansionPanelModel').tag(sync=True)

    dark = Bool(None, allow_none=True).tag(sync=True)

    disabled = Bool(None, allow_none=True).tag(sync=True)

    expand = Bool(None, allow_none=True).tag(sync=True)

    focusable = Bool(None, allow_none=True).tag(sync=True)

    inset = Bool(None, allow_none=True).tag(sync=True)

    light = Bool(None, allow_none=True).tag(sync=True)

    popout = Bool(None, allow_none=True).tag(sync=True)

    readonly = Bool(None, allow_none=True).tag(sync=True)

    value = Union([
        Float(),
        List(Any())
    ], default_value=None, allow_none=True).tag(sync=True)


__all__ = ['ExpansionPanel']
