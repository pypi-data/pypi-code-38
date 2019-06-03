from traitlets import (
    Unicode, Enum, Instance, Union, Float, Int, List, Tuple, Dict,
    Undefined, Bool, Any
)

from .VuetifyWidget import VuetifyWidget


class ListTileActionText(VuetifyWidget):

    _model_name = Unicode('ListTileActionTextModel').tag(sync=True)


__all__ = ['ListTileActionText']
