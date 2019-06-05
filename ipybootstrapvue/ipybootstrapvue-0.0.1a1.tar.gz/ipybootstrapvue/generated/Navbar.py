from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class Navbar(VuetifyWidget):

    _model_name = Unicode('NavbarModel').tag(sync=True)

    fixed = Unicode(None, allow_none=True).tag(sync=True)

    print = Bool(None, allow_none=True).tag(sync=True)

    sticky = Bool(None, allow_none=True).tag(sync=True)

    tag = Unicode(None, allow_none=True).tag(sync=True)

    toggleable = Union([
        Bool(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)

    type = Unicode(None, allow_none=True).tag(sync=True)

    variant = Unicode(None, allow_none=True).tag(sync=True)


__all__ = ['Navbar']
