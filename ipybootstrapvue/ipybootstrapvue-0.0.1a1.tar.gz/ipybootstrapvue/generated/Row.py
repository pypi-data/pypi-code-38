from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class Row(VuetifyWidget):

    _model_name = Unicode('RowModel').tag(sync=True)

    align_content = Unicode(None, allow_none=True).tag(sync=True)

    align_h = Unicode(None, allow_none=True).tag(sync=True)

    align_v = Unicode(None, allow_none=True).tag(sync=True)

    no_gutters = Bool(None, allow_none=True).tag(sync=True)

    tag = Unicode(None, allow_none=True).tag(sync=True)


__all__ = ['Row']
