from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class Media(VuetifyWidget):

    _model_name = Unicode('MediaModel').tag(sync=True)

    no_body = Bool(None, allow_none=True).tag(sync=True)

    right_align = Bool(None, allow_none=True).tag(sync=True)

    tag = Unicode(None, allow_none=True).tag(sync=True)

    vertical_align = Unicode(None, allow_none=True).tag(sync=True)


__all__ = ['Media']
