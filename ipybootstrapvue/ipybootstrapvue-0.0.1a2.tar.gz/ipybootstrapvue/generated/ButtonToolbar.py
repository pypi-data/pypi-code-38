from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class ButtonToolbar(VuetifyWidget):

    _model_name = Unicode('ButtonToolbarModel').tag(sync=True)

    justify = Bool(None, allow_none=True).tag(sync=True)

    key_nav = Bool(None, allow_none=True).tag(sync=True)


__all__ = ['ButtonToolbar']
