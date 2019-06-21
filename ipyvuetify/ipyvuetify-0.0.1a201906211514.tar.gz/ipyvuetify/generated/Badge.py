from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class Badge(VuetifyWidget):

    _model_name = Unicode('BadgeModel').tag(sync=True)

    bottom = Bool(None, allow_none=True).tag(sync=True)

    color = Unicode(None, allow_none=True).tag(sync=True)

    left = Bool(None, allow_none=True).tag(sync=True)

    mode = Unicode(None, allow_none=True).tag(sync=True)

    origin = Unicode(None, allow_none=True).tag(sync=True)

    overlap = Bool(None, allow_none=True).tag(sync=True)

    transition = Unicode(None, allow_none=True).tag(sync=True)

    value = Any(None, allow_none=True).tag(sync=True)


__all__ = ['Badge']
