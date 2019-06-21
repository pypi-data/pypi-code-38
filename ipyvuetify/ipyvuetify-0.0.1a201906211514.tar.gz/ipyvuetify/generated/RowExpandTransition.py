from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class RowExpandTransition(VuetifyWidget):

    _model_name = Unicode('RowExpandTransitionModel').tag(sync=True)

    mode = Unicode(None, allow_none=True).tag(sync=True)


__all__ = ['RowExpandTransition']
