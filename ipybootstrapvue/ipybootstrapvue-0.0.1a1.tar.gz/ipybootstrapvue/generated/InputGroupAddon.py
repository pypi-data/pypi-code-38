from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class InputGroupAddon(VuetifyWidget):

    _model_name = Unicode('InputGroupAddonModel').tag(sync=True)

    append = Bool(None, allow_none=True).tag(sync=True)

    id = Unicode(None, allow_none=True).tag(sync=True)

    is_text = Bool(None, allow_none=True).tag(sync=True)

    tag = Unicode(None, allow_none=True).tag(sync=True)


__all__ = ['InputGroupAddon']
