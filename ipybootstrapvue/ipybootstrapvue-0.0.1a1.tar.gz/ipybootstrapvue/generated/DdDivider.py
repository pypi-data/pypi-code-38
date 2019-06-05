from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class DdDivider(VuetifyWidget):

    _model_name = Unicode('DdDividerModel').tag(sync=True)

    tag = Unicode(None, allow_none=True).tag(sync=True)


__all__ = ['DdDivider']
