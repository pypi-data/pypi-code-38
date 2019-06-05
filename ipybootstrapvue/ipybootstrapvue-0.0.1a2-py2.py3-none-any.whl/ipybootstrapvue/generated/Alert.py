from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class Alert(VuetifyWidget):

    _model_name = Unicode('AlertModel').tag(sync=True)

    dismiss_label = Unicode(None, allow_none=True).tag(sync=True)

    dismissible = Bool(None, allow_none=True).tag(sync=True)

    fade = Bool(None, allow_none=True).tag(sync=True)

    show = Union([
        Bool(),
        Float(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)

    variant = Unicode(None, allow_none=True).tag(sync=True)


__all__ = ['Alert']
