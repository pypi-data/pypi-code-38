from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class Nav(VuetifyWidget):

    _model_name = Unicode('NavModel').tag(sync=True)

    align = Unicode(None, allow_none=True).tag(sync=True)

    fill = Bool(None, allow_none=True).tag(sync=True)

    is_nav_bar = Bool(None, allow_none=True).tag(sync=True)

    justified = Bool(None, allow_none=True).tag(sync=True)

    pills = Bool(None, allow_none=True).tag(sync=True)

    small = Bool(None, allow_none=True).tag(sync=True)

    tabs = Bool(None, allow_none=True).tag(sync=True)

    tag = Unicode(None, allow_none=True).tag(sync=True)

    vertical = Bool(None, allow_none=True).tag(sync=True)


__all__ = ['Nav']
