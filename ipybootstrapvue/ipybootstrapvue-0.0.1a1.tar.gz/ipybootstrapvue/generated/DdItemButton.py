from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class DdItemButton(VuetifyWidget):

    _model_name = Unicode('DdItemButtonModel').tag(sync=True)

    active = Bool(None, allow_none=True).tag(sync=True)

    active_class = Unicode(None, allow_none=True).tag(sync=True)

    disabled = Bool(None, allow_none=True).tag(sync=True)

    variant = Unicode(None, allow_none=True).tag(sync=True)


__all__ = ['DdItemButton']
