from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class ExpansionPanelContent(VuetifyWidget):

    _model_name = Unicode('ExpansionPanelContentModel').tag(sync=True)

    disabled = Bool(None, allow_none=True).tag(sync=True)

    expand_icon = Unicode(None, allow_none=True).tag(sync=True)

    hide_actions = Bool(None, allow_none=True).tag(sync=True)

    lazy = Bool(None, allow_none=True).tag(sync=True)

    readonly = Bool(None, allow_none=True).tag(sync=True)

    ripple = Union([
        Bool(),
        Dict()
    ], default_value=None, allow_none=True).tag(sync=True)

    value = Any(None, allow_none=True).tag(sync=True)


__all__ = ['ExpansionPanelContent']
