from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class BtnClose(VuetifyWidget):

    _model_name = Unicode('BtnCloseModel').tag(sync=True)

    aria_label = Unicode(None, allow_none=True).tag(sync=True)

    disabled = Bool(None, allow_none=True).tag(sync=True)

    text_variant = Unicode(None, allow_none=True).tag(sync=True)


__all__ = ['BtnClose']
