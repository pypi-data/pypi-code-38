from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class List(VuetifyWidget):

    _model_name = Unicode('ListModel').tag(sync=True)

    dark = Bool(None, allow_none=True).tag(sync=True)

    dense = Bool(None, allow_none=True).tag(sync=True)

    expand = Bool(None, allow_none=True).tag(sync=True)

    light = Bool(None, allow_none=True).tag(sync=True)

    subheader = Bool(None, allow_none=True).tag(sync=True)

    three_line = Bool(None, allow_none=True).tag(sync=True)

    two_line = Bool(None, allow_none=True).tag(sync=True)


__all__ = ['List']
