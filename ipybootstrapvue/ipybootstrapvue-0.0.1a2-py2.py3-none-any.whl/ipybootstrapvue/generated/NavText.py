from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class NavText(VuetifyWidget):

    _model_name = Unicode('NavTextModel').tag(sync=True)

    tag = Unicode(None, allow_none=True).tag(sync=True)


__all__ = ['NavText']
