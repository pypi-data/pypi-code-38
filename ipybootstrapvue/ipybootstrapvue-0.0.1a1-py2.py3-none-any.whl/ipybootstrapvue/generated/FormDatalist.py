from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class FormDatalist(VuetifyWidget):

    _model_name = Unicode('FormDatalistModel').tag(sync=True)

    disabled_field = Unicode(None, allow_none=True).tag(sync=True)

    html_field = Unicode(None, allow_none=True).tag(sync=True)

    id = Unicode(None, allow_none=True).tag(sync=True)

    options = Union([
        List(Any()),
        Dict()
    ], default_value=None, allow_none=True).tag(sync=True)

    text_field = Unicode(None, allow_none=True).tag(sync=True)

    value_field = Unicode(None, allow_none=True).tag(sync=True)


__all__ = ['FormDatalist']
