from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class InputGroupAppend(VuetifyWidget):

    _model_name = Unicode('InputGroupAppendModel').tag(sync=True)

    id = Unicode(None, allow_none=True).tag(sync=True)

    is_text = Bool(None, allow_none=True).tag(sync=True)

    tag = Unicode(None, allow_none=True).tag(sync=True)


__all__ = ['InputGroupAppend']
