from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class BtnToolbar(VuetifyWidget):

    _model_name = Unicode('BtnToolbarModel').tag(sync=True)

    justify = Bool(None, allow_none=True).tag(sync=True)

    key_nav = Bool(None, allow_none=True).tag(sync=True)


__all__ = ['BtnToolbar']
