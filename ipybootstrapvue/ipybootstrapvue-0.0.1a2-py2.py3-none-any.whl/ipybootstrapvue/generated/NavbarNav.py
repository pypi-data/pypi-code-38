from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class NavbarNav(VuetifyWidget):

    _model_name = Unicode('NavbarNavModel').tag(sync=True)

    align = Unicode(None, allow_none=True).tag(sync=True)

    fill = Bool(None, allow_none=True).tag(sync=True)

    justified = Bool(None, allow_none=True).tag(sync=True)

    small = Bool(None, allow_none=True).tag(sync=True)

    tag = Unicode(None, allow_none=True).tag(sync=True)


__all__ = ['NavbarNav']
