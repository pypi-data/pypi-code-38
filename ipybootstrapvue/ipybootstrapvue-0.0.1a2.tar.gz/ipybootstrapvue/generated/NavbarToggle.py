from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class NavbarToggle(VuetifyWidget):

    _model_name = Unicode('NavbarToggleModel').tag(sync=True)

    label = Unicode(None, allow_none=True).tag(sync=True)

    target = Unicode(None, allow_none=True).tag(sync=True)


__all__ = ['NavbarToggle']
