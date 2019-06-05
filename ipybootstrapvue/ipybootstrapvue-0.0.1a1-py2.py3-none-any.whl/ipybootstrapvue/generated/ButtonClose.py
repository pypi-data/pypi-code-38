from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class ButtonClose(VuetifyWidget):

    _model_name = Unicode('ButtonCloseModel').tag(sync=True)

    aria_label = Unicode(None, allow_none=True).tag(sync=True)

    disabled = Bool(None, allow_none=True).tag(sync=True)

    text_variant = Unicode(None, allow_none=True).tag(sync=True)


__all__ = ['ButtonClose']
