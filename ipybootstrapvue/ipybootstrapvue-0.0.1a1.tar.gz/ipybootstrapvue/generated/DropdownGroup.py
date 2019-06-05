from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class DropdownGroup(VuetifyWidget):

    _model_name = Unicode('DropdownGroupModel').tag(sync=True)

    aria_describedby = Unicode(None, allow_none=True).tag(sync=True)

    header = Unicode(None, allow_none=True).tag(sync=True)

    header_classes = Union([
        Unicode(),
        List(Any()),
        Dict()
    ], default_value=None, allow_none=True).tag(sync=True)

    header_tag = Unicode(None, allow_none=True).tag(sync=True)

    header_variant = Unicode(None, allow_none=True).tag(sync=True)

    id = Unicode(None, allow_none=True).tag(sync=True)


__all__ = ['DropdownGroup']
