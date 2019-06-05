from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class CardGroup(VuetifyWidget):

    _model_name = Unicode('CardGroupModel').tag(sync=True)

    columns = Bool(None, allow_none=True).tag(sync=True)

    deck = Bool(None, allow_none=True).tag(sync=True)

    tag = Unicode(None, allow_none=True).tag(sync=True)


__all__ = ['CardGroup']
