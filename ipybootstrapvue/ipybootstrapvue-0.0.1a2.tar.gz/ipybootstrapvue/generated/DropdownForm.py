from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class DropdownForm(VuetifyWidget):

    _model_name = Unicode('DropdownFormModel').tag(sync=True)

    disabled = Bool(None, allow_none=True).tag(sync=True)

    id = Unicode(None, allow_none=True).tag(sync=True)

    inline = Bool(None, allow_none=True).tag(sync=True)

    novalidate = Bool(None, allow_none=True).tag(sync=True)

    validated = Bool(None, allow_none=True).tag(sync=True)


__all__ = ['DropdownForm']
