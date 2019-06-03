from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class Alert(VuetifyWidget):

    _model_name = Unicode('AlertModel').tag(sync=True)

    color = Unicode(None, allow_none=True).tag(sync=True)

    dismissible = Bool(None, allow_none=True).tag(sync=True)

    icon = Unicode(None, allow_none=True).tag(sync=True)

    mode = Unicode(None, allow_none=True).tag(sync=True)

    origin = Unicode(None, allow_none=True).tag(sync=True)

    outline = Bool(None, allow_none=True).tag(sync=True)

    transition = Unicode(None, allow_none=True).tag(sync=True)

    type = Unicode(None, allow_none=True).tag(sync=True)

    value = Any(None, allow_none=True).tag(sync=True)


__all__ = ['Alert']
