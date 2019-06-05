from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class InputGroup(VuetifyWidget):

    _model_name = Unicode('InputGroupModel').tag(sync=True)

    append = Unicode(None, allow_none=True).tag(sync=True)

    append_html = Unicode(None, allow_none=True).tag(sync=True)

    id = Unicode(None, allow_none=True).tag(sync=True)

    prepend = Unicode(None, allow_none=True).tag(sync=True)

    prepend_html = Unicode(None, allow_none=True).tag(sync=True)

    size = Unicode(None, allow_none=True).tag(sync=True)

    tag = Unicode(None, allow_none=True).tag(sync=True)


__all__ = ['InputGroup']
