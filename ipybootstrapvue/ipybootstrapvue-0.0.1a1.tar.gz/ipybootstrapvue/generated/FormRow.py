from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class FormRow(VuetifyWidget):

    _model_name = Unicode('FormRowModel').tag(sync=True)

    tag = Unicode(None, allow_none=True).tag(sync=True)


__all__ = ['FormRow']
