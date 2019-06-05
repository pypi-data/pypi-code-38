from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class FormText(VuetifyWidget):

    _model_name = Unicode('FormTextModel').tag(sync=True)

    id = Unicode(None, allow_none=True).tag(sync=True)

    inline = Bool(None, allow_none=True).tag(sync=True)

    tag = Unicode(None, allow_none=True).tag(sync=True)

    text_variant = Unicode(None, allow_none=True).tag(sync=True)


__all__ = ['FormText']
