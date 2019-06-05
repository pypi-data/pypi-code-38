from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class ListGroup(VuetifyWidget):

    _model_name = Unicode('ListGroupModel').tag(sync=True)

    flush = Bool(None, allow_none=True).tag(sync=True)

    horizontal = Union([
        Bool(),
        Unicode()
    ], default_value=None, allow_none=True).tag(sync=True)

    tag = Unicode(None, allow_none=True).tag(sync=True)


__all__ = ['ListGroup']
