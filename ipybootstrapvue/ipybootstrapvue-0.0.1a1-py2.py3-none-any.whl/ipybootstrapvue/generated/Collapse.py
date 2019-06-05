from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class Collapse(VuetifyWidget):

    _model_name = Unicode('CollapseModel').tag(sync=True)

    accordion = Unicode(None, allow_none=True).tag(sync=True)

    id = Unicode(None, allow_none=True).tag(sync=True)

    is_nav = Bool(None, allow_none=True).tag(sync=True)

    tag = Unicode(None, allow_none=True).tag(sync=True)

    visible = Bool(None, allow_none=True).tag(sync=True)


__all__ = ['Collapse']
