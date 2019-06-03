from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class ToolbarSideIcon(VuetifyWidget):

    _model_name = Unicode('ToolbarSideIconModel').tag(sync=True)


__all__ = ['ToolbarSideIcon']
