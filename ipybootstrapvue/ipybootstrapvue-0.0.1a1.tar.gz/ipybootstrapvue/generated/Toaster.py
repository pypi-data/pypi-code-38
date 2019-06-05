from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class Toaster(VuetifyWidget):

    _model_name = Unicode('ToasterModel').tag(sync=True)

    aria_atomic = Unicode(None, allow_none=True).tag(sync=True)

    aria_live = Unicode(None, allow_none=True).tag(sync=True)

    name = Unicode(None, allow_none=True).tag(sync=True)

    role = Unicode(None, allow_none=True).tag(sync=True)


__all__ = ['Toaster']
